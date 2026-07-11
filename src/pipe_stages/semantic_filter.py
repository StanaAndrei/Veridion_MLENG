from typing import List
from google import genai
from google.genai import types
from Types.Company import Company
from Types.QueryIntent import QueryIntent


def _dot_product(vec_a: List[float], vec_b: List[float]) -> float:
    return sum(a * b for a, b in zip(vec_a, vec_b))


def _get_embedding(client: genai.Client, text: str, is_query: bool = False) -> List[float]:
    """Fetches an isolated vector with explicit retrieval tasks optimized for asymmetric matching."""
    task = "RETRIEVAL_QUERY" if is_query else "RETRIEVAL_DOCUMENT"

    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config=types.EmbedContentConfig(task_type=task)
    )
    return response.embeddings[0].values


def ranked_semantic_candidates(filtered_companies: List[Company], parsed_intent: QueryIntent) -> List[Company]:
    if not filtered_companies:
        return []

    client = genai.Client()

    # 1. Generate the single query intent anchor vector
    query_vector = _get_embedding(client, parsed_intent.semantic_search_prompt, is_query=True)

    scored_candidates = []
    keywords = [k.lower() for k in parsed_intent.industry_intent.primary_keywords]

    # 2. Iterate cleanly through companies, ensuring isolated tracking per element
    for company in filtered_companies:
        offerings_str = ", ".join(company.core_offerings or [])
        markets_str = ", ".join(company.target_markets or [])

        company_text_blob = f"""
        Company: {company.operational_name}
        Description: {company.description}
        Offerings: {offerings_str}
        Target Markets: {markets_str}
        """

        try:
            # Isolated vector calculation eliminates multi-part token index shift bugs
            company_vector = _get_embedding(client, company_text_blob.strip(), is_query=False)
            base_score = _dot_product(query_vector, company_vector)
        except Exception as e:
            # Fallback defensively if a specific company profile triggers an execution hitch
            base_score = 0.0

        # 3. Hybrid Search: Apply industry keyword validation adjustments
        keyword_boost = 0.0
        company_metadata_pool = []

        if company.business_model:
            company_metadata_pool.extend([bm.lower() for bm in company.business_model])
        if company.target_markets:
            company_metadata_pool.extend([tm.lower() for tm in company.target_markets])
        if company.primary_naics and company.primary_naics.label:
            company_metadata_pool.append(company.primary_naics.label.lower())

        # If the metadata pool explicitly contains the requested intent keys, award a boost
        for kw in keywords:
            if any(kw in meta for meta in company_metadata_pool):
                keyword_boost += 0.30

        final_score = base_score + keyword_boost
        scored_candidates.append((final_score, company))

    # 4. Sort descending based on our updated hybrid metrics
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    # Absolute unique item preservation layer
    seen_ids = set()
    unique_ranked_companies = []
    for _, company in scored_candidates:
        # Deduplicate using operational name or internal tracking reference
        if company.operational_name not in seen_ids:
            seen_ids.add(company.operational_name)
            unique_ranked_companies.append(company)

    return unique_ranked_companies
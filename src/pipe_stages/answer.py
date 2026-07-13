import json
from google import genai
from google.genai import types
from typing import List
from Types.Company import Company
from Types.Qualification import FinalQualificationReport


def final_count(raw_companies: List[Company]) -> int:
    """Takes the list of parsed companies and returns the total count."""
    return len(raw_companies)


def final_evaluation(ranked_semantic_candidates: List[Company], query: str) -> FinalQualificationReport:
    """
    Takes the top semantically ranked candidates from Stage 3 and uses Gemini-2.5-flash
    to filter out false positives and borderline matches.
    """
    if not ranked_semantic_candidates:
        return FinalQualificationReport(qualified_matches=[])

    client = genai.Client()

    # We slice the top 15 candidates to keep API latencies low and cost tiny
    top_candidates = ranked_semantic_candidates[:15]

    # Format a highly compact JSON payload for the LLM prompt
    company_catalog = []
    for c in top_candidates:
        company_catalog.append({
            "operational_name": c.operational_name,
            "description": c.description,
            "business_model": c.business_model,
            "core_offerings": c.core_offerings,
            "target_markets": c.target_markets
        })

    prompt = f"""
    You are an expert industry matching auditor. Your job is to audit potential company candidates 
    retrieved by our search system and flag false positives, role reversals, or weak matches.

    Original User Query: "{query}"

    Analyze the following candidates carefully. For each company, evaluate whether they truly satisfy the user's exact query.
    Pay close attention to relationship nuances (e.g., if a user wants a packaging supplier, a cosmetics brand that uses packaging is a MISMATCH).

    Candidates to Evaluate:
    {json.dumps(company_catalog, indent=2)}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FinalQualificationReport,
            temperature=0.0,
        ),
    )

    return FinalQualificationReport.model_validate_json(response.text)
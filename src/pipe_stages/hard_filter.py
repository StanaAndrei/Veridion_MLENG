from typing import List
from Types.Company import Company
from Types.QueryIntent import QueryIntent


def filtered_companies(raw_companies: List[Company], parsed_intent: QueryIntent) -> List[Company]:
    filters = parsed_intent.hard_filters

    keywords = [k.lower() for k in parsed_intent.industry_intent.primary_keywords]
    if "logistics" in keywords:
        keywords.extend(["transport", "freight", "cargo", "delivery", "shipping", "warehouse", "supply chain"])

    valid_candidates: List[Company] = []

    for company in raw_companies:
        # --- 1. Regional / Country Filter ---
        if filters.country_codes:
            if company.address and company.address.country_code:
                if company.address.country_code.lower() not in [c.lower() for c in filters.country_codes]:
                    continue

                    # --- 2. Public / Private Status Filter ---
        if filters.is_public is not None:
            if company.is_public != filters.is_public:
                continue

        # --- 3. Employee Count Bounds ---
        if filters.min_employees and company.employee_count is not None:
            if company.employee_count < filters.min_employees:
                continue
        if filters.max_employees and company.employee_count is not None:
            if company.employee_count > filters.max_employees:
                continue

        # --- 4. Revenue Bounds ---
        if filters.min_revenue and company.revenue is not None:
            if company.revenue < filters.min_revenue:
                continue
        if filters.max_revenue and company.revenue is not None:
            if company.revenue > filters.max_revenue:
                continue

        # --- 5. Year Founded Bounds ---
        if filters.founded_after and company.year_founded is not None:
            if company.year_founded <= filters.founded_after:
                continue

        valid_candidates.append(company)

    # --- 6. Smart Keyword Scoring Fallback ---
    # We score each company based on keyword hits. If companies with hits exist,
    # we only return those. If zero match, we keep the entire country list
    # so Stage 3's neural embeddings can try to find them anyway.
    if keywords:
        matched_candidates = []
        for company in valid_candidates:
            company_text_footprint = []
            if company.primary_naics and company.primary_naics.label:
                company_text_footprint.append(company.primary_naics.label.lower())
            if company.core_offerings:
                company_text_footprint.extend([o.lower() for o in company.core_offerings])
            if company.business_model:
                company_text_footprint.extend([b.lower() for b in company.business_model])
            if company.description:
                company_text_footprint.append(company.description.lower())

            # If there's any synonym hit, keep them
            if any(any(kw in footprint_item for footprint_item in company_text_footprint) for kw in keywords):
                matched_candidates.append(company)

        if matched_candidates:
            return matched_candidates

    return valid_candidates


def filtered_count(filtered_companies: List[Company]) -> int:
    return len(filtered_companies)
from typing import List
from Types.Company import Company
from Types.QueryIntent import QueryIntent


def filtered_companies(raw_companies: List[Company], parsed_intent: QueryIntent) -> List[Company]:
    filters = parsed_intent.hard_filters
    valid_candidates: List[Company] = []

    for company in raw_companies:
        # --- 1. Regional / Country Filter ---
        if filters.country_codes:
            if company.address and company.address.country_code:
                # Check if the company country is in our allowed extracted list
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

    return valid_candidates


def filtered_count(filtered_companies: List[Company]) -> int:
    return len(filtered_companies)
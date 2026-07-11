from typing import List
from Types.Company import Company
from Types.QueryIntent import QueryIntent


def filtered_companies(raw_companies: List[Company], parsed_intent: QueryIntent) -> List[Company]:
    """
    Filters the initial company list based on deterministic hard constraints.
    Applies a 'soft-fail' design: if a constraint is requested but a company's data field
    is missing (None), we KEEP the company to avoid false negatives.
    """
    filters = parsed_intent.hard_filters
    valid_candidates: List[Company] = []

    for company in raw_companies:
        # --- 1. Geography Filter (Country Code) ---
        if filters.country_code:
            # If company has an address, verify country. If address is completely missing, we keep it.
            if company.address and company.address.country_code:
                if company.address.country_code.lower() != filters.country_code.lower():
                    continue  # Disqualify: Country code explicitly mismatches

        # --- 2. Public / Private Status Filter ---
        if filters.is_public is not None:
            # is_public is guaranteed to be a bool in our dataset, so we check directly
            if company.is_public != filters.is_public:
                continue  # Disqualify: Public status explicitly mismatches

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

        # If it survives all checks, it passes to the next phase
        valid_candidates.append(company)

    return valid_candidates


def filtered_count(filtered_companies: List[Company]) -> int:
    """Helper asset node to track the shrinking pipeline size."""
    return len(filtered_companies)
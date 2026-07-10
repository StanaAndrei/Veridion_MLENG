from typing import List
from Types.Company import Company

def final_count(raw_companies: List[Company]) -> int:
    """Takes the list of parsed companies and returns the total count."""
    return len(raw_companies)
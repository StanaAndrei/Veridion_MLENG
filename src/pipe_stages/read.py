from typing import List
from pydantic import ValidationError
from Types.Company import Company


def raw_companies(infile: str) -> List[Company]:
    companies: List[Company] = []

    with open(infile, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                company = Company.model_validate_json(line)
                companies.append(company)
            except ValidationError as e:
                print(f"Line {idx} failed validation. Errors:")
                print(e.json(indent=2))
                print("-" * 40)
            except Exception as e:
                print(f"Line {idx} had a general error: {e}")

    return companies
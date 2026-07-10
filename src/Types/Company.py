import ast, json
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class Address(BaseModel):
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region_name: Optional[str] = None
    town: Optional[str] = None


class NaicsCode(BaseModel):
    code: str
    label: str
    share: Optional[float] = None  # Added to handle fields containing a share metric cleanly


class Company(BaseModel):
    website: Optional[str] = None
    operational_name: Optional[str] = None
    year_founded: Optional[int] = None
    address: Optional[Address] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None
    primary_naics: Optional[NaicsCode] = None
    secondary_naics: Optional[List[NaicsCode]] = None
    description: str
    business_model: Optional[List[str]] = None
    target_markets: Optional[List[str]] = None
    core_offerings: Optional[List[str]] = None
    is_public: bool

    @field_validator("address", "primary_naics", "secondary_naics", mode="before")
    @classmethod
    def parse_malformed_json_strings(cls, v: Any, info) -> Any:
        """Safely transforms stringified python dicts and wraps single objects into lists when required."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            try:
                v = ast.literal_eval(v)
            except (ValueError, SyntaxError):
                try:
                    v = json.loads(v)
                except Exception:
                    return None

        # Check if we are validating secondary_naics, which expects a list
        if info.field_name == "secondary_naics" and isinstance(v, dict):
            return [v]

        return v
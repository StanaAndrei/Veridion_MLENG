from typing import List, Optional
from pydantic import BaseModel, Field

class HardFilters(BaseModel):
    country_codes: Optional[List[str]] = Field(
        None, description="List of ISO 2-letter country codes implied by the query. For 'Europe', include ['es', 'fr', 'de', 'gb', 'it', 'nl', 'ro', 'ch', 'pt', 'be']. For 'Germany', just ['de']."
    )
    min_employees: Optional[int] = Field(None, description="Minimum number of employees requested.")
    max_employees: Optional[int] = Field(None, description="Maximum number of employees requested.")
    min_revenue: Optional[float] = Field(None, description="Minimum annual revenue in USD.")
    max_revenue: Optional[float] = Field(None, description="Maximum annual revenue in USD.")
    is_public: Optional[bool] = Field(None, description="True if explicitly public, False if private, None if not mentioned.")
    founded_after: Optional[int] = Field(None, description="Year founded must be strictly greater than this.")

class IndustryIntent(BaseModel):
    primary_keywords: List[str] = Field(..., description="List of relevant industry or role keywords.")
    banned_keywords: List[str] = Field(default_factory=list, description="Keywords to actively avoid.")

class QueryIntent(BaseModel):
    hard_filters: HardFilters = Field(..., description="Deterministic attribute parameters extracted from the query.")
    industry_intent: IndustryIntent = Field(..., description="Semantic text blocks and role identifiers.")
    semantic_search_prompt: str = Field(..., description="An optimized, descriptive sentence targeted at asymmetric vector search matching.")
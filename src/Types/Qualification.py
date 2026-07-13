from typing import List
from pydantic import BaseModel, Field

class CompanyEvaluation(BaseModel):
    operational_name: str
    is_true_match: bool = Field(
        ...,
        description="True if the company fully and explicitly satisfies the user's core intent. False if borderline, unrelated, or a mismatch."
    )
    confidence_score: float = Field(..., description="Score from 0.0 to 1.0 representing matching confidence.")
    justification: str = Field(..., description="One concise sentence explaining why this company is or isn't a true match.")

class FinalQualificationReport(BaseModel):
    qualified_matches: List[CompanyEvaluation] = Field(..., description="List of evaluations for the analyzed companies.")
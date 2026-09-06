from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class FeedbackRequest(BaseModel):
    feedback_text: str = Field(..., description="The unstructured text of the customer feedback.")
    source_platform: str = Field(..., description="The platform where the feedback was left (e.g., Twitter, Email, Support Portal).")
    customer_id: Optional[str] = Field(None, description="Optional customer identifier.")

class SentimentEnum(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"

class FeedbackAnalysis(BaseModel):
    sentiment: SentimentEnum = Field(..., description="The sentiment of the feedback.")
    summary: str = Field(..., description="A strict 1-sentence summary of the feedback.")
    urgency_score: int = Field(..., ge=1, le=5, description="Urgency score from 1 (lowest) to 5 (highest).")
    action_items: List[str] = Field(..., description="A list of actionable items extracted from the feedback.")

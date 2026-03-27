from pydantic import BaseModel

class BugPrediction(BaseModel):
    label: str
    reasoning: str
    evidence: str
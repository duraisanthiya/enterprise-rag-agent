from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error_code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable explanation of the error")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC time when the error occurred",
    )

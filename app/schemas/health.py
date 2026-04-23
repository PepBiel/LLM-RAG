from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_version: str
    environment: str
    checks: dict[str, Any] = Field(default_factory=dict)


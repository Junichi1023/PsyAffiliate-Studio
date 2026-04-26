from __future__ import annotations

from fastapi import APIRouter

from ..schemas import (
    ComplianceCheckRequest,
    ComplianceCheckResult,
    EmpathyCheckRequest,
    EmpathyCheckResult,
    GeneratedContent,
    GenerateContentRequest,
)
from ..services.ai.openai_client import generate_content
from ..services.compliance.checker import check_compliance
from ..services.empathy import check_empathy


router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/generate", response_model=GeneratedContent)
def generate(payload: GenerateContentRequest) -> dict:
    return generate_content(payload)


@router.post("/compliance-check", response_model=ComplianceCheckResult)
def compliance_check(payload: ComplianceCheckRequest) -> dict:
    return check_compliance(**payload.model_dump())


@router.post("/empathy-check", response_model=EmpathyCheckResult)
def empathy_check(payload: EmpathyCheckRequest) -> dict:
    return check_empathy(**payload.model_dump())

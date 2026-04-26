from __future__ import annotations

from fastapi import APIRouter

from ..schemas import ComplianceCheckRequest, ComplianceCheckResult, GeneratedContent, GenerateContentRequest
from ..services.ai.openai_client import generate_content
from ..services.compliance.checker import check_compliance


router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/generate", response_model=GeneratedContent)
def generate(payload: GenerateContentRequest) -> dict:
    return generate_content(payload)


@router.post("/compliance-check", response_model=ComplianceCheckResult)
def compliance_check(payload: ComplianceCheckRequest) -> dict:
    return check_compliance(**payload.model_dump())

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Platform = Literal["threads", "instagram", "both"]
Tone = Literal["empathy", "practical", "story", "educational", "soft_sales"]
DraftStatus = Literal["draft", "needs_review", "approved", "scheduled", "posted", "failed"]


class KnowledgeBase(BaseModel):
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str | None = None


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    content: str | None = None
    source: str | None = None


class KnowledgeItem(KnowledgeBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class AffiliateProductBase(BaseModel):
    name: str = Field(min_length=1)
    asp_name: str | None = None
    affiliate_url: str = Field(min_length=1)
    display_url: str | None = None
    category: str | None = None
    target_pain: str | None = None
    commission_type: str | None = None
    commission_amount: float | None = None
    prohibited_claims: str | None = None
    priority: int = 0
    is_active: bool = True


class AffiliateProductCreate(AffiliateProductBase):
    pass


class AffiliateProductUpdate(BaseModel):
    name: str | None = None
    asp_name: str | None = None
    affiliate_url: str | None = None
    display_url: str | None = None
    category: str | None = None
    target_pain: str | None = None
    commission_type: str | None = None
    commission_amount: float | None = None
    prohibited_claims: str | None = None
    priority: int | None = None
    is_active: bool | None = None


class AffiliateProduct(AffiliateProductBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class GenerateContentRequest(BaseModel):
    theme: str = Field(min_length=1)
    target_reader: str = Field(min_length=1)
    platform: Platform
    tone: Tone
    selected_product_id: int | None = None


class GeneratedContent(BaseModel):
    platform: Platform
    theme: str
    body: str
    caption: str | None = None
    cta: str
    pr_disclosure: str
    affiliate_product_id: int | None = None
    compliance_score: int
    risk_notes: list[str]
    suggested_hashtags: list[str]


class ComplianceCheckRequest(BaseModel):
    body: str = ""
    caption: str | None = None
    cta: str | None = None
    affiliate_product_id: int | None = None
    prohibited_claims: str | None = None


class ComplianceCheckResult(BaseModel):
    compliance_score: int
    risk_level: str
    risk_notes: list[str]
    suggested_fix: str
    has_pr_disclosure: bool
    flagged_terms: list[str]
    recommendation: str


class DraftBase(BaseModel):
    platform: Platform
    theme: str = Field(min_length=1)
    body: str = Field(min_length=1)
    caption: str | None = None
    cta: str | None = None
    affiliate_product_id: int | None = None
    compliance_score: int | None = None
    risk_notes: str | None = None
    status: DraftStatus = "draft"
    scheduled_at: str | None = None
    posted_at: str | None = None


class DraftCreate(DraftBase):
    pass


class DraftUpdate(BaseModel):
    platform: Platform | None = None
    theme: str | None = None
    body: str | None = None
    caption: str | None = None
    cta: str | None = None
    affiliate_product_id: int | None = None
    compliance_score: int | None = None
    risk_notes: str | None = None
    status: DraftStatus | None = None
    scheduled_at: str | None = None
    posted_at: str | None = None


class Draft(DraftBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class DashboardStats(BaseModel):
    knowledge_count: int
    affiliate_product_count: int
    draft_count: int
    pending_review: int
    today_drafts: int
    active_products: int
    recent_drafts: list[Draft]


class AppSettingsOut(BaseModel):
    openai_api_key_set: bool
    openai_model: str
    default_platform: Platform
    default_pr_disclosure: str
    brand_voice_summary: str


class AppSettingsUpdate(BaseModel):
    openai_api_key: str | None = None
    openai_model: str | None = None
    default_platform: Platform | None = None
    default_pr_disclosure: str | None = None
    brand_voice_summary: str | None = None

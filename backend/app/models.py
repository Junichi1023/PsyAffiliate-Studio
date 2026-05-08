from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Platform = Literal["threads", "instagram", "both"]
Tone = Literal["empathy", "practical", "story", "educational", "soft_sales"]
DraftStatus = Literal["draft", "needs_review", "approved", "scheduled", "posted", "failed"]
AffiliateIntent = Literal["none", "soft", "moderate"]
ScheduleMode = Literal["draft_only", "next_free_slot", "scheduled_time"]


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


class PersonaPainBase(BaseModel):
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    pain_summary: str = Field(min_length=1)
    emotional_state: str | None = None
    desired_future: str | None = None
    forbidden_approach: str | None = None
    recommended_tone: str | None = None


class PersonaPainCreate(PersonaPainBase):
    pass


class PersonaPainUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    pain_summary: str | None = None
    emotional_state: str | None = None
    desired_future: str | None = None
    forbidden_approach: str | None = None
    recommended_tone: str | None = None


class PersonaPain(PersonaPainBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class FortuneTemplateBase(BaseModel):
    name: str = Field(min_length=1)
    fortune_type: str = Field(min_length=1)
    target_pain_category: str | None = None
    structure: str = Field(min_length=1)
    example_output: str | None = None
    prohibited_patterns: str | None = None


class FortuneTemplateCreate(FortuneTemplateBase):
    pass


class FortuneTemplateUpdate(BaseModel):
    name: str | None = None
    fortune_type: str | None = None
    target_pain_category: str | None = None
    structure: str | None = None
    example_output: str | None = None
    prohibited_patterns: str | None = None


class FortuneTemplate(FortuneTemplateBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class GenerateContentRequest(BaseModel):
    theme: str = Field(min_length=1)
    target_reader: str = Field(min_length=1)
    platform: Platform
    tone: Tone
    selected_product_id: int | None = None
    fortune_type: str | None = None
    persona_pain_id: int | None = None
    fortune_template_id: int | None = None
    affiliate_intent: AffiliateIntent = "none"
    pain_category: str | None = None
    post_type: str | None = None
    note_page_id: int | None = None
    fortune_offer_id: int | None = None
    threads_template_id: int | None = None
    cta_template_id: int | None = None
    typefully_schedule_mode: ScheduleMode | None = None
    typefully_scheduled_at: str | None = None


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
    empathy_score: int | None = None
    empathy_notes: list[str] = []
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


class EmpathyCheckRequest(BaseModel):
    body: str = ""
    caption: str | None = None
    target_reader: str | None = None
    persona_pain_id: int | None = None


class EmpathyCheckResult(BaseModel):
    empathy_score: int
    risk_level: str
    checks: dict[str, bool]
    notes: list[str]
    suggested_fix: str


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
    fortune_type: str | None = None
    persona_pain_id: int | None = None
    fortune_template_id: int | None = None
    affiliate_intent: AffiliateIntent | None = "none"
    empathy_score: int | None = None
    empathy_notes: str | None = None
    publish_ready: bool = False
    publish_block_reason: str | None = None
    note_page_id: int | None = None
    fortune_offer_id: int | None = None
    threads_template_id: int | None = None
    typefully_job_id: int | None = None
    traffic_destination: str | None = "profile_note"
    direct_a8_link_detected: bool = False
    profile_note_cta_included: bool = False
    human_review_required: bool = True


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
    fortune_type: str | None = None
    persona_pain_id: int | None = None
    fortune_template_id: int | None = None
    affiliate_intent: AffiliateIntent | None = None
    empathy_score: int | None = None
    empathy_notes: str | None = None
    publish_ready: bool | None = None
    publish_block_reason: str | None = None
    note_page_id: int | None = None
    fortune_offer_id: int | None = None
    threads_template_id: int | None = None
    typefully_job_id: int | None = None
    traffic_destination: str | None = None
    direct_a8_link_detected: bool | None = None
    profile_note_cta_included: bool | None = None
    human_review_required: bool | None = None


class Draft(DraftBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class DashboardStats(BaseModel):
    knowledge_count: int
    affiliate_product_count: int
    persona_pain_count: int
    fortune_template_count: int
    draft_count: int
    pending_review: int
    publish_ready_count: int
    risky_draft_count: int
    today_drafts: int
    active_products: int
    today_scheduled_count: int = 0
    typefully_waiting_count: int = 0
    note_missing_draft_count: int = 0
    a8_link_detected_count: int = 0
    facebook_candidate_count: int = 0
    plan_done_count: int = 0
    plan_total_count: int = 0
    weekly_post_type_distribution: dict[str, int] = {}
    recent_drafts: list[Draft]


class AppSettingsOut(BaseModel):
    openai_api_key_set: bool
    openai_model: str
    default_platform: Platform
    default_pr_disclosure: str
    brand_voice_summary: str
    typefully_api_key_set: bool = False
    typefully_social_set_id: str | None = None
    typefully_default_schedule_mode: ScheduleMode = "draft_only"
    profile_note_url: str | None = None


class AppSettingsUpdate(BaseModel):
    openai_api_key: str | None = None
    openai_model: str | None = None
    default_platform: Platform | None = None
    default_pr_disclosure: str | None = None
    brand_voice_summary: str | None = None
    typefully_api_key: str | None = None
    typefully_social_set_id: str | None = None
    typefully_default_schedule_mode: ScheduleMode | None = None
    profile_note_url: str | None = None


class PublishResult(BaseModel):
    ok: bool
    draft_id: int
    provider_results: list[dict]
    message: str


class ImportSession(BaseModel):
    id: int
    source_type: str
    source_name: str | None = None
    status: str
    total_items: int = 0
    sanitized_items: int = 0
    candidate_count: int = 0
    redaction_summary: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ImportCandidateBase(BaseModel):
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str | None = None
    confidence_score: int = 70
    redaction_notes: str | None = None
    selected: bool = True


class ImportCandidateUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    content: str | None = None
    source: str | None = None
    confidence_score: int | None = None
    redaction_notes: str | None = None
    selected: bool | None = None


class ImportCandidate(ImportCandidateBase):
    id: int
    session_id: int
    created_at: str | None = None
    updated_at: str | None = None


class ImportCommitResult(BaseModel):
    committed_count: int
    knowledge_items: list[KnowledgeItem]


class NoteFunnelPageBase(BaseModel):
    title: str = Field(min_length=1)
    note_url: str = Field(min_length=1)
    purpose: str | None = None
    target_theme: str | None = None
    target_reader: str | None = None
    article_type: str | None = None
    pr_disclosure: str | None = "【PR】"
    status: str | None = "idea"
    memo: str | None = None


class NoteFunnelPageCreate(NoteFunnelPageBase):
    pass


class NoteFunnelPageUpdate(BaseModel):
    title: str | None = None
    note_url: str | None = None
    purpose: str | None = None
    target_theme: str | None = None
    target_reader: str | None = None
    article_type: str | None = None
    pr_disclosure: str | None = None
    status: str | None = None
    memo: str | None = None


class NoteFunnelPage(NoteFunnelPageBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class FortuneA8OfferBase(BaseModel):
    offer_name: str = Field(min_length=1)
    advertiser_name: str | None = None
    service_type: str | None = None
    affiliate_url: str | None = None
    lp_url: str | None = None
    reward_amount: float | None = None
    conversion_condition: str | None = None
    rejection_conditions: str | None = None
    first_time_bonus: str | None = None
    consultation_genres: str | None = None
    lp_impression: str | None = None
    approval_rate: str | None = None
    recommended_use: str | None = None
    prohibited_claims: str | None = None
    is_active: bool = True


class FortuneA8OfferCreate(FortuneA8OfferBase):
    pass


class FortuneA8OfferUpdate(BaseModel):
    offer_name: str | None = None
    advertiser_name: str | None = None
    service_type: str | None = None
    affiliate_url: str | None = None
    lp_url: str | None = None
    reward_amount: float | None = None
    conversion_condition: str | None = None
    rejection_conditions: str | None = None
    first_time_bonus: str | None = None
    consultation_genres: str | None = None
    lp_impression: str | None = None
    approval_rate: str | None = None
    recommended_use: str | None = None
    prohibited_claims: str | None = None
    is_active: bool | None = None


class FortuneA8Offer(FortuneA8OfferBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class ThreadsPostTemplateBase(BaseModel):
    name: str = Field(min_length=1)
    template_type: str = Field(min_length=1)
    target_theme: str | None = None
    structure: str = Field(min_length=1)
    example_post: str | None = None
    cta_style: str | None = None
    prohibited_patterns: str | None = None


class ThreadsPostTemplateCreate(ThreadsPostTemplateBase):
    pass


class ThreadsPostTemplateUpdate(BaseModel):
    name: str | None = None
    template_type: str | None = None
    target_theme: str | None = None
    structure: str | None = None
    example_post: str | None = None
    cta_style: str | None = None
    prohibited_patterns: str | None = None


class ThreadsPostTemplate(ThreadsPostTemplateBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class NoteCtaTemplateBase(BaseModel):
    name: str = Field(min_length=1)
    cta_type: str = Field(min_length=1)
    text: str = Field(min_length=1)
    target_note_page_id: int | None = None
    use_pr_disclosure: bool = True


class NoteCtaTemplateCreate(NoteCtaTemplateBase):
    pass


class NoteCtaTemplateUpdate(BaseModel):
    name: str | None = None
    cta_type: str | None = None
    text: str | None = None
    target_note_page_id: int | None = None
    use_pr_disclosure: bool | None = None


class NoteCtaTemplate(NoteCtaTemplateBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class Threads30DayPlanTask(BaseModel):
    id: int
    day_number: int
    phase: str
    title: str
    description: str | None = None
    status: str = "todo"
    created_at: str | None = None
    updated_at: str | None = None


class Threads30DayPlanTaskUpdate(BaseModel):
    status: str | None = None
    title: str | None = None
    description: str | None = None


class Threads30DayPlan(BaseModel):
    tasks: list[Threads30DayPlanTask]
    post_type_distribution: dict[str, int]


class TypefullyScheduleRequest(BaseModel):
    schedule_mode: ScheduleMode = "draft_only"
    scheduled_at: str | None = None


class TypefullyScheduleJob(BaseModel):
    id: int
    draft_id: int
    typefully_draft_id: str | None = None
    social_set_id: str | None = None
    scheduled_at: str | None = None
    status: str = "created"
    schedule_mode: str | None = "draft_only"
    typefully_url: str | None = None
    error_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class TypefullyScheduleResult(BaseModel):
    ok: bool
    job: TypefullyScheduleJob
    provider_result: dict
    message: str

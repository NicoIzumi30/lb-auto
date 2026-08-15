from typing import Literal
from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    email: str
    password: str


class UnitCreate(BaseModel):
    brand: str
    model: str
    year: int = Field(ge=1980, le=2100)
    color: str
    plate: str
    transmission: str
    km: int = Field(ge=0)
    vin: str | None = None
    engine_number: str | None = None
    source: str
    seller: str
    seller_phone: str
    location: str
    offer_price: int = Field(ge=0)
    target_price: int = Field(default=0, ge=0)
    cover_photo: str = Field(min_length=1)


class AssignmentInput(BaseModel):
    checker_id: int


class InspectionInput(BaseModel):
    body_score: int = Field(ge=1, le=100)
    major_accident: bool
    flood: bool
    engine_condition: str
    oil_condition: str
    suspension_condition: str
    tax_status: str
    notes: str = ""
    photos: list[str] = Field(min_length=8, max_length=8)


class InitialQCInput(BaseModel):
    approved: bool
    notes: str = ""


class LegalPrecheckInput(BaseModel):
    stnk_available: bool
    bpkb_available: bool
    vin_match: bool
    engine_match: bool
    tax_checked: bool
    notes: str = ""


class PurchaseDecisionInput(BaseModel):
    decision: Literal["DEAL", "REJECT"]
    final_price: int = Field(default=0, ge=0)
    payment_method: str = "Transfer Bank"
    rejection_reason: str = ""


class PaymentRequestInput(BaseModel):
    voucher_number: str
    amount: int = Field(gt=0)
    method: str = "Transfer Bank"


class PaymentConfirmInput(BaseModel):
    proof_url: str
    paid_at: str | None = None


class RepairHandoverInput(BaseModel):
    odometer: int = Field(ge=0)
    notes: str = ""


class RepairWorkItem(BaseModel):
    category: str
    panel: str
    progress: int = Field(ge=0, le=100)
    estimated_cost: int = Field(default=0, ge=0)
    actual_cost: int = Field(default=0, ge=0)


class RepairInput(BaseModel):
    categories: list[str] = []
    vendor: str
    stage: str
    estimated_cost: int = Field(default=0, ge=0)
    actual_cost: int = Field(default=0, ge=0)
    progress: int = Field(default=0, ge=0, le=100)
    target_date: str | None = None
    notes: str = ""
    work_items: list[RepairWorkItem] = []
    before_photos: list[str] = []
    after_photos: list[str] = []


class ApprovalInput(BaseModel):
    approved: bool
    notes: str = ""


class DocumentInput(BaseModel):
    stnk_status: str
    tax_due: str | None = None
    plate_due: str | None = None
    bpkb_status: str
    bpkb_number: str | None = None
    invoice_status: str
    receipt_available: bool = False
    owner_id_copy: bool = False
    items: list[str] = []


class LeadCreate(BaseModel):
    name: str
    phone: str
    unit_id: str | None = None
    source: str
    notes: str = ""
    assigned_to: int | None = None


class LeadStatusInput(BaseModel):
    status: Literal["NEW", "FOLLOW_UP", "TEST_DRIVE", "SPK_ISSUED", "CLOSED", "CANCELLED"]
    notes: str | None = None


class EventCreate(BaseModel):
    title: str
    event_type: Literal["INSPECTION", "REPAIR", "TAX", "TEST_DRIVE", "DELIVERY"]
    starts_at: str
    unit_id: str | None = None
    assigned_to: int | None = None
    notes: str = ""


class SaleCreate(BaseModel):
    unit_id: str
    buyer_name: str
    buyer_phone: str
    buyer_nik: str | None = None
    buyer_address: str | None = None
    payment_scheme: Literal["CASH", "CREDIT"]
    leasing_vendor: str | None = None
    tenor_months: int | None = None
    down_payment: int = Field(default=0, ge=0)
    final_price: int = Field(gt=0)
    delivered_at: str | None = None


class FinanceApprovalInput(BaseModel):
    approved: bool
    reference: str = ""
    notes: str = ""


class DeliveryScheduleInput(BaseModel):
    scheduled_at: str
    notes: str = ""


class DeliveryCompleteInput(BaseModel):
    notes: str = ""


class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8)
    role: str
    phone: str = ""


class UserStatusInput(BaseModel):
    active: bool


class UserContactInput(BaseModel):
    phone: str


class ListingInput(BaseModel):
    media_items: list[str] = []
    video_url: str | None = None
    cash_price: int = Field(gt=0)
    credit_price: int = Field(gt=0)
    description: str
    channels: list[str]
    publish: bool = False


class CreditSimulationInput(BaseModel):
    otr_price: int = Field(gt=0)
    total_down_payment: int = Field(ge=0)
    tenor_months: Literal[12, 24, 36, 48, 60]
    annual_interest_rate: float = Field(default=8.5, ge=0, le=100)
    admin_fee: int = Field(default=0, ge=0)
    insurance_fee: int = Field(default=0, ge=0)


class GreetingInput(BaseModel):
    media_url: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    consent: bool = False
    notes: str = ""

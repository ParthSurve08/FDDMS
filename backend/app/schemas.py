from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- AUTH SCHEMAS ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(donor|ngo|volunteer|admin)$")
    phone: str = Field(..., min_length=8, max_length=20)
    organization_name: Optional[str] = None
    registration_number: Optional[str] = None
    address: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str
    organization_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: str
    organization_name: Optional[str] = None
    registration_number: Optional[str] = None
    address: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- DONATION SCHEMAS ---
class DonationCreate(BaseModel):
    food_name: str = Field(..., min_length=2, max_length=150)
    category: str
    is_veg: bool = True
    quantity: float = Field(..., gt=0)
    unit: str
    prep_time: datetime
    expiry_time: datetime
    pickup_address: str
    description: Optional[str] = None

class DonationOut(BaseModel):
    id: int
    donor_id: int
    food_name: str
    category: str
    is_veg: bool
    quantity: float
    remaining_quantity: float
    unit: str
    prep_time: datetime
    expiry_time: datetime
    pickup_address: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    donor_name: Optional[str] = None
    donor_org: Optional[str] = None

    class Config:
        from_attributes = True

# --- REQUEST SCHEMAS ---
class RequestCreate(BaseModel):
    donation_id: int
    requested_quantity: float = Field(..., gt=0)
    unit: str
    purpose: str

class RequestOut(BaseModel):
    id: int
    donation_id: int
    ngo_id: int
    requested_quantity: float
    unit: str
    purpose: str
    status: str
    created_at: datetime
    ngo_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- DELIVERY TASK SCHEMAS ---
class DeliveryTaskOut(BaseModel):
    id: int
    donation_id: int
    request_id: int
    volunteer_id: Optional[int] = None
    volunteer_name: Optional[str] = None
    food_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    pickup_address: str
    dropoff_address: str
    special_instructions: Optional[str] = None
    status: str
    assigned_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- PICKUP SCHEDULE SCHEMAS ---
class PickupScheduleCreate(BaseModel):
    donation_id: int
    scheduled_date: datetime
    scheduled_time: str
    pickup_window: str
    packaging_method: str
    contact_person: str

class PickupScheduleOut(BaseModel):
    id: int
    donation_id: int
    donor_id: int
    food_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    scheduled_date: datetime
    scheduled_time: str
    pickup_window: str
    packaging_method: str
    contact_person: str
    assigned_volunteer: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- CHATBOT & FAQ SCHEMAS ---
class ChatMessageRequest(BaseModel):
    message: str
    language: Optional[str] = "en"

class ChatMessageResponse(BaseModel):
    reply: str
    matched_intent: Optional[str] = None
    suggested_actions: Optional[List[str]] = None

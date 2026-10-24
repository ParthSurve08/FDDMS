import os
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import engine, get_db, Base
from .models import User, FoodDonation, FoodRequest, DeliveryTask, PickupSchedule, AuditLog
from .schemas import (
    UserRegister, UserLogin, Token, UserOut,
    DonationCreate, DonationOut, RequestCreate, RequestOut,
    DeliveryTaskOut, PickupScheduleCreate, PickupScheduleOut,
    ChatMessageRequest, ChatMessageResponse
)
from .auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_role
)
from .data_structures import (
    TaskFIFOQueue, FoodExpiryPriorityQueue, FAQInvertedIndex, LogisticsNetworkGraph
)

# Initialize Database tables if not already present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FoodShare API",
    description="REST API for FoodShare – Food Donation & Distribution Management System",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize in-memory computer science data structures
fifo_task_queue = TaskFIFOQueue()
expiry_pq = FoodExpiryPriorityQueue()
faq_index = FAQInvertedIndex()
city_graph = LogisticsNetworkGraph()


# ==============================================================================
# AUTHENTICATION & USER MANAGEMENT ENDPOINTS
# ==============================================================================
@app.post("/api/v1/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    if user_in.role == "ngo" and (not user_in.organization_name or not user_in.registration_number):
        raise HTTPException(status_code=400, detail="NGO Name and Registration number are required for NGO accounts.")

    new_user = User(
        name=user_in.name,
        email=user_in.email.lower(),
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
        phone=user_in.phone,
        organization_name=user_in.organization_name,
        registration_number=user_in.registration_number,
        address=user_in.address,
        status="active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Audit log
    audit = AuditLog(user_id=new_user.id, action="USER_REGISTER", details=f"Registered as {new_user.role}")
    db.add(audit)
    db.commit()

    token = create_access_token(data={"sub": new_user.id, "role": new_user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "name": new_user.name,
        "role": new_user.role,
        "organization_name": new_user.organization_name
    }

@app.post("/api/v1/auth/login", response_model=Token)
def login_user(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email.lower()).first()
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if user.status == "suspended":
        raise HTTPException(status_code=403, detail="Account is suspended. Contact administration.")

    token = create_access_token(data={"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "role": user.role,
        "organization_name": user.organization_name
    }

@app.get("/api/v1/auth/me", response_model=UserOut)
def get_profile(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return user


# ==============================================================================
# FOOD DONATIONS ENDPOINTS (DONOR & NGO)
# ==============================================================================
@app.get("/api/v1/donations", response_model=List[DonationOut])
def list_available_donations(
    category: Optional[str] = None,
    is_veg: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FoodDonation).filter(FoodDonation.status == "available", FoodDonation.remaining_quantity > 0)
    if category and category != "All":
        query = query.filter(FoodDonation.category == category)
    if is_veg is not None:
        query = query.filter(FoodDonation.is_veg == is_veg)
    if search:
        query = query.filter(
            (FoodDonation.food_name.ilike(f"%{search}%")) |
            (FoodDonation.pickup_address.ilike(f"%{search}%"))
        )

    donations = query.order_by(FoodDonation.expiry_time.asc()).all()
    out = []
    for d in donations:
        item = DonationOut.from_orm(d)
        item.donor_name = d.donor.name if d.donor else None
        item.donor_org = d.donor.organization_name if d.donor else None
        out.append(item)
    return out

@app.post("/api/v1/donations", response_model=DonationOut, status_code=status.HTTP_201_CREATED)
def create_donation(
    donation_in: DonationCreate,
    user: User = Depends(require_role(["donor", "admin"])),
    db: Session = Depends(get_db)
):
    if donation_in.expiry_time <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Expiry time must be in the future.")

    new_donation = FoodDonation(
        donor_id=user.id,
        food_name=donation_in.food_name,
        category=donation_in.category,
        is_veg=donation_in.is_veg,
        quantity=donation_in.quantity,
        remaining_quantity=donation_in.quantity,
        unit=donation_in.unit,
        prep_time=donation_in.prep_time,
        expiry_time=donation_in.expiry_time,
        pickup_address=donation_in.pickup_address,
        description=donation_in.description,
        status="available"
    )
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)

    # In-memory priority queue registration
    expiry_pq.push({
        "id": new_donation.id,
        "name": new_donation.food_name,
        "expiry_timestamp": new_donation.expiry_time.timestamp(),
        "quantity": float(new_donation.quantity),
        "unit": new_donation.unit
    })

    return DonationOut.from_orm(new_donation)


# ==============================================================================
# NGO FOOD REQUEST / CLAIMING (ATOMIC CONCURRENCY PROTECTED)
# ==============================================================================
@app.post("/api/v1/requests", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def claim_food(
    req_in: RequestCreate,
    user: User = Depends(require_role(["ngo", "admin"])),
    db: Session = Depends(get_db)
):
    donation = db.query(FoodDonation).filter(FoodDonation.id == req_in.donation_id).with_for_update().first()
    if not donation or donation.status != "available":
        raise HTTPException(status_code=400, detail="Donation is no longer available.")

    if req_in.requested_quantity > float(donation.remaining_quantity):
        raise HTTPException(status_code=400, detail=f"Requested quantity exceeds remaining ({donation.remaining_quantity} {donation.unit}).")

    # Atomic decrement
    donation.remaining_quantity = float(donation.remaining_quantity) - req_in.requested_quantity
    if donation.remaining_quantity <= 0:
        donation.status = "accepted"

    new_req = FoodRequest(
        donation_id=donation.id,
        ngo_id=user.id,
        requested_quantity=req_in.requested_quantity,
        unit=req_in.unit,
        purpose=req_in.purpose,
        status="accepted"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    # Queue delivery task for volunteers
    new_task = DeliveryTask(
        donation_id=donation.id,
        request_id=new_req.id,
        volunteer_id=None,
        pickup_address=donation.pickup_address,
        dropoff_address=user.address,
        special_instructions=f"Transport to {user.organization_name or user.name}. {req_in.purpose}",
        status="available"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Enqueue to FIFO task queue
    fifo_task_queue.enqueue({
        "task_id": new_task.id,
        "food_name": donation.food_name,
        "quantity": req_in.requested_quantity,
        "unit": req_in.unit,
        "pickup": new_task.pickup_address,
        "dropoff": new_task.dropoff_address
    })

    return RequestOut.from_orm(new_req)


# ==============================================================================
# VOLUNTEER DISPATCH & DELIVERY STATE MACHINE
# ==============================================================================
@app.get("/api/v1/deliveries/available", response_model=List[DeliveryTaskOut])
def list_available_deliveries(db: Session = Depends(get_db)):
    tasks = db.query(DeliveryTask).filter(DeliveryTask.status == "available").all()
    out = []
    for t in tasks:
        item = DeliveryTaskOut.from_orm(t)
        if t.donation:
            item.food_name = t.donation.food_name
            item.quantity = float(t.request.requested_quantity) if t.request else float(t.donation.quantity)
            item.unit = t.donation.unit
        out.append(item)
    return out

@app.post("/api/v1/deliveries/{task_id}/accept")
def accept_delivery(
    task_id: int,
    user: User = Depends(require_role(["volunteer", "admin"])),
    db: Session = Depends(get_db)
):
    task = db.query(DeliveryTask).filter(DeliveryTask.id == task_id).first()
    if not task or task.status != "available":
        raise HTTPException(status_code=400, detail="Delivery task is not available for assignment.")

    task.volunteer_id = user.id
    task.status = "assigned"
    task.assigned_at = datetime.utcnow()
    db.commit()
    return {"message": "Task accepted successfully.", "task_id": task.id}

@app.put("/api/v1/deliveries/{task_id}/status")
def update_delivery_status(
    task_id: int,
    new_status: str = Query(..., pattern="^(picked_up|in_transit|delivered)$"),
    user: User = Depends(require_role(["volunteer", "admin"])),
    db: Session = Depends(get_db)
):
    task = db.query(DeliveryTask).filter(DeliveryTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    task.status = new_status
    if new_status == "delivered":
        task.delivered_at = datetime.utcnow()
        if task.donation:
            task.donation.status = "delivered"
    elif task.donation:
        task.donation.status = new_status

    db.commit()
    return {"message": f"Task updated to {new_status}.", "task_id": task.id}


# ==============================================================================
# LOGISTICS & PICKUP SCHEDULING (DONOR LOGISTICS)
# ==============================================================================
@app.get("/api/v1/logistics/schedules", response_model=List[PickupScheduleOut])
def get_pickup_schedules(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(PickupSchedule)
    if user and user.role == "donor":
        query = query.filter(PickupSchedule.donor_id == user.id)
    schedules = query.order_by(PickupSchedule.scheduled_date.desc()).all()
    out = []
    for s in schedules:
        item = PickupScheduleOut.from_orm(s)
        if s.donation:
            item.food_name = s.donation.food_name
            item.quantity = float(s.donation.quantity)
            item.unit = s.donation.unit
        out.append(item)
    return out

@app.post("/api/v1/logistics/schedules", response_model=PickupScheduleOut, status_code=status.HTTP_201_CREATED)
def create_pickup_schedule(
    sched_in: PickupScheduleCreate,
    user: User = Depends(require_role(["donor", "admin"])),
    db: Session = Depends(get_db)
):
    donation = db.query(FoodDonation).filter(FoodDonation.id == sched_in.donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")

    new_schedule = PickupSchedule(
        donation_id=sched_in.donation_id,
        donor_id=user.id,
        scheduled_date=sched_in.scheduled_date,
        scheduled_time=sched_in.scheduled_time,
        pickup_window=sched_in.pickup_window,
        packaging_method=sched_in.packaging_method,
        contact_person=sched_in.contact_person,
        status="Scheduled"
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return PickupScheduleOut.from_orm(new_schedule)


# ==============================================================================
# CHATBOT AI ASSISTANT ENDPOINT (INVERTED INDEX ENGINE)
# ==============================================================================
@app.post("/api/v1/chatbot/message", response_model=ChatMessageResponse)
def chatbot_assistant(
    chat_req: ChatMessageRequest,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = chat_req.message.lower().strip()

    # Security check
    if any(k in msg for k in ["password", "secret", "credential", "database", "drop table", "api key"]):
        return {
            "reply": "Security Notice: I am not authorized to disclose credentials, user passwords, API keys, or private database details.",
            "matched_intent": "security_guardrail"
        }

    # Contextual user status check
    if any(k in msg for k in ["who am i", "my status", "my donation", "my request", "my task"]):
        if not user:
            return {
                "reply": "You are currently browsing as a guest. Please sign in or register to access your live personal donations, requests, or delivery assignments.",
                "matched_intent": "user_status_guest"
            }
        if user.role == "donor":
            dons = db.query(FoodDonation).filter(FoodDonation.donor_id == user.id).count()
            return {
                "reply": f"You are signed in as {user.name} (Donor • {user.organization_name or 'Individual'}). You have {dons} recorded donation(s).",
                "matched_intent": "user_status_donor"
            }
        if user.role == "ngo":
            reqs = db.query(FoodRequest).filter(FoodRequest.ngo_id == user.id).count()
            return {
                "reply": f"You are signed in as {user.name} ({user.organization_name or 'Verified NGO'}). You have placed {reqs} food claim(s).",
                "matched_intent": "user_status_ngo"
            }

    # Inverted Index query
    reply = faq_index.query(msg)
    if reply:
        return {"reply": reply, "matched_intent": "faq_inverted_index"}

    # Exact Fallback
    return {
        "reply": "I'm sorry, I couldn't resolve that. Please try another question or contact the administrator.",
        "matched_intent": "fallback"
    }


# ==============================================================================
# DATA STRUCTURES & ALGORITHM DEMO ENDPOINTS
# ==============================================================================
@app.get("/api/v1/ds/queue")
def get_queue_items():
    return {"queue_head_to_tail": fifo_task_queue.to_list(), "size": fifo_task_queue.size()}

@app.post("/api/v1/ds/dijkstra")
def compute_route(origin: str = Query(...), destination: str = Query(...)):
    return city_graph.dijkstra_shortest_path(origin, destination)


# ==============================================================================
# SYSTEM METRICS & HEALTH CHECK
# ==============================================================================
@app.get("/api/v1/stats")
def get_live_stats(db: Session = Depends(get_db)):
    active_donations = db.query(FoodDonation).filter(FoodDonation.status == "available").count()
    verified_ngos = db.query(User).filter(User.role == "ngo", User.status == "active").count()
    volunteers = db.query(User).filter(User.role == "volunteer", User.status == "active").count()
    completed_deliveries = db.query(DeliveryTask).filter(DeliveryTask.status == "delivered").count()
    return {
        "active_donations": active_donations,
        "verified_ngos": verified_ngos,
        "active_volunteers": volunteers,
        "completed_deliveries": completed_deliveries
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "FoodShare", "timestamp": datetime.utcnow().isoformat()}

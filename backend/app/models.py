from sqlalchemy import Column, Integer, String, Boolean, Numeric, Text, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(191), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SqlEnum('donor', 'ngo', 'volunteer', 'admin', name='user_roles'), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    organization_name = Column(String(150), nullable=True)
    registration_number = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    status = Column(SqlEnum('active', 'suspended', 'pending_verification', name='user_statuses'), default='active', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donations = relationship("FoodDonation", back_populates="donor")
    requests = relationship("FoodRequest", back_populates="ngo")
    deliveries = relationship("DeliveryTask", back_populates="volunteer")
    schedules = relationship("PickupSchedule", back_populates="donor")


class FoodDonation(Base):
    __tablename__ = "food_donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    food_name = Column(String(150), nullable=False)
    category = Column(SqlEnum('Cooked Meals', 'Bakery & Bread', 'Raw Produce', 'Packaged Goods', 'Dairy & Refrigerated', 'Beverages', name='food_categories'), nullable=False)
    is_veg = Column(Boolean, default=True, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    remaining_quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(SqlEnum('plates', 'kg', 'packets', 'servings', name='quantity_units'), nullable=False)
    prep_time = Column(DateTime, nullable=False)
    expiry_time = Column(DateTime, nullable=False, index=True)
    pickup_address = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SqlEnum('available', 'requested', 'accepted', 'picked_up', 'in_transit', 'delivered', 'cancelled', name='donation_statuses'), default='available', nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donor = relationship("User", back_populates="donations")
    requests = relationship("FoodRequest", back_populates="donation", cascade="all, delete-orphan")
    deliveries = relationship("DeliveryTask", back_populates="donation", cascade="all, delete-orphan")
    schedules = relationship("PickupSchedule", back_populates="donation", cascade="all, delete-orphan")


class FoodRequest(Base):
    __tablename__ = "food_requests"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("food_donations.id", ondelete="CASCADE"), nullable=False)
    ngo_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    requested_quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(SqlEnum('plates', 'kg', 'packets', 'servings', name='req_units'), nullable=False)
    purpose = Column(Text, nullable=False)
    status = Column(SqlEnum('pending', 'accepted', 'rejected', 'cancelled', name='request_statuses'), default='accepted', nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donation = relationship("FoodDonation", back_populates="requests")
    ngo = relationship("User", back_populates="requests")
    deliveries = relationship("DeliveryTask", back_populates="request")


class DeliveryTask(Base):
    __tablename__ = "delivery_tasks"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("food_donations.id", ondelete="CASCADE"), nullable=False)
    request_id = Column(Integer, ForeignKey("food_requests.id", ondelete="CASCADE"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    pickup_address = Column(Text, nullable=False)
    dropoff_address = Column(Text, nullable=False)
    special_instructions = Column(Text, nullable=True)
    status = Column(SqlEnum('available', 'assigned', 'picked_up', 'in_transit', 'delivered', 'failed', name='delivery_statuses'), default='available', nullable=False, index=True)
    assigned_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donation = relationship("FoodDonation", back_populates="deliveries")
    request = relationship("FoodRequest", back_populates="deliveries")
    volunteer = relationship("User", back_populates="deliveries")


class PickupSchedule(Base):
    __tablename__ = "pickup_schedules"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("food_donations.id", ondelete="CASCADE"), nullable=False)
    donor_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    scheduled_time = Column(String(20), nullable=False)
    pickup_window = Column(String(50), nullable=False)
    packaging_method = Column(String(100), nullable=False)
    contact_person = Column(String(150), nullable=False)
    status = Column(SqlEnum('Scheduled', 'Ready for Pickup', 'Dispatched', 'Completed', 'Cancelled', name='schedule_statuses'), default='Scheduled', nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donation = relationship("FoodDonation", back_populates="schedules")
    donor = relationship("User", back_populates="schedules")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(60), nullable=False, index=True)
    details = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

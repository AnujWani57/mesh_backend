from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Float

from app.db.database import Base


class Mine(Base):
    __tablename__ = "mines"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    mine_id = Column(String, nullable=False)
    sector_id = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    joining_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    avatar_url = Column(String, nullable=True)


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(String, primary_key=True)
    mine_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    supervisor_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="safe")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True)
    sector_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="online")
    signal_strength = Column(String, nullable=False, default="Excellent")
    battery = Column(Integer, nullable=False, default=100)
    last_updated = Column(DateTime, default=datetime.utcnow)


class WearableDevice(Base):
    __tablename__ = "wearable_devices"

    id = Column(String, primary_key=True)
    node_id = Column(String, nullable=False)
    sector_id = Column(String, nullable=False)
    worker_name = Column(String, nullable=False)
    worker_id = Column(String, nullable=False)
    battery = Column(Integer, nullable=False, default=100)
    signal_strength = Column(Integer, nullable=False, default=-60)
    status = Column(String, nullable=False, default="online")
    last_updated = Column(DateTime, default=datetime.utcnow)


class Reading(Base):
    __tablename__ = "readings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    device_id = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    methane = Column(Float, nullable=False)
    carbon_monoxide = Column(Float, nullable=False)
    oxygen = Column(Float, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True)
    device_id = Column(String, nullable=False)
    node_id = Column(String, nullable=False)
    sector_id = Column(String, nullable=False)
    worker_name = Column(String, nullable=False)
    hazard = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="warning")
    state = Column(String, nullable=False, default="active")
    acknowledged_by = Column(String, nullable=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    methane = Column(Float, nullable=False)
    carbon_monoxide = Column(Float, nullable=False)
    oxygen = Column(Float, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    scope_id = Column(String, nullable=False)
    temperature_warning = Column(Float, nullable=False, default=35)
    temperature_critical = Column(Float, nullable=False, default=45)
    humidity_warning = Column(Float, nullable=False, default=70)
    humidity_critical = Column(Float, nullable=False, default=85)
    methane_warning = Column(Float, nullable=False, default=1000)
    methane_critical = Column(Float, nullable=False, default=5000)
    co_warning = Column(Float, nullable=False, default=25)
    co_critical = Column(Float, nullable=False, default=50)
    oxygen_warning_low = Column(Float, nullable=False, default=19.5)
    oxygen_critical_low = Column(Float, nullable=False, default=18)
    oxygen_warning_high = Column(Float, nullable=False, default=23.5)
    oxygen_critical_high = Column(Float, nullable=False, default=25)

from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.schemas import (
    AdminDashboardResponse,
    AdminEnvironmentResponse,
    AdminStatsResponse,
    SectorSummary,
    SupervisorSummary,
    TrendPoint,
)
from app.db.database import get_db
from app.db.models import Alert, Node, Reading, Sector, User, WearableDevice

router = APIRouter(prefix="", tags=["admin"])


@router.get("/admin/stats", response_model=AdminStatsResponse)
def admin_stats(db: Session = Depends(get_db)):
    total_sectors = db.query(func.count(Sector.id)).scalar() or 0
    total_nodes = db.query(func.count(Node.id)).scalar() or 0
    total_devices = db.query(func.count(WearableDevice.id)).scalar() or 0
    active_devices = db.query(func.count(WearableDevice.id)).filter(WearableDevice.status == "online").scalar() or 0
    inactive_devices = total_devices - active_devices
    active_alerts = db.query(func.count(Alert.id)).filter(Alert.state == "active").scalar() or 0
    return {
        "totalSectors": total_sectors,
        "totalNodes": total_nodes,
        "totalDevices": total_devices,
        "activeDevices": active_devices,
        "inactiveDevices": inactive_devices,
        "activeAlerts": active_alerts,
        "workersInside": total_devices,
    }


@router.get("/admin/environment", response_model=AdminEnvironmentResponse)
def admin_environment(db: Session = Depends(get_db)):
    avg_values = db.query(
        func.avg(Reading.temperature),
        func.avg(Reading.humidity),
        func.avg(Reading.methane),
        func.avg(Reading.carbon_monoxide),
        func.avg(Reading.oxygen),
    ).one()
    avg_readings = {
        "temperature": float(avg_values[0] or 0.0),
        "humidity": float(avg_values[1] or 0.0),
        "methane": float(avg_values[2] or 0.0),
        "carbonMonoxide": float(avg_values[3] or 0.0),
        "oxygen": float(avg_values[4] or 0.0),
    }
    recent_readings = (
        db.query(Reading)
        .order_by(Reading.recorded_at.desc())
        .limit(5)
        .all()
    )
    trends = [
        {
            "time": r.recorded_at.strftime("%H:%M"),
            "temperature": r.temperature,
            "humidity": r.humidity,
            "methane": r.methane,
            "carbonMonoxide": r.carbon_monoxide,
            "oxygen": r.oxygen,
        }
        for r in reversed(recent_readings)
    ]
    health_counts = {
        "safe": db.query(func.count(Sector.id)).filter(Sector.status == "safe").scalar() or 0,
        "warning": db.query(func.count(Sector.id)).filter(Sector.status == "warning").scalar() or 0,
        "critical": db.query(func.count(Sector.id)).filter(Sector.status == "critical").scalar() or 0,
    }
    return {
        "averageReadings": avg_readings,
        "trends": trends,
        "health": health_counts,
    }


@router.get("/sectors", response_model=List[SectorSummary])
def get_sectors(db: Session = Depends(get_db)):
    sectors = db.query(Sector).all()
    response = []
    for sector in sectors:
        supervisor = db.query(User).filter(User.id == sector.supervisor_id).first()
        response.append(
            {
                "id": sector.id,
                "name": sector.name,
                "supervisor": {
                    "id": supervisor.id if supervisor else None,
                    "name": supervisor.name if supervisor else None,
                    "phone": supervisor.phone if supervisor else None,
                    "email": supervisor.email if supervisor else None,
                    "employeeId": supervisor.employee_id if supervisor else None,
                },
                "activeNodes": db.query(Node).filter(Node.sector_id == sector.id, Node.status == "online").count(),
                "inactiveNodes": db.query(Node).filter(Node.sector_id == sector.id, Node.status != "online").count(),
                "averageReadings": {"temperature": 29, "humidity": 58, "methane": 810, "carbonMonoxide": 10, "oxygen": 20.7},
                "status": sector.status,
            }
        )
    return response


@router.get("/sectors/{sector_id}", response_model=SectorSummary)
def get_sector(sector_id: str, db: Session = Depends(get_db)):
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if not sector:
        return {}
    supervisor = db.query(User).filter(User.id == sector.supervisor_id).first()
    return {
        "id": sector.id,
        "name": sector.name,
        "supervisor": {
            "id": supervisor.id if supervisor else None,
            "name": supervisor.name if supervisor else None,
            "phone": supervisor.phone if supervisor else None,
            "email": supervisor.email if supervisor else None,
            "employeeId": supervisor.employee_id if supervisor else None,
        },
        "activeNodes": db.query(Node).filter(Node.sector_id == sector.id, Node.status == "online").count(),
        "inactiveNodes": db.query(Node).filter(Node.sector_id == sector.id, Node.status != "online").count(),
        "averageReadings": {"temperature": 29, "humidity": 58, "methane": 810, "carbonMonoxide": 10, "oxygen": 20.7},
        "status": sector.status,
    }


@router.get("/supervisors", response_model=List[SupervisorSummary])
def get_supervisors(db: Session = Depends(get_db)):
    supervisors = db.query(User).filter(User.role == "supervisor").all()
    response = []
    for supervisor in supervisors:
        sector = db.query(Sector).filter(Sector.id == supervisor.sector_id).first()
        response.append(
            {
                "id": supervisor.id,
                "name": supervisor.name,
                "employeeId": supervisor.employee_id,
                "gender": supervisor.gender,
                "phone": supervisor.phone,
                "email": supervisor.email,
                "sectorId": supervisor.sector_id,
                "sectorName": sector.name if sector else None,
                "experienceYears": supervisor.experience_years,
                "status": "online",
                "nodeCount": db.query(Node).filter(Node.sector_id == supervisor.sector_id).count(),
            }
        )
    return response

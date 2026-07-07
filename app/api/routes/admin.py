from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import AdminDashboardResponse, SectorSummary, SupervisorSummary
from app.db.database import get_db
from app.db.models import Alert, Node, Sector, User, WearableDevice

router = APIRouter(prefix="", tags=["admin"])


@router.get("/admin/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard(db: Session = Depends(get_db)):
    sectors = db.query(Sector).all()
    nodes = db.query(Node).all()
    devices = db.query(WearableDevice).all()
    alerts = db.query(Alert).filter(Alert.state == "active").all()
    return {
        "totalSectors": len(sectors),
        "totalNodes": len(nodes),
        "totalDevices": len(devices),
        "activeDevices": len([d for d in devices if d.status == "online"]),
        "inactiveDevices": len([d for d in devices if d.status != "online"]),
        "activeAlerts": len(alerts),
        "workersInside": len(devices),
        "averageReadings": {
            "temperature": 31,
            "humidity": 61,
            "methane": 1180,
            "carbonMonoxide": 17,
            "oxygen": 20.3,
        },
        "trends": [
            {"time": "09:00", "temperature": 31, "humidity": 61, "methane": 1180, "carbonMonoxide": 17, "oxygen": 20.3}
        ],
        "health": {"safe": 0, "warning": 2, "critical": 1},
        "recentAlerts": [
            {
                "id": alert.id,
                "deviceId": alert.device_id,
                "workerName": alert.worker_name,
                "nodeId": alert.node_id,
                "sectorId": alert.sector_id,
                "hazard": alert.hazard,
                "severity": alert.severity,
                "time": alert.created_at.isoformat(),
                "state": alert.state,
                "acknowledgedBy": alert.acknowledged_by,
                "readings": {
                    "temperature": alert.temperature,
                    "humidity": alert.humidity,
                    "methane": alert.methane,
                    "carbonMonoxide": alert.carbon_monoxide,
                    "oxygen": alert.oxygen,
                },
                "coordinates": {"x": alert.x, "y": alert.y, "z": alert.z},
            }
            for alert in alerts[:5]
        ],
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

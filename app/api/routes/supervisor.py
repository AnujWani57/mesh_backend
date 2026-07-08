from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app.api.schemas import (
    NodeStatusItem,
    SupervisorEnvironmentResponse,
    SupervisorHomeResponse,
    SupervisorStatsResponse,
    TrendPoint,
)
from app.db.database import get_db
from app.db.models import Alert, Node, Reading, Sector, WearableDevice

router = APIRouter(prefix="", tags=["supervisor"])


@router.get("/supervisor/home", response_model=SupervisorHomeResponse)
def supervisor_home(sector_id: str = Query(..., alias="sectorId"), db: Session = Depends(get_db)):
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    nodes = db.query(Node).filter(Node.sector_id == sector_id).all()
    devices = db.query(WearableDevice).filter(WearableDevice.sector_id == sector_id).all()
    alerts = db.query(Alert).filter(Alert.sector_id == sector_id).order_by(Alert.created_at.desc()).limit(5).all()
    return {
        "sectorId": sector_id,
        "sectorName": sector.name if sector else None,
        "averageReadings": {"temperature": 29, "humidity": 58, "methane": 810, "carbonMonoxide": 10, "oxygen": 20.7},
        "status": sector.status if sector else "safe",
        "trends": [{"time": "09:00", "temperature": 29, "humidity": 58, "methane": 810, "carbonMonoxide": 10, "oxygen": 20.7}],
        "nodes": [{"id": node.id, "name": node.name, "status": node.status} for node in nodes],
        "totalWorkers": len(devices),
        "devicesOnline": len([device for device in devices if device.status == "online"]),
        "sosCount": len([alert for alert in alerts if alert.hazard == "SOS Button Pressed"]),
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
            for alert in alerts
        ],
    }


@router.get("/supervisor/sector/{sector_id}/stats", response_model=SupervisorStatsResponse)
def supervisor_sector_stats(sector_id: str, db: Session = Depends(get_db)):
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    devices = db.query(WearableDevice).filter(WearableDevice.sector_id == sector_id).all()
    alerts = db.query(Alert).filter(Alert.sector_id == sector_id).all()
    return {
        "sectorId": sector_id,
        "sectorName": sector.name if sector else None,
        "status": sector.status if sector else "safe",
        "totalWorkers": len(devices),
        "devicesOnline": len([device for device in devices if device.status == "online"]),
        "sosCount": len([alert for alert in alerts if alert.hazard == "SOS Button Pressed"]),
    }


@router.get("/supervisor/sector/{sector_id}/environment", response_model=SupervisorEnvironmentResponse)
def supervisor_sector_environment(sector_id: str, db: Session = Depends(get_db)):
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    readings = (
        db.query(Reading)
        .join(WearableDevice, Reading.device_id == WearableDevice.id)
        .filter(WearableDevice.sector_id == sector_id)
        .order_by(Reading.recorded_at.desc())
        .limit(5)
        .all()
    )
    avg_values = (
        db.query(
            func.avg(Reading.temperature),
            func.avg(Reading.humidity),
            func.avg(Reading.methane),
            func.avg(Reading.carbon_monoxide),
            func.avg(Reading.oxygen),
        )
        .join(WearableDevice, Reading.device_id == WearableDevice.id)
        .filter(WearableDevice.sector_id == sector_id)
        .one()
    )
    avg_readings = {
        "temperature": float(avg_values[0] or 0.0),
        "humidity": float(avg_values[1] or 0.0),
        "methane": float(avg_values[2] or 0.0),
        "carbonMonoxide": float(avg_values[3] or 0.0),
        "oxygen": float(avg_values[4] or 0.0),
    }
    trends = [
        {
            "time": r.recorded_at.strftime("%H:%M"),
            "temperature": r.temperature,
            "humidity": r.humidity,
            "methane": r.methane,
            "carbonMonoxide": r.carbon_monoxide,
            "oxygen": r.oxygen,
        }
        for r in reversed(readings)
    ]
    return {
        "averageReadings": avg_readings,
        "trends": trends,
    }


@router.get("/supervisor/sector/{sector_id}/nodes", response_model=List[NodeStatusItem])
def supervisor_sector_nodes(sector_id: str, db: Session = Depends(get_db)):
    nodes = db.query(Node).filter(Node.sector_id == sector_id).all()
    return [
        {"id": node.id, "name": node.name, "status": node.status}
        for node in nodes
    ]

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas import SupervisorHomeResponse
from app.db.database import get_db
from app.db.models import Alert, Node, Sector, WearableDevice

router = APIRouter(prefix="", tags=["supervisor"])


@router.get("/supervisor/home", response_model=SupervisorHomeResponse)
def supervisor_home(sector_id: str = Query(...), db: Session = Depends(get_db)):
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

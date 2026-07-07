from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas import AlertSummary
from app.db.database import get_db
from app.db.models import Alert

router = APIRouter(prefix="", tags=["alerts"])


@router.get("/alerts", response_model=List[AlertSummary])
def get_alerts(sector_id: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Alert)
    if sector_id:
        query = query.filter(Alert.sector_id == sector_id)
    alerts = query.all()
    return [
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
    ]


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertSummary, status_code=status.HTTP_200_OK)
def acknowledge_alert(alert_id: str, payload: Dict, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    alert.state = "resolved"
    alert.acknowledged_by = payload.get("by")
    db.commit()
    return {
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

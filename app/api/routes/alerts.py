from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.schemas import AlertListResponse, AlertListItem, AlertSummary
from app.db.database import get_db
from app.db.models import Alert

router = APIRouter(prefix="", tags=["alerts"])


def to_alert_list_item(alert: Alert) -> AlertListItem:
    hazard_text = alert.hazard.upper()
    if "METHANE" in hazard_text:
        reading_value = alert.methane
        reading_unit = "ppm"
    elif "CO" in hazard_text and "CARBON" in hazard_text or "CO" == hazard_text:
        reading_value = alert.carbon_monoxide
        reading_unit = "ppm"
    elif "TEMPERATURE" in hazard_text:
        reading_value = alert.temperature
        reading_unit = "°C"
    elif "HUMIDITY" in hazard_text:
        reading_value = alert.humidity
        reading_unit = "%"
    elif "OXYGEN" in hazard_text:
        reading_value = alert.oxygen
        reading_unit = "%"
    else:
        reading_value = None
        reading_unit = None

    return AlertListItem(
        id=alert.id,
        deviceId=alert.device_id,
        nodeId=alert.node_id,
        sectorId=alert.sector_id,
        time=alert.created_at.isoformat(),
        hazard=alert.hazard,
        severity=alert.severity,
        state=alert.state,
        acknowledgedBy=alert.acknowledged_by,
        readingValue=reading_value,
        readingUnit=reading_unit,
    )


def get_paginated_alerts(query, page: int, limit: int):
    total_count = query.count()
    items = (
        query.order_by(Alert.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
    return {
        "data": [to_alert_list_item(alert) for alert in items],
        "meta": {
            "page": page,
            "limit": limit,
            "totalCount": total_count,
            "totalPages": total_pages,
        },
    }


@router.get("/alerts/active", response_model=AlertListResponse)
def get_active_alerts(
    sector_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(Alert.state == "active")
    if sector_id:
        query = query.filter(Alert.sector_id == sector_id)
    return get_paginated_alerts(query, page, limit)


@router.get("/alerts/resolved", response_model=AlertListResponse)
def get_resolved_alerts(
    sector_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(Alert.state == "resolved")
    if sector_id:
        query = query.filter(Alert.sector_id == sector_id)
    return get_paginated_alerts(query, page, limit)


@router.get("/alerts/summary")
def get_alerts_summary(
    sector_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    active_query = db.query(Alert).filter(Alert.state == "active")
    resolved_query = db.query(Alert).filter(Alert.state == "resolved")
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    today_query = db.query(Alert).filter(Alert.created_at >= today_start, Alert.created_at < tomorrow_start)

    if sector_id:
        active_query = active_query.filter(Alert.sector_id == sector_id)
        resolved_query = resolved_query.filter(Alert.sector_id == sector_id)
        today_query = today_query.filter(Alert.sector_id == sector_id)

    return {
        "activeCount": active_query.count(),
        "resolvedCount": resolved_query.count(),
        "totalToday": today_query.count(),
    }


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

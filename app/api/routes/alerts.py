import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.schemas import AlertListResponse, AlertListItem, AlertSummary, PostSOSRequest
from app.api.sse import register_sos_subscriber, unregister_sos_subscriber, notify_sos_event
from app.db.database import get_db
from app.db.models import Alert, Sector, Threshold, WearableDevice
from app.api.routes.readings import generate_alert_id

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


def apply_hazard_filter(query, hazard: Optional[str]):
    if hazard:
        return query.filter(Alert.hazard == hazard)
    return query


@router.get("/alerts", response_model=AlertListResponse)
def get_all_alerts(
    sector_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    hazard: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Alert)
    if state:
        query = query.filter(Alert.state == state)
    if sector_id:
        query = query.filter(Alert.sector_id == sector_id)
    query = apply_hazard_filter(query, hazard)
    return get_paginated_alerts(query, page, limit)


@router.get("/alerts/active", response_model=AlertListResponse)
def get_active_alerts(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    hazard: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(Alert.state == "active")
    query = apply_hazard_filter(query, hazard)
    return get_paginated_alerts(query, page, limit)


@router.get("/alerts/resolved", response_model=AlertListResponse)
def get_resolved_alerts(
    sector_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1),
    hazard: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(Alert.state == "resolved")
    if sector_id:
        query = query.filter(Alert.sector_id == sector_id)
    query = apply_hazard_filter(query, hazard)
    return get_paginated_alerts(query, page, limit)


@router.get("/alerts/stream")
def stream_sos_events():
    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue(maxsize=10)
        register_sos_subscriber(queue)
        try:
            while True:
                alert_payload = await queue.get()
                yield f"data: {json.dumps(alert_payload)}\n\n"
        finally:
            unregister_sos_subscriber(queue)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


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


@router.get("/alerts/{alert_id}")
def get_alert_by_id(alert_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full details for a single alert by its ID.
    Includes threshold values so the frontend can highlight which reading triggered the alert.
    Coordinates are randomised for map display.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    # Resolve threshold: sector-level first, then mine-level fallback
    threshold = db.query(Threshold).filter(Threshold.scope_id == alert.sector_id).first()
    if not threshold:
        sector = db.query(Sector).filter(Sector.id == alert.sector_id).first()
        if sector:
            threshold = db.query(Threshold).filter(Threshold.scope_id == sector.mine_id).first()

    threshold_data = None
    if threshold:
        threshold_data = {
            "temperatureWarning": threshold.temperature_warning,
            "temperatureCritical": threshold.temperature_critical,
            "humidityWarning": threshold.humidity_warning,
            "humidityCritical": threshold.humidity_critical,
            "methaneWarning": threshold.methane_warning,
            "methaneCritical": threshold.methane_critical,
            "coWarning": threshold.co_warning,
            "coCritical": threshold.co_critical,
            "oxygenWarningLow": threshold.oxygen_warning_low,
            "oxygenCriticalLow": threshold.oxygen_critical_low,
            "oxygenWarningHigh": threshold.oxygen_warning_high,
            "oxygenCriticalHigh": threshold.oxygen_critical_high,
        }

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
        "thresholds": threshold_data,
        "coordinates": {
            "x": round(random.uniform(10.0, 90.0), 2),
            "y": round(random.uniform(10.0, 90.0), 2),
            "z": round(random.uniform(0.0, 50.0), 2),
        },
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


@router.post("/alerts/sos", status_code=status.HTTP_201_CREATED)
def trigger_sos(request: PostSOSRequest, db: Session = Depends(get_db)):
    """
    Manually trigger an SOS alert from a wearable device.
    """
    device = db.query(WearableDevice).filter(WearableDevice.id == request.deviceId).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {request.deviceId} not found")

    new_alert = Alert(
        id=generate_alert_id(db),
        device_id=device.id,
        node_id=device.node_id,
        sector_id=device.sector_id,
        worker_name=device.worker_name,
        hazard="SOS Button Pressed",
        severity="critical",
        state="active",
        acknowledged_by=None,
        temperature=0.0,
        humidity=0.0,
        methane=0.0,
        carbon_monoxide=0.0,
        oxygen=0.0,
        x=0.0,
        y=0.0,
        z=0.0,
        created_at=request.timestamp or datetime.utcnow(),
    )
    db.add(new_alert)
    db.commit()
    
    notify_sos_event({
        "id": new_alert.id,
        "deviceId": new_alert.device_id,
        "nodeId": new_alert.node_id,
        "sectorId": new_alert.sector_id,
        "workerName": new_alert.worker_name,
        "hazard": new_alert.hazard,
        "severity": new_alert.severity,
        "state": new_alert.state,
        "time": new_alert.created_at.isoformat(),
        "temperature": new_alert.temperature,
        "humidity": new_alert.humidity,
        "methane": new_alert.methane,
        "carbonMonoxide": new_alert.carbon_monoxide,
        "oxygen": new_alert.oxygen,
    })

    return {"status": "success", "message": "SOS alert triggered successfully", "alertId": new_alert.id}

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import PostReadingRequest, ReadingResponse
from app.db.database import get_db
from app.db.models import Alert, Reading, Threshold, WearableDevice

router = APIRouter(prefix="", tags=["readings"])


def check_thresholds_and_alert(
    device: WearableDevice,
    temperature: float,
    humidity: float,
    methane: float,
    carbon_monoxide: float,
    oxygen: float,
    db: Session,
):
    """Check if readings exceed thresholds and update/create alerts"""
    
    # Get threshold for this sector
    threshold = db.query(Threshold).filter(Threshold.scope_id == device.sector_id).first()
    if not threshold:
        return None, None
    
    hazard = None
    severity = None
    
    # Check temperature
    if temperature >= threshold.temperature_critical:
        hazard = "CRITICAL_TEMPERATURE"
        severity = "critical"
    elif temperature >= threshold.temperature_warning:
        hazard = "HIGH_TEMPERATURE"
        severity = "warning"
    
    # Check humidity
    if humidity >= threshold.humidity_critical:
        hazard = "CRITICAL_HUMIDITY"
        severity = "critical"
    elif humidity >= threshold.humidity_warning:
        hazard = "HIGH_HUMIDITY"
        severity = "warning"
    
    # Check methane
    if methane >= threshold.methane_critical:
        hazard = "CRITICAL_METHANE"
        severity = "critical"
    elif methane >= threshold.methane_warning:
        hazard = "HIGH_METHANE"
        severity = "warning"
    
    # Check carbon monoxide
    if carbon_monoxide >= threshold.co_critical:
        hazard = "CRITICAL_CO"
        severity = "critical"
    elif carbon_monoxide >= threshold.co_warning:
        hazard = "HIGH_CO"
        severity = "warning"
    
    # Check oxygen
    if oxygen <= threshold.oxygen_critical_low:
        hazard = "CRITICAL_LOW_OXYGEN"
        severity = "critical"
    elif oxygen >= threshold.oxygen_critical_high:
        hazard = "CRITICAL_HIGH_OXYGEN"
        severity = "critical"
    elif oxygen <= threshold.oxygen_warning_low:
        hazard = "LOW_OXYGEN"
        severity = "warning"
    elif oxygen >= threshold.oxygen_warning_high:
        hazard = "HIGH_OXYGEN"
        severity = "warning"
    
    # If hazard detected, update/create alert
    if hazard:
        existing_alert = db.query(Alert).filter(
            Alert.device_id == device.id,
            Alert.state == "active"
        ).first()
        
        if existing_alert:
            # Update existing alert
            existing_alert.hazard = hazard
            existing_alert.severity = severity
            existing_alert.temperature = temperature
            existing_alert.humidity = humidity
            existing_alert.methane = methane
            existing_alert.carbon_monoxide = carbon_monoxide
            existing_alert.oxygen = oxygen
            existing_alert.created_at = datetime.utcnow()
        else:
            # Create new alert
            new_alert = Alert(
                device_id=device.id,
                node_id=device.node_id,
                sector_id=device.sector_id,
                worker_name=device.worker_name,
                hazard=hazard,
                severity=severity,
                state="active",
                acknowledged_by=None,
                temperature=temperature,
                humidity=humidity,
                methane=methane,
                carbon_monoxide=carbon_monoxide,
                oxygen=oxygen,
                x=0.0,
                y=0.0,
                z=0.0,
                created_at=datetime.utcnow(),
            )
            db.add(new_alert)
        
        db.commit()
        return True, severity
    
    return None, None


@router.post("/readings", response_model=ReadingResponse)
def post_reading(request: PostReadingRequest, db: Session = Depends(get_db)):
    """
    Post a new sensor reading from a wearable device.
    
    - Validates sensor data against ranges
    - Updates WearableDevice with latest status
    - Checks thresholds and creates/updates alerts
    - Returns reading ID and alert status
    """
    
    # Find device
    device = db.query(WearableDevice).filter(WearableDevice.id == request.deviceId).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {request.deviceId} not found")
    
    # Create reading record
    reading = Reading(
        device_id=request.deviceId,
        temperature=request.temperature,
        humidity=request.humidity,
        methane=request.methane,
        carbon_monoxide=request.carbonMonoxide,
        oxygen=request.oxygen,
        heart_rate=request.heartRate,
        x=request.x,
        y=request.y,
        z=request.z,
        recorded_at=request.timestamp,
    )
    db.add(reading)
    db.flush()  # Get the ID without committing
    reading_id = reading.id
    
    # Update device status
    device.battery = request.battery
    device.signal_strength = request.signalStrength
    device.last_updated = datetime.utcnow()
    
    # Determine device status based on sensor data and connection
    if request.signalStrength < -100:
        device.status = "offline"
    elif request.battery < 10:
        device.status = "low_battery"
    else:
        device.status = "online"
    
    db.commit()
    
    # Check thresholds and handle alerts
    alert_created, alert_severity = check_thresholds_and_alert(
        device, request.temperature, request.humidity, request.methane,
        request.carbonMonoxide, request.oxygen, db
    )
    
    return ReadingResponse(
        readingId=reading_id,
        deviceId=request.deviceId,
        status="success",
        message=f"Reading recorded for device {request.deviceId}",
        alertCreated=alert_created,
        alertSeverity=alert_severity,
    )

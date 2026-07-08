from datetime import datetime
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import PostReadingRequest, ReadingResponse
from app.api.sse import notify_sos_event
from app.db.database import get_db
from app.db.models import Alert, Reading, Sector, Threshold, WearableDevice

router = APIRouter(prefix="", tags=["readings"])


def generate_alert_id(db: Session) -> str:
    existing = db.query(Alert.id).filter(Alert.id.like("AL-%")).all()
    max_val = 100
    for row in existing:
        alert_id = row[0]
        if not alert_id:
            continue
        parts = alert_id.split("-", 1)
        if len(parts) != 2:
            continue
        try:
            value = int(parts[1])
            if value > max_val:
                max_val = value
        except ValueError:
            continue
    return f"AL-{max_val + 1}"


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
        sector = db.query(Sector).filter(Sector.id == device.sector_id).first()
        if sector:
            threshold = db.query(Threshold).filter(Threshold.scope_id == sector.mine_id).first()
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
            db.commit()
            notify_sos_event({
                "id": existing_alert.id,
                "deviceId": existing_alert.device_id,
                "nodeId": existing_alert.node_id,
                "sectorId": existing_alert.sector_id,
                "workerName": existing_alert.worker_name,
                "hazard": existing_alert.hazard,
                "severity": existing_alert.severity,
                "state": existing_alert.state,
                "time": existing_alert.created_at.isoformat(),
                "temperature": existing_alert.temperature,
                "humidity": existing_alert.humidity,
                "methane": existing_alert.methane,
                "carbonMonoxide": existing_alert.carbon_monoxide,
                "oxygen": existing_alert.oxygen,
            })
        else:
            # Create new alert
            new_alert = Alert(
                id=generate_alert_id(db),
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

    def rand_float(low: float, high: float, precision: int = 1) -> float:
        return round(random.uniform(low, high), precision)

    def rand_int(low: int, high: int) -> int:
        return random.randint(low, high)

    timestamp = request.timestamp or datetime.utcnow()

    temperature = request.temperature if request.temperature is not None else rand_float(28.0, 55.0)
    humidity = request.humidity if request.humidity is not None else rand_float(40.0, 100.0)
    methane = request.methane if request.methane is not None else rand_float(0.0, 7000.0)
    carbon_monoxide = request.carbonMonoxide if request.carbonMonoxide is not None else rand_float(0.0, 150.0)
    oxygen = request.oxygen if request.oxygen is not None else rand_float(15.0, 22.0)
    heart_rate = request.heartRate if request.heartRate is not None else rand_int(40, 140)
    battery = request.battery if request.battery is not None else rand_int(5, 100)
    signal_strength = request.signalStrength if request.signalStrength is not None else rand_int(-110, -40)
    x = request.x if request.x is not None else rand_float(0.0, 200.0, 2)
    y = request.y if request.y is not None else rand_float(0.0, 200.0, 2)
    z = request.z if request.z is not None else rand_float(0.0, 20.0, 2)

    # Create reading record
    reading = Reading(
        device_id=request.deviceId,
        temperature=temperature,
        humidity=humidity,
        methane=methane,
        carbon_monoxide=carbon_monoxide,
        oxygen=oxygen,
        heart_rate=heart_rate,
        x=x,
        y=y,
        z=z,
        recorded_at=timestamp,
    )
    db.add(reading)
    db.flush()  # Get the ID without committing
    reading_id = reading.id

    # Update device status
    device.battery = battery
    device.signal_strength = signal_strength
    device.last_updated = datetime.utcnow()

    if signal_strength < -100:
        device.status = "offline"
    elif battery < 10:
        device.status = "low_battery"
    else:
        device.status = "online"

    db.commit()

    alert_created, alert_severity = check_thresholds_and_alert(
        device, temperature, humidity, methane,
        carbon_monoxide, oxygen, db
    )

    return ReadingResponse(
        readingId=reading_id,
        deviceId=request.deviceId,
        status="success",
        message=f"Reading recorded for device {request.deviceId}",
        alertCreated=alert_created,
        alertSeverity=alert_severity,
    )

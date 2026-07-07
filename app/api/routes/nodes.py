from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas import NodeSummary
from app.db.database import get_db
from app.db.models import Node, WearableDevice, Reading

router = APIRouter(prefix="", tags=["nodes"])


def get_device_summaries(devices, db: Session):
    summaries = []
    for device in devices:
        latest_reading = db.query(Reading).filter(Reading.device_id == device.id).order_by(Reading.recorded_at.desc()).first()
        if latest_reading:
            coords = {"x": latest_reading.x, "y": latest_reading.y, "z": latest_reading.z}
            readings = {
                "temperature": latest_reading.temperature,
                "humidity": latest_reading.humidity,
                "methane": latest_reading.methane,
                "carbonMonoxide": latest_reading.carbon_monoxide,
                "oxygen": latest_reading.oxygen
            }
            heart_rate = latest_reading.heart_rate
        else:
            coords = {"x": 12.0, "y": 8.0, "z": 3.0}
            readings = {"temperature": 28.0, "humidity": 55.0, "methane": 420.0, "carbonMonoxide": 8.0, "oxygen": 20.9}
            heart_rate = 78

        summaries.append({
            "id": device.id,
            "workerName": device.worker_name,
            "workerId": device.worker_id,
            "nodeId": device.node_id,
            "sectorId": device.sector_id,
            "coordinates": coords,
            "readings": readings,
            "heartRate": heart_rate,
            "battery": device.battery,
            "signalStrength": device.signal_strength,
            "lastUpdated": device.last_updated.isoformat(),
            "status": device.status,
            "health": "safe",
        })
    return summaries


@router.get("/nodes", response_model=List[NodeSummary])
def get_nodes(sector_id: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Node)
    if sector_id:
        query = query.filter(Node.sector_id == sector_id)
    nodes = query.all()
    response = []
    for node in nodes:
        devices = db.query(WearableDevice).filter(WearableDevice.node_id == node.id).all()
        response.append(
            {
                "id": node.id,
                "name": node.name,
                "sectorId": node.sector_id,
                "status": node.status,
                "connectedDevices": len(devices),
                "signalStrength": node.signal_strength,
                "battery": node.battery,
                "lastUpdated": node.last_updated.isoformat(),
                "devices": get_device_summaries(devices, db),
            }
        )
    return response


@router.get("/nodes/{node_id}", response_model=NodeSummary)
def get_node(node_id: str, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    devices = db.query(WearableDevice).filter(WearableDevice.node_id == node.id).all()
    return {
        "id": node.id,
        "name": node.name,
        "sectorId": node.sector_id,
        "status": node.status,
        "connectedDevices": len(devices),
        "signalStrength": node.signal_strength,
        "battery": node.battery,
        "lastUpdated": node.last_updated.isoformat(),
        "devices": get_device_summaries(devices, db),
    }

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas import NodeSummary
from app.db.database import get_db
from app.db.models import Node, WearableDevice

router = APIRouter(prefix="", tags=["nodes"])


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
                "devices": [
                    {
                        "id": device.id,
                        "workerName": device.worker_name,
                        "workerId": device.worker_id,
                        "nodeId": device.node_id,
                        "sectorId": device.sector_id,
                        "coordinates": {"x": 12, "y": 8, "z": 3},
                        "readings": {"temperature": 28, "humidity": 55, "methane": 420, "carbonMonoxide": 8, "oxygen": 20.9},
                        "heartRate": 78,
                        "battery": device.battery,
                        "signalStrength": device.signal_strength,
                        "lastUpdated": device.last_updated.isoformat(),
                        "status": device.status,
                        "health": "safe",
                    }
                    for device in devices
                ],
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
        "devices": [
            {
                "id": device.id,
                "workerName": device.worker_name,
                "workerId": device.worker_id,
                "nodeId": device.node_id,
                "sectorId": device.sector_id,
                "coordinates": {"x": 12, "y": 8, "z": 3},
                "readings": {"temperature": 28, "humidity": 55, "methane": 420, "carbonMonoxide": 8, "oxygen": 20.9},
                "heartRate": 78,
                "battery": device.battery,
                "signalStrength": device.signal_strength,
                "lastUpdated": device.last_updated.isoformat(),
                "status": device.status,
                "health": "safe",
            }
            for device in devices
        ],
    }

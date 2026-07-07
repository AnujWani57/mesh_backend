# Frontend Live Data Integration Guide

## Overview

This document describes how to implement **live sensor data visualization** in the MineMesh frontend using:
1. **Polling** - Frontend regularly fetches latest data from backend
2. **Posting** - Simulator sends new readings to backend API

---

## Architecture

```
Simulator (CSV Files)
        ↓ POST /readings
    FastAPI Backend
    ├─ Store Reading in DB
    ├─ Update WearableDevice
    ├─ Check Thresholds → Create/Update Alert
        ↓ Poll
    Frontend
    ├─ GET /nodes/{node_id}
    ├─ Display Live Gauges
    ├─ Show Alerts
    └─ Update Charts
```

---

## 1. Simulator → Backend: POST New Readings

### Endpoint
```
POST http://127.0.0.1:8002/readings
```

### Request Format

**Content-Type:** `application/json`

**Body (one reading at a time from one device):**

```json
{
  "deviceId": "WD-101",
  "temperature": 28.5,
  "humidity": 62,
  "methane": 850,
  "carbonMonoxide": 12,
  "oxygen": 20.5,
  "heartRate": 78,
  "battery": 85,
  "signalStrength": -65,
  "x": 10.5,
  "y": 20.3,
  "z": 5.1,
  "timestamp": "2026-07-07T14:30:00Z"
}
```

### Field Specifications & Validation

| Field | Type | Range | Required | Description |
|-------|------|-------|----------|-------------|
| `deviceId` | string | - | ✓ | Wearable ID (e.g., WD-101, WD-102) |
| `temperature` | float | -50 to 60°C | ✓ | Device/body temperature |
| `humidity` | float | 0-100% | ✓ | Environmental humidity |
| `methane` | float | ≥ 0 ppm | ✓ | Methane concentration |
| `carbonMonoxide` | float | ≥ 0 ppm | ✓ | CO concentration |
| `oxygen` | float | 0-100% | ✓ | Oxygen level |
| `heartRate` | int | 40-200 bpm | ✓ | Worker heart rate |
| `battery` | int | 0-100% | ✓ | Device battery level |
| `signalStrength` | int | -120 to -30 dBm | ✓ | WiFi/signal strength |
| `x` | float | any | ✓ | X coordinate |
| `y` | float | any | ✓ | Y coordinate |
| `z` | float | any | ✓ | Z coordinate |
| `timestamp` | string | ISO format | ✓ | Reading timestamp (e.g., 2026-07-07T14:30:00Z) |

### Response (Success)

```json
{
  "readingId": "reading-12345",
  "deviceId": "WD-101",
  "status": "success",
  "message": "Reading recorded for device WD-101",
  "alertCreated": true,
  "alertSeverity": "warning"
}
```

**Response Fields:**
- `readingId`: Unique ID for this reading (store if needed)
- `alertCreated`: `true` if thresholds were exceeded and alert created/updated
- `alertSeverity`: `"warning"` or `"critical"` if alert created

### Response (Error Examples)

**Invalid device:**
```json
{
  "detail": "Device WD-999 not found"
}
```
Status: `404`

**Validation error (e.g., temperature > 60°C):**
```json
{
  "detail": [
    {
      "type": "value_error.number.not_le",
      "loc": ["body", "temperature"],
      "msg": "ensure this value is less than or equal to 60"
    }
  ]
}
```
Status: `422`

### Example: Simulate 3 Devices

```bash
# Device WD-101 - Normal conditions
curl -X POST "http://127.0.0.1:8002/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "WD-101",
    "temperature": 28.5,
    "humidity": 62,
    "methane": 850,
    "carbonMonoxide": 12,
    "oxygen": 20.5,
    "heartRate": 78,
    "battery": 85,
    "signalStrength": -65,
    "x": 10.5,
    "y": 20.3,
    "z": 5.1,
    "timestamp": "2026-07-07T14:35:00Z"
  }'

# Device WD-102 - High methane (alert will be created)
curl -X POST "http://127.0.0.1:8002/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "WD-102",
    "temperature": 29.2,
    "humidity": 68,
    "methane": 1200,
    "carbonMonoxide": 15,
    "oxygen": 19.8,
    "heartRate": 85,
    "battery": 72,
    "signalStrength": -72,
    "x": 15.2,
    "y": 25.1,
    "z": 4.8,
    "timestamp": "2026-07-07T14:35:00Z"
  }'

# Device WD-103 - Low oxygen (critical alert)
curl -X POST "http://127.0.0.1:8002/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "WD-103",
    "temperature": 27.8,
    "humidity": 55,
    "methane": 600,
    "carbonMonoxide": 8,
    "oxygen": 16.5,
    "heartRate": 82,
    "battery": 90,
    "signalStrength": -58,
    "x": 12.0,
    "y": 22.5,
    "z": 6.2,
    "timestamp": "2026-07-07T14:35:00Z"
  }'
```

---

## 2. Frontend: Polling for Live Data

### Polling Approach

Frontend fetches latest wearable device data at **regular intervals** (recommended: **2-5 seconds**).

### Endpoint
```
GET http://127.0.0.1:8002/nodes/{node_id}
```

### Query Parameter

| Param | Type | Example | Purpose |
|-------|------|---------|---------|
| `node_id` | string (path) | `node-1` | Get all devices in this node |

### Response Format

```json
[
  {
    "id": "node-1",
    "name": "Node-Sector1-A",
    "sectorId": "sector-1",
    "status": "online",
    "connectedDevices": 3,
    "signalStrength": "strong",
    "battery": 85,
    "lastUpdated": "2026-07-07T14:35:22Z",
    "devices": [
      {
        "id": "WD-101",
        "workerName": "Rajesh Kumar",
        "workerId": "EMP-001",
        "nodeId": "node-1",
        "sectorId": "sector-1",
        "coordinates": {
          "x": 10.5,
          "y": 20.3,
          "z": 5.1
        },
        "readings": {
          "temperature": 28.5,
          "humidity": 62,
          "methane": 850,
          "carbonMonoxide": 12,
          "oxygen": 20.5
        },
        "heartRate": 78,
        "battery": 85,
        "signalStrength": -65,
        "lastUpdated": "2026-07-07T14:35:22Z",
        "status": "online",
        "health": "good"
      },
      {
        "id": "WD-102",
        "workerName": "Priya Singh",
        "workerId": "EMP-002",
        "nodeId": "node-1",
        "sectorId": "sector-1",
        "coordinates": {
          "x": 15.2,
          "y": 25.1,
          "z": 4.8
        },
        "readings": {
          "temperature": 29.2,
          "humidity": 68,
          "methane": 1200,
          "carbonMonoxide": 15,
          "oxygen": 19.8
        },
        "heartRate": 85,
        "battery": 72,
        "signalStrength": -72,
        "lastUpdated": "2026-07-07T14:35:20Z",
        "status": "online",
        "health": "warning"
      }
    ]
  }
]
```

### Frontend Implementation: Polling Loop

**JavaScript/React Example:**

```javascript
import { useState, useEffect } from 'react';

function LiveSensorDashboard({ nodeId }) {
  const [liveData, setLiveData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch on mount
    fetchLatestData();

    // Poll every 3 seconds
    const interval = setInterval(fetchLatestData, 3000);
    return () => clearInterval(interval);
  }, [nodeId]);

  const fetchLatestData = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:8002/nodes/${nodeId}`
      );
      const data = await response.json();
      setLiveData(data[0]?.devices || []);
    } catch (error) {
      console.error('Polling error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Live Worker Monitoring</h2>
      {liveData?.map(device => (
        <div key={device.id} className="device-card">
          <h3>{device.workerName}</h3>
          
          {/* Temperature Gauge */}
          <div>
            <label>Temperature</label>
            <gauge value={device.readings.temperature} max={60} />
            <span>{device.readings.temperature}°C</span>
          </div>

          {/* Methane Level */}
          <div>
            <label>Methane</label>
            <gauge value={device.readings.methane} max={2000} />
            <span>{device.readings.methane} ppm</span>
          </div>

          {/* Oxygen Level */}
          <div>
            <label>Oxygen</label>
            <gauge value={device.readings.oxygen} max={100} />
            <span>{device.readings.oxygen}%</span>
          </div>

          {/* Heart Rate */}
          <div>
            <label>Heart Rate</label>
            <span>{device.heartRate} bpm</span>
          </div>

          {/* Status */}
          <div>
            <label>Device Status</label>
            <span style={{ color: device.status === 'online' ? 'green' : 'red' }}>
              {device.status.toUpperCase()}
            </span>
          </div>

          {/* Health Indicator */}
          <div>
            <label>Health</label>
            <span style={{ 
              color: device.health === 'good' ? 'green' : 
                     device.health === 'warning' ? 'orange' : 'red' 
            }}>
              {device.health.toUpperCase()}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default LiveSensorDashboard;
```

---

## 3. Alerts: Automatic Threshold Detection

### How Alerts Work

1. **POST /readings receives data**
2. **Backend checks thresholds against Threshold table**
3. **If reading exceeds threshold:**
   - Existing active alert for that device is **updated** (timestamp reset, data refreshed)
   - OR new alert is created if none exists
4. **Frontend polls and sees alert in response**

### Alert Status Values

| Status | Meaning |
|--------|---------|
| `active` | Alert is current and unacknowledged |
| `resolved` | Alert acknowledged by supervisor |

### Alert Severity Levels

| Severity | Trigger | Action |
|----------|---------|--------|
| `warning` | Reading exceeds warning threshold | Yellow badge, notification |
| `critical` | Reading exceeds critical threshold | Red badge, urgent notification, sound |

### Example: Fetch Active Alerts

```
GET http://127.0.0.1:8002/alerts?sectorId=sector-1
```

Response:
```json
[
  {
    "id": "alert-5678",
    "deviceId": "WD-102",
    "workerName": "Priya Singh",
    "nodeId": "node-1",
    "sectorId": "sector-1",
    "hazard": "HIGH_METHANE",
    "severity": "warning",
    "time": "2026-07-07T14:35:20Z",
    "state": "active",
    "acknowledgedBy": null,
    "readings": {
      "temperature": 29.2,
      "humidity": 68,
      "methane": 1200,
      "carbonMonoxide": 15,
      "oxygen": 19.8
    },
    "coordinates": {
      "x": 15.2,
      "y": 25.1,
      "z": 4.8
    }
  }
]
```

---

## 4. Threshold Configuration

### Current Thresholds (from seed data)

```
Scope: sector-1

Temperature:
  - Warning: 35°C
  - Critical: 45°C

Humidity:
  - Warning: 80%
  - Critical: 90%

Methane:
  - Warning: 1000 ppm
  - Critical: 1500 ppm

Carbon Monoxide:
  - Warning: 20 ppm
  - Critical: 35 ppm

Oxygen:
  - Warning Low: 18%
  - Critical Low: 16%
  - Warning High: 22%
  - Critical High: 23%
```

---

## 5. Frontend Integration Checklist

### Phase 1: Setup (First Time)
- [ ] Identify node IDs in your sector (from GET /sectors endpoint)
- [ ] Extract wearable device IDs (WD-101, WD-102, etc.)
- [ ] Set up polling interval (recommended: 3 seconds)
- [ ] Design gauge/chart components for sensor readings

### Phase 2: Polling Implementation
- [ ] Create fetch function: `GET /nodes/{nodeId}`
- [ ] Set interval: `setInterval(fetchLatestData, 3000)`
- [ ] Parse response and extract device readings
- [ ] Bind data to gauge/chart UI components
- [ ] Handle errors gracefully (offline fallback)

### Phase 3: Alert Handling
- [ ] Fetch alerts: `GET /alerts?sectorId=sectorId`
- [ ] Display critical alerts prominently (red)
- [ ] Display warning alerts moderately (yellow)
- [ ] Poll alerts on same interval as devices

### Phase 4: Testing
- [ ] Start simulator sending POST /readings
- [ ] Verify data appears in frontend within 3-5 seconds
- [ ] Verify alerts trigger when thresholds exceeded
- [ ] Test alert acknowledgment: `POST /alerts/{alertId}/acknowledge`

---

## 6. Performance Tips

1. **Polling Interval:** 
   - 2-3 seconds: Responsive, smooth animations
   - 5-10 seconds: Less network load, acceptable latency
   - Adjust based on UI needs

2. **Data Caching:**
   - Cache last known values for 1-2 seconds
   - Prevents UI flicker from duplicate requests

3. **Batch Rendering:**
   - Update multiple gauges in single render cycle
   - Use React keys to avoid re-renders

4. **Connection Handling:**
   - Show "Offline" badge if no data in 10 seconds
   - Retry polling on network error
   - Exponential backoff after 3 consecutive failures

---

## 7. Example Supervisor Dashboard Flow

```
1. Load supervisor home:
   GET /supervisor/home?sectorId=sector-1

2. Extract node IDs from response

3. For each node:
   - Start polling: GET /nodes/{node_id} every 3 sec
   - Poll alerts: GET /alerts?sectorId=sector-1 every 3 sec

4. Display:
   - Live gauges for each wearable device
   - Active alerts table
   - Worker location map (using x, y, z coordinates)
   - Device status indicators

5. Handle user action:
   - Acknowledge alert: POST /alerts/{alert_id}/acknowledge
   - Fetches updated alert list
```

---

## 8. Simulator Configuration

### CSV Format Expected

```
device_id,temperature,humidity,methane,carbon_monoxide,oxygen,heart_rate,battery,signal_strength,x,y,z,timestamp
WD-101,28.5,62,850,12,20.5,78,85,-65,10.5,20.3,5.1,2026-07-07T14:35:00Z
WD-102,29.2,68,1200,15,19.8,85,72,-72,15.2,25.1,4.8,2026-07-07T14:35:01Z
WD-103,27.8,55,600,8,16.5,82,90,-58,12.0,22.5,6.2,2026-07-07T14:35:02Z
```

### Simulator Pseudo-Code

```python
import csv
import requests
import time

with open('wearables_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        payload = {
            "deviceId": row['device_id'],
            "temperature": float(row['temperature']),
            "humidity": float(row['humidity']),
            "methane": float(row['methane']),
            "carbonMonoxide": float(row['carbon_monoxide']),
            "oxygen": float(row['oxygen']),
            "heartRate": int(row['heart_rate']),
            "battery": int(row['battery']),
            "signalStrength": int(row['signal_strength']),
            "x": float(row['x']),
            "y": float(row['y']),
            "z": float(row['z']),
            "timestamp": row['timestamp']
        }
        
        response = requests.post(
            'http://127.0.0.1:8002/readings',
            json=payload
        )
        print(f"Posted reading for {row['device_id']}: {response.status_code}")
        
        # Pause between sends (simulate real-time data)
        time.sleep(2)
```

---

## Questions?

- Backend API docs: http://127.0.0.1:8002/docs
- ReDoc: http://127.0.0.1:8002/redoc
- Contact: Backend team for threshold tuning

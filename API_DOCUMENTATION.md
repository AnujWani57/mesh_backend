# MineMesh API Documentation

This document is intended for the frontend team. It describes the backend endpoints, request and response payloads, and the shared data shapes used by the UI.

## Base URLs
- Local development: http://127.0.0.1:8002
- Swagger UI: http://127.0.0.1:8002/docs
- ReDoc: http://127.0.0.1:8002/redoc

## Content Type
- All requests and responses use JSON.
- Authentication uses a Bearer token when available.

## Shared Shapes

### SensorReadings
```json
{
  "temperature": 29,
  "humidity": 58,
  "methane": 810,
  "carbonMonoxide": 10,
  "oxygen": 20.7
}
```

### Coordinates
```json
{
  "x": 12,
  "y": 8,
  "z": 3
}
```

## Authentication

### POST /auth/login
Login an admin or supervisor.

Request body:
```json
{
  "email": "admin@minemesh.io",
  "password": "admin123",
  "role": "admin"
}
```

Successful response: 200
```json
{
  "token": "jwt-token",
  "user": {
    "id": "u-admin-1",
    "role": "admin",
    "name": "Arjun Mehta",
    "employeeId": "EMP-A001",
    "gender": "Male",
    "phone": "+91 98200 11223",
    "email": "admin@minemesh.io",
    "mineName": "Jharia Coalfield",
    "companyName": "BharatMinerals Ltd.",
    "lastLogin": "2026-07-07T10:00:00Z",
    "sectorId": null,
    "sectorName": null
  }
}
```

### POST /auth/signup/admin
Create an admin account.

Request body:
```json
{
  "name": "Arjun Mehta",
  "employeeId": "EMP-A002",
  "gender": "Male",
  "phone": "+91 98765 43210",
  "email": "newadmin@minemesh.io",
  "password": "password123",
  "mineName": "Jharia Coalfield",
  "companyName": "BharatMinerals Ltd."
}
```

Successful response: 201
```json
{
  "token": "jwt-token",
  "user": {
    "id": "generated-id",
    "role": "admin",
    "name": "Arjun Mehta",
    "employeeId": "EMP-A002",
    "gender": "Male",
    "phone": "+91 98765 43210",
    "email": "newadmin@minemesh.io",
    "mineName": "Jharia Coalfield",
    "companyName": "BharatMinerals Ltd.",
    "lastLogin": null,
    "sectorId": null,
    "sectorName": null
  }
}
```

### POST /auth/signup/supervisor
Create a supervisor account.

Request body:
```json
{
  "name": "Rahul Sharma",
  "employeeId": "EMP-S104",
  "sectorId": "sector-1",
  "gender": "Male",
  "phone": "+91 98765 00000",
  "email": "rahul2@minemesh.io",
  "password": "password123"
}
```

Successful response: 201
```json
{
  "token": "jwt-token",
  "user": {
    "id": "generated-id",
    "role": "supervisor",
    "name": "Rahul Sharma",
    "employeeId": "EMP-S104",
    "gender": "Male",
    "phone": "+91 98765 00000",
    "email": "rahul2@minemesh.io",
    "mineName": "Jharia Coalfield",
    "companyName": null,
    "lastLogin": null,
    "sectorId": "sector-1",
    "sectorName": "Sector 1"
  }
}
```

## Admin

### GET /admin/dashboard
Returns dashboard metrics for the admin panel.

Successful response: 200
```json
{
  "totalSectors": 3,
  "totalNodes": 6,
  "totalDevices": 12,
  "activeDevices": 10,
  "inactiveDevices": 2,
  "activeAlerts": 3,
  "workersInside": 10,
  "averageReadings": {
    "temperature": 31,
    "humidity": 61,
    "methane": 1180,
    "carbonMonoxide": 17,
    "oxygen": 20.3
  },
  "trends": [
    {
      "time": "09:00",
      "temperature": 31,
      "humidity": 61,
      "methane": 1180,
      "carbonMonoxide": 17,
      "oxygen": 20.3
    }
  ],
  "health": {
    "safe": 0,
    "warning": 2,
    "critical": 1
  },
  "recentAlerts": []
}
```

### GET /sectors
Returns all sectors.

Successful response: 200
```json
[
  {
    "id": "sector-1",
    "name": "Sector 1",
    "supervisor": {
      "id": "u-sup-1",
      "name": "Rahul Sharma",
      "phone": "+91 90000 11111",
      "email": "rahul@minemesh.io",
      "employeeId": "EMP-S101"
    },
    "activeNodes": 2,
    "inactiveNodes": 0,
    "averageReadings": {
      "temperature": 29,
      "humidity": 58,
      "methane": 810,
      "carbonMonoxide": 10,
      "oxygen": 20.7
    },
    "status": "warning"
  }
]
```

### GET /sectors/{sector_id}
Returns a single sector by ID.

### GET /supervisors
Returns all supervisors.

Successful response: 200
```json
[
  {
    "id": "u-sup-1",
    "name": "Rahul Sharma",
    "employeeId": "EMP-S101",
    "gender": "Male",
    "phone": "+91 90000 11111",
    "email": "rahul@minemesh.io",
    "sectorId": "sector-1",
    "sectorName": "Sector 1",
    "experienceYears": 8,
    "status": "online",
    "nodeCount": 2
  }
]
```

## Nodes and Devices

### GET /nodes
Returns all nodes. Optional query parameter: sectorId.

Example:
- /nodes
- /nodes?sectorId=sector-1

Successful response: 200
```json
[
  {
    "id": "node-1-1",
    "name": "Node 1",
    "sectorId": "sector-1",
    "status": "online",
    "connectedDevices": 2,
    "signalStrength": "Excellent",
    "battery": 92,
    "lastUpdated": "2026-07-07T10:00:00Z",
    "devices": [
      {
        "id": "WD-101",
        "workerName": "Ramesh Yadav",
        "workerId": "W-1001",
        "nodeId": "node-1-1",
        "sectorId": "sector-1",
        "coordinates": {
          "x": 12,
          "y": 8,
          "z": 3
        },
        "readings": {
          "temperature": 28,
          "humidity": 55,
          "methane": 420,
          "carbonMonoxide": 8,
          "oxygen": 20.9
        },
        "heartRate": 78,
        "battery": 88,
        "signalStrength": -62,
        "lastUpdated": "2026-07-07T10:00:00Z",
        "status": "online",
        "health": "safe"
      }
    ]
  }
]
```

### GET /nodes/{node_id}
Returns a single node with its devices.

## Alerts

### GET /alerts
Returns alerts. Optional query parameter: sectorId.

Successful response: 200
```json
[
  {
    "id": "AL-102",
    "deviceId": "WD-203",
    "workerName": "Rahul Meena",
    "nodeId": "node-2-1",
    "sectorId": "sector-2",
    "hazard": "Methane High",
    "severity": "critical",
    "time": "2026-07-07T09:45:00Z",
    "state": "active",
    "acknowledgedBy": null,
    "readings": {
      "temperature": 39,
      "humidity": 74,
      "methane": 5200,
      "carbonMonoxide": 55,
      "oxygen": 17.8
    },
    "coordinates": {
      "x": 20,
      "y": 15,
      "z": 4
    }
  }
]
```

### POST /alerts/{alert_id}/acknowledge
Acknowledge an active alert.

Request body:
```json
{
  "by": "Rahul Sharma"
}
```

Successful response: 200
```json
{
  "id": "AL-102",
  "deviceId": "WD-203",
  "workerName": "Rahul Meena",
  "nodeId": "node-2-1",
  "sectorId": "sector-2",
  "hazard": "Methane High",
  "severity": "critical",
  "time": "2026-07-07T09:45:00Z",
  "state": "resolved",
  "acknowledgedBy": "Rahul Sharma",
  "readings": {
    "temperature": 39,
    "humidity": 74,
    "methane": 5200,
    "carbonMonoxide": 55,
    "oxygen": 17.8
  },
  "coordinates": {
    "x": 20,
    "y": 15,
    "z": 4
  }
}
```

## Supervisor

### GET /supervisor/home
Returns the supervisor home summary for a sector.

Query parameter: sectorId

Successful response: 200
```json
{
  "sectorId": "sector-1",
  "sectorName": "Sector 1",
  "averageReadings": {
    "temperature": 29,
    "humidity": 58,
    "methane": 810,
    "carbonMonoxide": 10,
    "oxygen": 20.7
  },
  "status": "warning",
  "trends": [
    {
      "time": "09:00",
      "temperature": 29,
      "humidity": 58,
      "methane": 810,
      "carbonMonoxide": 10,
      "oxygen": 20.7
    }
  ],
  "nodes": [
    {
      "id": "node-1-1",
      "name": "Node 1",
      "status": "online"
    }
  ],
  "totalWorkers": 4,
  "devicesOnline": 4,
  "sosCount": 1,
  "recentAlerts": []
}
```

## Notes for Frontend Team
- Use the Swagger docs for live examples while the backend is running.
- The backend currently uses seeded demo data and is ready to be connected to your real database.
- If you need more fields or alternate response names, I can adjust the API contract quickly.

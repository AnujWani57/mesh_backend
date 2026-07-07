from typing import List, Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    x: float
    y: float
    z: float


class SensorReadings(BaseModel):
    temperature: float
    humidity: float
    methane: float
    carbonMonoxide: float
    oxygen: float


class UserSummary(BaseModel):
    id: str
    role: str
    name: str
    employeeId: str
    gender: str
    phone: str
    email: str
    mineName: str
    companyName: Optional[str] = None
    lastLogin: Optional[str] = None
    sectorId: Optional[str] = None
    sectorName: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str
    role: str


class SignupAdminRequest(BaseModel):
    name: str
    employeeId: str
    gender: str
    phone: str
    email: str
    password: str
    mineName: str
    companyName: str


class SignupSupervisorRequest(BaseModel):
    name: str
    employeeId: str
    sectorId: str
    gender: str
    phone: str
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: UserSummary


class SectorSupervisor(BaseModel):
    id: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    employeeId: Optional[str]


class SectorSummary(BaseModel):
    id: str
    name: str
    supervisor: SectorSupervisor
    activeNodes: int
    inactiveNodes: int
    averageReadings: SensorReadings
    status: str


class SupervisorSummary(BaseModel):
    id: str
    name: str
    employeeId: str
    gender: str
    phone: str
    email: str
    sectorId: Optional[str]
    sectorName: Optional[str]
    experienceYears: Optional[int]
    status: str
    nodeCount: int


class DeviceSummary(BaseModel):
    id: str
    workerName: str
    workerId: str
    nodeId: str
    sectorId: str
    coordinates: Coordinates
    readings: SensorReadings
    heartRate: int
    battery: int
    signalStrength: int
    lastUpdated: str
    status: str
    health: str


class NodeSummary(BaseModel):
    id: str
    name: str
    sectorId: str
    status: str
    connectedDevices: int
    signalStrength: str
    battery: int
    lastUpdated: str
    devices: List[DeviceSummary]


class AlertSummary(BaseModel):
    id: str
    deviceId: str
    workerName: str
    nodeId: str
    sectorId: str
    hazard: str
    severity: str
    time: str
    state: str
    acknowledgedBy: Optional[str]
    readings: SensorReadings
    coordinates: Coordinates


class AdminDashboardResponse(BaseModel):
    totalSectors: int
    totalNodes: int
    totalDevices: int
    activeDevices: int
    inactiveDevices: int
    activeAlerts: int
    workersInside: int
    averageReadings: SensorReadings
    trends: List[dict]
    health: dict
    recentAlerts: List[AlertSummary]


class SupervisorHomeResponse(BaseModel):
    sectorId: str
    sectorName: Optional[str]
    averageReadings: SensorReadings
    status: str
    trends: List[dict]
    nodes: List[dict]
    totalWorkers: int
    devicesOnline: int
    sosCount: int
    recentAlerts: List[AlertSummary]


class PostReadingRequest(BaseModel):
    deviceId: str = Field(..., description="Wearable device ID")
    temperature: float = Field(..., ge=-50, le=60, description="Temperature in Celsius (-50 to 60)")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage (0-100)")
    methane: float = Field(..., ge=0, description="Methane level in ppm")
    carbonMonoxide: float = Field(..., ge=0, description="CO level in ppm")
    oxygen: float = Field(..., ge=0, le=100, description="Oxygen level percentage")
    heartRate: int = Field(..., ge=40, le=200, description="Heart rate in bpm (40-200)")
    battery: int = Field(..., ge=0, le=100, description="Battery percentage (0-100)")
    signalStrength: int = Field(..., ge=-120, le=-30, description="Signal strength in dBm")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    timestamp: str = Field(..., description="ISO format timestamp")


class ReadingResponse(BaseModel):
    readingId: str
    deviceId: str
    status: str
    message: str
    alertCreated: Optional[bool] = None
    alertSeverity: Optional[str] = None

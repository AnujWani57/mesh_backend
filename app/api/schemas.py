from datetime import datetime
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


class AdminStatsResponse(BaseModel):
    totalSectors: int
    totalNodes: int
    totalDevices: int
    activeDevices: int
    inactiveDevices: int
    activeAlerts: int
    workersInside: int


class TrendPoint(BaseModel):
    time: str
    temperature: float
    humidity: float
    methane: float
    carbonMonoxide: float
    oxygen: float


class EnvironmentHealth(BaseModel):
    safe: int
    warning: int
    critical: int


class AdminEnvironmentResponse(BaseModel):
    averageReadings: SensorReadings
    trends: List[TrendPoint]
    health: EnvironmentHealth


class SupervisorStatsResponse(BaseModel):
    sectorId: str
    sectorName: Optional[str]
    status: str
    totalWorkers: int
    devicesOnline: int
    sosCount: int
    activeSosCount: int


class SupervisorEnvironmentResponse(BaseModel):
    averageReadings: SensorReadings
    trends: List[TrendPoint]


class NodeStatusItem(BaseModel):
    id: str
    name: str
    status: str


class AlertListItem(BaseModel):
    id: str
    deviceId: str
    nodeId: str
    sectorId: str
    time: str
    hazard: str
    severity: str
    state: str
    acknowledgedBy: Optional[str] = None
    readingValue: Optional[float] = None
    readingUnit: Optional[str] = None


class PaginationMeta(BaseModel):
    page: int
    limit: int
    totalCount: int
    totalPages: int


class AlertListResponse(BaseModel):
    data: List[AlertListItem]
    meta: PaginationMeta


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


class PostSOSRequest(BaseModel):
    deviceId: str = Field(..., description="Wearable device ID triggering the SOS")
    timestamp: Optional[datetime] = Field(None, description="ISO format timestamp")


class PostReadingRequest(BaseModel):
    deviceId: str = Field(..., description="Wearable device ID")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    methane: Optional[float] = Field(None, description="Methane level in ppm")
    carbonMonoxide: Optional[float] = Field(None, description="CO level in ppm")
    oxygen: Optional[float] = Field(None, description="Oxygen level percentage")
    heartRate: Optional[int] = Field(None, description="Heart rate in bpm")
    battery: Optional[int] = Field(None, description="Battery percentage")
    signalStrength: Optional[int] = Field(None, description="Signal strength in dBm")
    x: Optional[float] = Field(None, description="X coordinate")
    y: Optional[float] = Field(None, description="Y coordinate")
    z: Optional[float] = Field(None, description="Z coordinate")
    timestamp: Optional[datetime] = Field(None, description="ISO format timestamp")


class ReadingResponse(BaseModel):
    readingId: str
    deviceId: str
    status: str
    message: str
    alertCreated: Optional[bool] = None
    alertSeverity: Optional[str] = None

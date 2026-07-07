from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Alert, Mine, Node, Reading, Sector, Threshold, User, WearableDevice


def seed_database():
    db: Session = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        mine = Mine(id="mine-1", name="Jharia Coalfield", company_name="BharatMinerals Ltd.")
        db.add(mine)
        db.flush()

        admin = User(
            id="u-admin-1",
            role="admin",
            name="Arjun Mehta",
            employee_id="EMP-A001",
            gender="Male",
            phone="+91 98200 11223",
            email="admin@minemesh.io",
            password_hash="admin123",
            mine_id=mine.id,
            experience_years=10,
            last_login=datetime.utcnow(),
        )
        db.add(admin)

        sectors = [
            Sector(id="sector-1", mine_id=mine.id, name="Sector 1", supervisor_id="u-sup-1", status="warning"),
            Sector(id="sector-2", mine_id=mine.id, name="Sector 2", supervisor_id="u-sup-2", status="critical"),
            Sector(id="sector-3", mine_id=mine.id, name="Sector 3", supervisor_id="u-sup-3", status="safe"),
        ]
        db.add_all(sectors)
        db.flush()

        supervisors = [
            User(id="u-sup-1", role="supervisor", name="Rahul Sharma", employee_id="EMP-S101", gender="Male", phone="+91 90000 11111", email="rahul@minemesh.io", password_hash="super123", mine_id=mine.id, sector_id="sector-1", experience_years=8, last_login=datetime.utcnow() - timedelta(days=1)),
            User(id="u-sup-2", role="supervisor", name="Neha Gupta", employee_id="EMP-S102", gender="Female", phone="+91 90000 22222", email="neha@minemesh.io", password_hash="super123", mine_id=mine.id, sector_id="sector-2", experience_years=6, last_login=datetime.utcnow() - timedelta(days=2)),
            User(id="u-sup-3", role="supervisor", name="Aman Verma", employee_id="EMP-S103", gender="Male", phone="+91 90000 33333", email="aman@minemesh.io", password_hash="super123", mine_id=mine.id, sector_id="sector-3", experience_years=5, last_login=datetime.utcnow() - timedelta(days=3)),
        ]
        db.add_all(supervisors)

        nodes = [
            Node(id="node-1-1", sector_id="sector-1", name="Node 1", status="online", signal_strength="Excellent", battery=92, last_updated=datetime.utcnow()),
            Node(id="node-1-2", sector_id="sector-1", name="Node 2", status="online", signal_strength="Good", battery=81, last_updated=datetime.utcnow()),
            Node(id="node-2-1", sector_id="sector-2", name="Node 1", status="offline", signal_strength="Weak", battery=27, last_updated=datetime.utcnow() - timedelta(hours=2)),
            Node(id="node-2-2", sector_id="sector-2", name="Node 2", status="online", signal_strength="Excellent", battery=88, last_updated=datetime.utcnow()),
            Node(id="node-3-1", sector_id="sector-3", name="Node 1", status="online", signal_strength="Excellent", battery=95, last_updated=datetime.utcnow()),
            Node(id="node-3-2", sector_id="sector-3", name="Node 2", status="online", signal_strength="Good", battery=90, last_updated=datetime.utcnow()),
        ]
        db.add_all(nodes)
        db.flush()

        devices = [
            WearableDevice(id="WD-101", node_id="node-1-1", sector_id="sector-1", worker_name="Ramesh Yadav", worker_id="W-1001", battery=88, signal_strength=-62, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-102", node_id="node-1-1", sector_id="sector-1", worker_name="Suresh Kumar", worker_id="W-1002", battery=84, signal_strength=-65, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-103", node_id="node-1-2", sector_id="sector-1", worker_name="Kiran Rao", worker_id="W-1003", battery=80, signal_strength=-56, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-104", node_id="node-1-2", sector_id="sector-1", worker_name="Mohan Das", worker_id="W-1004", battery=76, signal_strength=-69, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-201", node_id="node-2-1", sector_id="sector-2", worker_name="Rahul Meena", worker_id="W-2001", battery=33, signal_strength=-87, status="offline", last_updated=datetime.utcnow() - timedelta(hours=3)),
            WearableDevice(id="WD-202", node_id="node-2-1", sector_id="sector-2", worker_name="Pooja Singh", worker_id="W-2002", battery=41, signal_strength=-82, status="offline", last_updated=datetime.utcnow() - timedelta(hours=3)),
            WearableDevice(id="WD-203", node_id="node-2-2", sector_id="sector-2", worker_name="Sameer Khan", worker_id="W-2003", battery=90, signal_strength=-58, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-204", node_id="node-2-2", sector_id="sector-2", worker_name="Anita Joshi", worker_id="W-2004", battery=87, signal_strength=-61, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-301", node_id="node-3-1", sector_id="sector-3", worker_name="Nilesh Patel", worker_id="W-3001", battery=95, signal_strength=-54, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-302", node_id="node-3-1", sector_id="sector-3", worker_name="Ishita Rao", worker_id="W-3002", battery=91, signal_strength=-57, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-303", node_id="node-3-2", sector_id="sector-3", worker_name="Deepak Jain", worker_id="W-3003", battery=92, signal_strength=-55, status="online", last_updated=datetime.utcnow()),
            WearableDevice(id="WD-304", node_id="node-3-2", sector_id="sector-3", worker_name="Priya Sen", worker_id="W-3004", battery=89, signal_strength=-59, status="online", last_updated=datetime.utcnow()),
        ]
        db.add_all(devices)
        db.flush()

        base_time = datetime.utcnow() - timedelta(hours=3)
        readings = []
        for device in devices:
            readings.append(Reading(id=f"{device.id}-R1", device_id=device.id, temperature=28 if device.sector_id == "sector-1" else 39 if device.sector_id == "sector-2" else 26, humidity=55 if device.sector_id == "sector-1" else 74 if device.sector_id == "sector-2" else 58, methane=420 if device.sector_id == "sector-1" else 5200 if device.sector_id == "sector-2" else 300, carbon_monoxide=8 if device.sector_id == "sector-1" else 55 if device.sector_id == "sector-2" else 9, oxygen=20.9 if device.sector_id == "sector-1" else 17.8 if device.sector_id == "sector-2" else 21.1, heart_rate=78 if device.id.endswith(("1", "3")) else 82, x=10 + (len(readings) % 4), y=5 + (len(readings) % 3), z=3, recorded_at=base_time))
            readings.append(Reading(id=f"{device.id}-R2", device_id=device.id, temperature=29 if device.sector_id == "sector-1" else 40 if device.sector_id == "sector-2" else 27, humidity=57 if device.sector_id == "sector-1" else 76 if device.sector_id == "sector-2" else 59, methane=470 if device.sector_id == "sector-1" else 5300 if device.sector_id == "sector-2" else 310, carbon_monoxide=9 if device.sector_id == "sector-1" else 58 if device.sector_id == "sector-2" else 10, oxygen=20.8 if device.sector_id == "sector-1" else 17.5 if device.sector_id == "sector-2" else 21.0, heart_rate=80 if device.id.endswith(("1", "3")) else 84, x=11 + (len(readings) % 4), y=6 + (len(readings) % 3), z=4, recorded_at=base_time + timedelta(minutes=15)))
        db.add_all(readings)

        alerts = [
            Alert(id="AL-101", device_id="WD-201", node_id="node-2-1", sector_id="sector-2", worker_name="Rahul Meena", hazard="Methane High", severity="critical", state="active", acknowledged_by=None, temperature=39, humidity=74, methane=5200, carbon_monoxide=55, oxygen=17.8, x=20, y=15, z=4, created_at=datetime.utcnow() - timedelta(minutes=10)),
            Alert(id="AL-102", device_id="WD-203", node_id="node-2-2", sector_id="sector-2", worker_name="Sameer Khan", hazard="SOS Button Pressed", severity="critical", state="active", acknowledged_by=None, temperature=38, humidity=72, methane=4800, carbon_monoxide=50, oxygen=18.1, x=20, y=18, z=4, created_at=datetime.utcnow() - timedelta(minutes=8)),
            Alert(id="AL-103", device_id="WD-102", node_id="node-1-1", sector_id="sector-1", worker_name="Suresh Kumar", hazard="High Temperature", severity="warning", state="resolved", acknowledged_by="Rahul Sharma", temperature=36, humidity=67, methane=980, carbon_monoxide=24, oxygen=20.5, x=12, y=8, z=3, created_at=datetime.utcnow() - timedelta(hours=1)),
        ]
        db.add_all(alerts)

        thresholds = [Threshold(scope_id=mine.id, temperature_warning=35, temperature_critical=45, humidity_warning=70, humidity_critical=85, methane_warning=1000, methane_critical=5000, co_warning=25, co_critical=50, oxygen_warning_low=19.5, oxygen_critical_low=18, oxygen_warning_high=23.5, oxygen_critical_high=25)]
        db.add_all(thresholds)

        db.commit()
    finally:
        db.close()

import os
import sqlite3
from typing import Optional, List, Dict

DB_PATH = os.path.join("data", "clinic.db")


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # doctors: doctor_id PK
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id TEXT PRIMARY KEY,
            name TEXT,
            age TEXT,
            gender TEXT,
            specialization TEXT,
            fee REAL DEFAULT 0.0,
            room TEXT,
            status TEXT DEFAULT 'available'
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT,
            age TEXT,
            gender TEXT,
            disease TEXT,
            assigned_doctor_id TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            doctor_id TEXT,
            dt TEXT,
            status TEXT DEFAULT 'scheduled'
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rooms (
            room_id TEXT PRIMARY KEY,
            is_available INTEGER DEFAULT 1
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS timings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id TEXT,
            day TEXT,
            start TEXT,
            end TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            days INTEGER,
            daily_charge REAL,
            total REAL
        )
        """
    )

    conn.commit()
    conn.close()


def db_exists() -> bool:
    return os.path.exists(DB_PATH)


def add_doctor(doctor_id: str, name: str, age: str, gender: str, specialization: str, fee: float = 0.0, room: Optional[str] = None, status: str = "available"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO doctors(doctor_id,name,age,gender,specialization,fee,room,status) VALUES (?,?,?,?,?,?,?,?)",
        (doctor_id, name, age, gender, specialization, float(fee), room, status),
    )
    conn.commit()
    conn.close()


def get_doctors() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT doctor_id,name,age,gender,specialization,fee,room,status FROM doctors")
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["doctor_id", "name", "age", "gender", "specialization", "fee", "room", "status"], r)) for r in rows]


def get_doctor(doctor_id: str) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT doctor_id,name,age,gender,specialization,fee,room,status FROM doctors WHERE doctor_id=?", (doctor_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return dict(zip(["doctor_id", "name", "age", "gender", "specialization", "fee", "room", "status"], r))


def update_doctor_status(doctor_id: str, new_status: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE doctors SET status=? WHERE doctor_id=?", (new_status, doctor_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def update_doctor_fee(doctor_id: str, new_fee: float) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE doctors SET fee=? WHERE doctor_id=?", (float(new_fee), doctor_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def update_doctor_room(doctor_id: str, room: Optional[str]) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE doctors SET room=? WHERE doctor_id=?", (room, doctor_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def add_timing(doctor_id: str, day: str, start: str, end: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO timings(doctor_id,day,start,end) VALUES (?,?,?,?)", (doctor_id, day, start, end))
    conn.commit()
    conn.close()


def get_timings(doctor_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT day,start,end FROM timings WHERE doctor_id=?", (doctor_id,))
    rows = cur.fetchall()
    conn.close()
    return [(r[0], r[1], r[2]) for r in rows]


def remove_timing(doctor_id: str, day: str, start: str, end: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM timings WHERE doctor_id=? AND day=? AND start=? AND end=?", (doctor_id, day, start, end))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def add_patient(patient_id: str, name: str, age: str, gender: str, disease: str, assigned_doctor_id: Optional[str] = None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO patients(patient_id,name,age,gender,disease,assigned_doctor_id) VALUES (?,?,?,?,?,?)",
        (patient_id, name, age, gender, disease, assigned_doctor_id),
    )
    conn.commit()
    conn.close()


def get_patients():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT patient_id,name,age,gender,disease,assigned_doctor_id FROM patients")
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["patient_id", "name", "age", "gender", "disease", "assigned_doctor_id"], r)) for r in rows]


def assign_doctor_to_patient(patient_id: str, doctor_id: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE patients SET assigned_doctor_id=? WHERE patient_id=?", (doctor_id, patient_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def add_appointment(patient_id: str, doctor_id: str, dt: str, status: str = "scheduled"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO appointments(patient_id,doctor_id,dt,status) VALUES (?,?,?,?)", (patient_id, doctor_id, dt, status))
    conn.commit()
    conn.close()


def list_appointments():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id,patient_id,doctor_id,dt,status FROM appointments ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "patient_id", "doctor_id", "date", "status"], r)) for r in rows]


def update_appointment_status(appointment_id: int, new_status: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status=? WHERE id=?", (new_status, appointment_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def add_room(room_id: str, is_available: bool = True):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO rooms(room_id,is_available) VALUES (?,?)", (room_id, 1 if is_available else 0))
    conn.commit()
    conn.close()


def list_rooms():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT room_id,is_available FROM rooms")
    rows = cur.fetchall()
    conn.close()
    return [(r[0], bool(r[1])) for r in rows]


def update_room(room_id: str, is_available: bool) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET is_available=? WHERE room_id=?", (1 if is_available else 0, room_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def add_billing(patient_id: str, days: int, daily_charge: float):
    total = int(days) * float(daily_charge)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO billing(patient_id,days,daily_charge,total) VALUES (?,?,?,?)", (patient_id, int(days), float(daily_charge), total))
    conn.commit()
    conn.close()


def list_billing():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id,patient_id,days,daily_charge,total FROM billing")
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "patient_id", "days", "daily_charge", "total"], r)) for r in rows]

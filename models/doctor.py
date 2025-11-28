import os


class Doctor:
    def __init__(self, doctor_id, name, age, gender, specialization, fee: float = 0.0, room: str = None, status: str = "available"):
        self.doctor_id = doctor_id
        self.name = name
        self.age = age
        self.gender = gender
        self.specialization = specialization
        self.fee = float(fee) if fee is not None and fee != "" else 0.0
        self.room = room
        self.status = status

    def to_line(self):
        # doctor_id,name,age,gender,specialization,fee,room,status
        return f"{self.doctor_id},{self.name},{self.age},{self.gender},{self.specialization},{self.fee},{self.room if self.room is not None else ''},{self.status}"

    def save_to_file(self):
        os.makedirs("data", exist_ok=True)
        with open("data/doctors.txt", "a") as f:
            f.write(self.to_line() + "\n")
        try:
            from models import db
            if db.db_exists():
                db.add_doctor(self.doctor_id, self.name, self.age, self.gender, self.specialization, self.fee, self.room, self.status)
        except Exception:
            pass

    @staticmethod
    def load_all():
        # prefer sqlite if available
        try:
            from models import db
            if db.db_exists():
                docs = db.get_doctors()
                return [Doctor(d['doctor_id'], d['name'], d['age'], d['gender'], d['specialization'], d.get('fee', 0.0), d.get('room'), d.get('status', 'available')) for d in docs]
        except Exception:
            pass

        doctors = []
        try:
            with open("data/doctors.txt", "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    parts = line.strip().split(",")
                    # support legacy formats (5 fields) by filling defaults
                    while len(parts) < 8:
                        parts.append("")
                    did, name, age, gender, spec, fee, room, status = parts[:8]
                    d = Doctor(did, name, age, gender, spec, fee or 0.0, room or None, status or "available")
                    doctors.append(d)
        except FileNotFoundError:
            pass
        return doctors

    @staticmethod
    def find_by_id(doctor_id: str):
        try:
            from models import db
            if db.db_exists():
                row = db.get_doctor(str(doctor_id))
                if row:
                    return Doctor(row['doctor_id'], row['name'], row['age'], row['gender'], row['specialization'], row.get('fee', 0.0), row.get('room'), row.get('status', 'available'))
        except Exception:
            pass

        for d in Doctor.load_all():
            if d.doctor_id == str(doctor_id):
                return d
        return None

    @staticmethod
    def update_status(doctor_id: str, new_status: str):
        try:
            from models import db
            if db.db_exists():
                return db.update_doctor_status(str(doctor_id), new_status)
        except Exception:
            pass

        try:
            with open("data/doctors.txt", "r") as fh:
                lines = [l.rstrip() for l in fh if l.strip()]
        except FileNotFoundError:
            return False
        changed = False
        for i, ln in enumerate(lines):
            parts = ln.split(",")
            if parts[0] == str(doctor_id):
                while len(parts) < 8:
                    parts.append("")
                parts[7] = new_status
                lines[i] = ",".join(parts)
                changed = True
        if not changed:
            return False
        with open("data/doctors.txt", "w") as f:
            for l in lines:
                f.write(l + "\n")
        return True

    @staticmethod
    def update_fee(doctor_id: str, new_fee: float):
        try:
            from models import db
            if db.db_exists():
                return db.update_doctor_fee(str(doctor_id), float(new_fee))
        except Exception:
            pass

        # fallback to file
        try:
            with open("data/doctors.txt", "r") as fh:
                lines = [l.rstrip() for l in fh if l.strip()]
        except FileNotFoundError:
            return False

        changed = False
        for i, ln in enumerate(lines):
            parts = ln.split(",")
            if parts[0] == str(doctor_id):
                while len(parts) < 8:
                    parts.append("")
                parts[5] = str(float(new_fee))
                lines[i] = ",".join(parts)
                changed = True

        if not changed:
            return False

        with open("data/doctors.txt", "w") as fh:
            for l in lines:
                fh.write(l + "\n")
        return True

    @staticmethod
    def update_room(doctor_id: str, new_room: str):
        db_ok = False
        try:
            from models import db
            if db.db_exists():
                db_ok = db.update_doctor_room(str(doctor_id), new_room)
        except Exception:
            db_ok = False

        try:
            with open("data/doctors.txt", "r") as fh:
                lines = [l.rstrip() for l in fh if l.strip()]
        except FileNotFoundError:
            return False

        changed = False
        for i, ln in enumerate(lines):
            parts = ln.split(",")
            if parts[0] == str(doctor_id):
                while len(parts) < 8:
                    parts.append("")
                parts[6] = new_room
                lines[i] = ",".join(parts)
                changed = True

        if not changed:
            return db_ok

        with open("data/doctors.txt", "w") as fh:
            for l in lines:
                fh.write(l + "\n")
        # return True if either DB or file update succeeded
        return True if (changed or db_ok) else False
    
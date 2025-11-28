import os


class Appointment:
    def __init__(self, patient_id, doctor_id, date, status: str = "scheduled"):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.status = status

    def save_to_file(self):
        os.makedirs("data", exist_ok=True)
        with open("data/appointments.txt", "a") as f:
            f.write(f"{self.patient_id},{self.doctor_id},{self.date},{self.status}\n")
        # save to sqlite if available
        try:
            from models import db
            if db.db_exists():
                db.add_appointment(self.patient_id, self.doctor_id, self.date, self.status)
        except Exception:
            pass

    @staticmethod
    def list_appointments():
        # prefer sqlite
        try:
            from models import db
            if db.db_exists():
                return db.list_appointments()
        except Exception:
            pass

        rows = []
        try:
            with open("data/appointments.txt", "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    parts = line.strip().split(",")
                    # patient, doctor, date, status
                    if len(parts) < 4:
                        parts += ["scheduled"] * (4 - len(parts))
                    rows.append({
                        "patient_id": parts[0],
                        "doctor_id": parts[1],
                        "date": parts[2],
                        "status": parts[3],
                    })
        except FileNotFoundError:
            pass
        return rows

    @staticmethod
    def update_status(index: int, new_status: str):
        # prefer sqlite: map index -> appointment id
        try:
            from models import db
            if db.db_exists():
                rows = db.list_appointments()
                if index < 0 or index >= len(rows):
                    return False
                appt_id = rows[index]['id']
                return db.update_appointment_status(appt_id, new_status)
        except Exception:
            pass

        # update the appointment at the given zero-based index (file-based fallback)
        try:
            with open("data/appointments.txt", "r") as fh:
                lines = [l.rstrip() for l in fh if l.strip()]
        except FileNotFoundError:
            return False
        if index < 0 or index >= len(lines):
            return False
        parts = lines[index].split(",")
        # ensure at least 4 parts
        if len(parts) < 4:
            parts += ["scheduled"] * (4 - len(parts))
        parts[3] = new_status
        lines[index] = ",".join(parts)
        with open("data/appointments.txt", "w") as f:
            for l in lines:
                f.write(l + "\n")
        return True

    @staticmethod
    def reschedule(index: int, new_date: str):
        # prefer sqlite: map index -> appointment id
        try:
            from models import db
            if db.db_exists():
                rows = db.list_appointments()
                if index < 0 or index >= len(rows):
                    return False
                appt_id = rows[index]['id']
                conn = db.get_conn()
        except Exception:
            pass

        try:
            with open("data/appointments.txt", "r") as fh:
                lines = [l.rstrip() for l in fh if l.strip()]
        except FileNotFoundError:
            return False

        if index < 0 or index >= len(lines):
            return False

        parts = lines[index].split(",")
        if len(parts) < 3:
            return False
        parts[2] = new_date
        lines[index] = ",".join(parts)
        with open("data/appointments.txt", "w") as f:
            for l in lines:
                f.write(l + "\n")
        try:
            # If DB exists, update particular appointment entry
            from models import db
            if db.db_exists():
                # find appointment id again
                rows = db.list_appointments()
                if index < 0 or index >= len(rows):
                    return True
                appt_id = rows[index]['id']
                # perform update
                conn = db.get_conn()
                cur = conn.cursor()
                cur.execute("UPDATE appointments SET dt=? WHERE id=?", (new_date, appt_id))
                conn.commit()
                conn.close()
        except Exception:
            pass

        return True

import os


class Patient:
    def __init__(self, patient_id, name, age, gender, disease):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.disease = disease
        self.assigned_doctor_id = None

    def save_to_file(self):
        # keep file-based storage for compatibility
        os.makedirs("data", exist_ok=True)
        with open("data/patients.txt", "a") as f:
            f.write(f"{self.patient_id},{self.name},{self.age},{self.gender},{self.disease},{self.assigned_doctor_id}\n")
        # and store in sqlite if available
        try:
            from models import db
            if db.db_exists():
                db.add_patient(self.patient_id, self.name, self.age, self.gender, self.disease, self.assigned_doctor_id)
        except Exception:
            pass

    @staticmethod
    def assign_doctor(patient_id, doctor_id):
        # prefer sqlite if available
        try:
            from models import db
            if db.db_exists():
                return db.assign_doctor_to_patient(str(patient_id), str(doctor_id))
        except Exception:
            pass

        lines = []
        with open("data/patients.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if parts[0] == str(patient_id):
                    # ensure enough parts
                    while len(parts) < 6:
                        parts.append("")
                    parts[5] = str(doctor_id)
                lines.append(",".join(parts))
        with open("data/patients.txt", "w") as f:
            for line in lines:
                f.write(line + "\n")
        return True

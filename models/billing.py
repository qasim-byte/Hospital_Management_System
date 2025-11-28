import os


class Billing:
    def __init__(self, patient_id, days, daily_charge):
        self.patient_id = patient_id
        self.days = days
        self.daily_charge = daily_charge
        self.total = self.days * self.daily_charge

    def save_to_file(self):
        os.makedirs("data", exist_ok=True)
        with open("data/billing.txt", "a") as f:
            f.write(f"{self.patient_id},{self.days},{self.daily_charge},{self.total}\n")
        # also store in sqlite if available
        try:
            from models import db
            if db.db_exists():
                db.add_billing(self.patient_id, self.days, self.daily_charge)
        except Exception:
            pass

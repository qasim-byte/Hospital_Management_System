import os
import tempfile
import importlib
import unittest
from datetime import datetime, timedelta


class TestEditDoctorFeatures(unittest.TestCase):
    def test_update_fee_persists(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()
            from models.doctor import Doctor
            d = Doctor('D200', 'Fee Doc', '39', 'F', 'Cardio', fee=45.0, room=None)
            d.save_to_file()

            ok = Doctor.update_fee('D200', 99.5)
            self.assertTrue(ok)
            loaded = Doctor.find_by_id('D200')
            self.assertIsNotNone(loaded)
            self.assertAlmostEqual(float(loaded.fee), 99.5)
        finally:
            os.chdir(cwd)

    def test_add_remove_timing_updates_availability(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()

            from models.doctor import Doctor
            d = Doctor('D300', 'Timing Doc', '50', 'M', 'General', fee=10.0)
            d.save_to_file()

            # ensure doctor not available initially
            free_initial = main.available_doctors_now()
            ids_init = [x.doctor_id for x in free_initial]
            self.assertNotIn('D300', ids_init)

            # add timing covering now
            now = datetime.now()
            start = (now - timedelta(minutes=30)).strftime('%H:%M')
            end = (now + timedelta(minutes=30)).strftime('%H:%M')
            main.add_timing_for_doctor('D300', now.strftime('%a'), start, end)

            free_after = main.available_doctors_now()
            ids_after = [x.doctor_id for x in free_after]
            self.assertIn('D300', ids_after)

            # remove timing
            ok = main.remove_timing_for_doctor('D300', now.strftime('%a'), start, end)
            self.assertTrue(ok)

            free_final = main.available_doctors_now()
            ids_final = [x.doctor_id for x in free_final]
            self.assertNotIn('D300', ids_final)

        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()

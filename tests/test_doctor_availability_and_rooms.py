import os
import tempfile
import importlib
import unittest
from datetime import datetime, timedelta


class DoctorAvailabilityRoomsTests(unittest.TestCase):
    def test_doctor_available_now(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()

            # create a doctor
            from models.doctor import Doctor
            d = Doctor('D_NOW', 'Now Doc', '50', 'M', 'General', fee=10.0, room=None, status='available')
            d.save_to_file()

            # add timing that includes now
            now = datetime.now()
            start = (now - timedelta(minutes=30)).strftime('%H:%M')
            end = (now + timedelta(minutes=30)).strftime('%H:%M')
            with open(main.TIMINGS_FILE, 'a') as f:
                f.write(f"D_NOW,{now.strftime('%a')},{start},{end}\n")

            free = main.available_doctors_now()
            ids = [x.doctor_id for x in free]
            self.assertIn('D_NOW', ids)
        finally:
            os.chdir(cwd)

    def test_add_room_and_assign(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()

            # add new room and confirm exists
            main.add_room('R_TEST', True)
            with open(main.ROOMS_FILE) as f:
                content = f.read()
                self.assertIn('R_TEST,True', content)

            # assign room to doctor and mark occupied
            from models.doctor import Doctor
            d = Doctor('D_ROOM', 'Room Doc', '40', 'F', 'Surgeon', fee=120.0, room='R_TEST', status='available')
            d.save_to_file()
            # mark occupied
            main.update_room_status('R_TEST', False)
            with open(main.ROOMS_FILE) as f:
                content = f.read()
                self.assertIn('R_TEST,False', content)

        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()

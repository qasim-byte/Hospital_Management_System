import os
import tempfile
import importlib
import unittest


class AssignAndStatusTests(unittest.TestCase):
    def test_assign_doctor_updates_patient(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            # create data dir and patient
            os.makedirs('data', exist_ok=True)
            with open(os.path.join('data', 'patients.txt'), 'w') as f:
                f.write('P1,Patient One,40,M,Checkup,None\n')
            # call assign
            from models.patient import Patient
            Patient.assign_doctor('P1', 'D50')
            with open(os.path.join('data', 'patients.txt')) as f:
                content = f.read()
                self.assertIn('P1,Patient One,40,M,Checkup,D50', content)
        finally:
            os.chdir(cwd)

    def test_appointment_status_update(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()

            from models.appointment import Appointment
            a1 = Appointment('P1', 'D1', '2025-12-01')
            a1.save_to_file()
            a2 = Appointment('P2', 'D1', '2025-12-02')
            a2.save_to_file()

            rows = Appointment.list_appointments()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['status'], 'scheduled')

            ok = Appointment.update_status(0, 'in-progress')
            self.assertTrue(ok)

            rows2 = Appointment.list_appointments()
            self.assertEqual(rows2[0]['status'], 'in-progress')

            # invalid index
            self.assertFalse(Appointment.update_status(10, 'completed'))

        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()

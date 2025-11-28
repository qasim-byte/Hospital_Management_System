import os
import tempfile
import importlib
import unittest


class AppointmentTests(unittest.TestCase):
    def test_add_appointment_and_assign_room(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()

            # create doctor and room
            main.add_doctor('D5', 'Dr Test', '40', 'M', 'General')
            main.add_room('R_TEST', True)

            ok, msg = main.add_appointment_and_assign_room('P1', 'D5', '2025-11-28 09:00', 'R_TEST')
            self.assertTrue(ok, msg)

            # check appointment in file
            with open(os.path.join('data', 'appointments.txt')) as f:
                content = f.read()
                self.assertIn('P1,D5,2025-11-28 09:00', content)

            # room should be marked occupied
            with open(os.path.join('data', 'rooms.txt')) as f:
                content = f.read()
                self.assertIn('R_TEST,False', content)

            # doctor's file should contain the room assignment
            with open(os.path.join('data', 'doctors.txt')) as f:
                content = f.read()
                self.assertIn('D5,Dr Test,40,M,General', content)
                # the line should contain R_TEST somewhere
                self.assertIn('R_TEST', content)

        finally:
            os.chdir(cwd)

    def test_reschedule_appointment(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()

            # add patient, doctor, appointment
            main.add_patient_interactive.__globals__['Patient'] = importlib.import_module('models.patient').Patient
            main.add_doctor('D9', 'Dr R', '50', 'F', 'Cardio')
            # create an appointment file entry
            from models.appointment import Appointment
            a = Appointment('P2', 'D9', '2025-11-28 10:00')
            a.save_to_file()

            # reschedule index 0
            ok = main.reschedule_appointment(0, '2025-11-29 11:30')
            self.assertTrue(ok)

            with open(os.path.join('data', 'appointments.txt')) as f:
                content = f.read()
                self.assertIn('P2,D9,2025-11-29 11:30', content)

        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()

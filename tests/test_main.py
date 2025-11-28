import os
import tempfile
import importlib
import unittest


class MainCLITests(unittest.TestCase):
    def test_ensure_data_files_creates_structure(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            # import module and call the helper
            main = importlib.import_module('main')
            main.ensure_data_files()
            self.assertTrue(os.path.isdir('data'))
            self.assertTrue(os.path.exists(os.path.join('data', 'patients.txt')))
            self.assertTrue(os.path.exists(os.path.join('data', 'doctors.txt')))
            self.assertTrue(os.path.exists(os.path.join('data', 'appointments.txt')))
        finally:
            os.chdir(cwd)

    def test_add_patient_and_persist(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            from models.patient import Patient
            os.makedirs('data', exist_ok=True)
            p = Patient('TP1', 'Test Person', '30', 'M', 'Checkup')
            p.save_to_file()
            with open(os.path.join('data', 'patients.txt'), 'r') as f:
                content = f.read()
                self.assertIn('TP1,Test Person,30,M,Checkup', content)
        finally:
            os.chdir(cwd)

if __name__ == '__main__':
    unittest.main()

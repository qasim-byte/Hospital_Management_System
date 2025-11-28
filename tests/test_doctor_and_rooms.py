import os
import tempfile
import importlib
import unittest


class DoctorRoomTests(unittest.TestCase):
    def test_add_doctor_persists(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()
            # use helper
            main.add_doctor('D100', 'Doc Tester', '45', 'F', 'General')
            with open(os.path.join('data', 'doctors.txt')) as f:
                content = f.read()
                self.assertIn('D100,Doc Tester,45,F,General', content)
        finally:
            os.chdir(cwd)

    def test_add_room_and_update(self):
        cwd = os.getcwd()
        td = tempfile.TemporaryDirectory()
        try:
            os.chdir(td.name)
            main = importlib.import_module('main')
            main.ensure_data_files()
            main.add_room('R42', True)
            with open(os.path.join('data', 'rooms.txt')) as f:
                content = f.read()
                self.assertIn('R42,True', content)

            # update R42 -> occupied
            ok = main.update_room_status('R42', False)
            self.assertTrue(ok)
            with open(os.path.join('data', 'rooms.txt')) as f:
                content = f.read()
                self.assertIn('R42,False', content)

            # non-existing room update should return False
            self.assertFalse(main.update_room_status('ROOM-XYZ', True))

        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()

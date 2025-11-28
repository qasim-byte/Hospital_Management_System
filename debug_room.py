import os
import tempfile
import importlib

cwd = os.getcwd()
td = tempfile.TemporaryDirectory()
os.chdir(td.name)
print('CWD ->', os.getcwd())
main = importlib.import_module('main')
main.ensure_data_files()
main.add_room('R42', True)
print('Before file contents:')
with open('data/rooms.txt','r') as f:
    print(f.read())
ok = main.update_room_status('R42', False)
print('Update returned:', ok)
print('After file contents:')
with open('data/rooms.txt','r') as f:
    print(f.read())
os.chdir(cwd)
print('Done')

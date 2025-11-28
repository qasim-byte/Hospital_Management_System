import os, tempfile, importlib

cwd = os.getcwd()
td = tempfile.TemporaryDirectory()
os.chdir(td.name)
main = importlib.import_module('main')
main.ensure_data_files()
main.add_room('R42', True)
with open('data/rooms.txt','r') as f:
    orig = [l.rstrip('\n') for l in f if l.strip()]
print('orig lines ->', orig)
lines = []
found = False
with open('data/rooms.txt','r') as f:
    for line in f:
        if not line.strip():
            continue
        rid, avail = line.strip().split(',')
        if rid == 'R42':
            lines.append(f"{rid},{'True' if False else 'False'}")
            found = True
        else:
            lines.append(line.strip())
print('Will write:', lines, 'found=', found)
with open('data/rooms.txt','w') as f:
    for l in lines:
        f.write(l+'\n')
with open('data/rooms.txt','r') as f:
    after = [l.rstrip('\n') for l in f if l.strip()]
print('After lines ->', after)
os.chdir(cwd)

import os
from datetime import datetime, timedelta

# Optional color support
try:
    from colorama import init as _colorama_init, Fore, Style
    _colorama_init(autoreset=True)
except Exception:
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = RESET = ""

    class Style:
        BRIGHT = RESET_ALL = ""

from models.patient import Patient
from models.doctor import Doctor
from models.billing import Billing
from models.appointment import Appointment

DATA_DIR = "data"
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.txt")
DOCTORS_FILE = os.path.join(DATA_DIR, "doctors.txt")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.txt")
ROOMS_FILE = os.path.join(DATA_DIR, "rooms.txt")
TIMINGS_FILE = os.path.join(DATA_DIR, "doctor_timings.txt")

PASSWORD = "admin123"


# UI helpers ------------------------------------------------------------------
def _col_widths(headers, rows):
    widths = [len(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], len(str(c)))
    return widths


def print_star_table(title: str, headers, rows):
    """Print a boxed table using '*' separator and aligned columns.

    headers: list[str]
    rows: list[list[str]] (rows may be empty)
    """
    headers = [str(h) for h in headers]
    rows = [[str(c) for c in row] for row in rows]
    widths = _col_widths(headers, rows)
    total_width = sum(widths) + 3 * (len(widths) - 1) + 4

    print('\n' + '*' * total_width)
    title_line = f"* {title.center(total_width - 4)} *"
    print(title_line)
    print('*' * total_width)

    # header
    def fmt_row(row):
        return '* ' + ' | '.join([str(v).ljust(w) for v, w in zip(row, widths)]) + ' *'

    print(fmt_row(headers))
    print('*' + '-'.join(['-' * (w + 2) for w in widths]) + '*')

    if not rows:
        print(fmt_row([''] * len(headers)))
    else:
        for r in rows:
            print(fmt_row(r))

    print('*' * total_width + '\n')


# Lookup helpers --------------------------------------------------------------
def get_doctor_name(doctor_id: str):
    if not doctor_id:
        return None
    try:
        d = Doctor.find_by_id(str(doctor_id))
        return d.name if d else None
    except Exception:
        return None


def get_patient_name(patient_id: str):
    if not patient_id:
        return None
    try:
        # prefer DB lookup
        from models import db
        if db.db_exists():
            rows = db.get_patients()
            for r in rows:
                if r.get('patient_id') == str(patient_id):
                    return r.get('name')
    except Exception:
        pass
    # file fallback
    try:
        with open(PATIENTS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if parts and parts[0] == str(patient_id):
                    return parts[1] if len(parts) > 1 else None
    except Exception:
        pass
    return None


def prompt_doctor_id(prompt_text: str = 'Doctor ID: '):
    did = input(prompt_text)
    if not did:
        return did
    name = get_doctor_name(did)
    if name:
        print(f"Selected doctor -> {did} : {name}")
    else:
        print(f"Selected doctor -> {did} : (name not found)")
    return did


def prompt_patient_id(prompt_text: str = 'Patient ID: '):
    pid = input(prompt_text)
    if not pid:
        return pid
    name = get_patient_name(pid)
    if name:
        print(f"Selected patient -> {pid} : {name}")
    else:
        print(f"Selected patient -> {pid} : (name not found)")
    return pid




def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path in (PATIENTS_FILE, DOCTORS_FILE, APPOINTMENTS_FILE):
        if not os.path.exists(path):
            open(path, "w").close()

    if not os.path.exists(ROOMS_FILE):
        default_rooms = ["Surgery1", "Surgery2", "Surgery3", "MedLab1", "MedLab2", "R23", "R24", "R25", "R26", "R29"]
        with open(ROOMS_FILE, "w") as f:
            for rid in default_rooms:
                f.write(f"{rid},True\n")

    if not os.path.exists(TIMINGS_FILE):
        with open(TIMINGS_FILE, "w") as f:
            f.write("D1,Mon,09:00,13:00\n")
            f.write("D1,Wed,10:00,15:00\n")

    # initialize sqlite DB if available
    try:
        from models import db
        db.init_db()
    except Exception:
        pass


def check_password(attempts=3):
    for _ in range(attempts):
        pwd = input("Enter system password: ")
        if pwd == PASSWORD:
            print(Fore.GREEN + "Access granted!" + Style.RESET_ALL)
            return True
        print(Fore.RED + "Wrong password!" + Style.RESET_ALL)

    print("Too many attempts. Exiting...")
    return False


def choose_db_or_file_patients():
    try:
        from models import db
        if db.db_exists():
            rows = db.get_patients()
            # prefer DB only when it has data
            if rows:
                return rows
    except Exception:
        pass
    # fallback to file
    rows = []
    try:
        with open(PATIENTS_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split(",")
                while len(parts) < 6:
                    parts.append("")
                rows.append({
                    "patient_id": parts[0],
                    "name": parts[1],
                    "age": parts[2],
                    "gender": parts[3],
                    "disease": parts[4],
                    "assigned_doctor_id": parts[5],
                })
    except FileNotFoundError:
        pass
    return rows


def list_patients():
    print("\n" + Style.BRIGHT + Fore.CYAN + "--- Patients ---" + Style.RESET_ALL)
    rows = choose_db_or_file_patients()
    if not rows:
        print("No patients found.")
        return
    headers = ["ID", "Name", "Age", "Gender", "Disease", "DoctorAssigned"]
    table_rows = [[r['patient_id'], r['name'], r['age'], r['gender'], r['disease'], r.get('assigned_doctor_id') or ''] for r in rows]
    print_star_table('Patients', headers, table_rows)


def doctors_assigned_to_patient():
    print("\n" + Style.BRIGHT + Fore.CYAN + "--- Doctor assigned to a Patient ---" + Style.RESET_ALL)
    pid = prompt_patient_id("Enter Patient ID (or press Enter to list all assignments): ")
    rows = choose_db_or_file_patients()
    if not rows:
        print("No patients found.")
        return
    headers = ["PatientID", "PatientName", "AssignedDoctorID"]
    table_rows = []
    for r in rows:
        aid = r.get('assigned_doctor_id') or ''
        if pid == "" and aid:
            table_rows.append([r['patient_id'], r['name'], aid])
        elif pid and r['patient_id'] == pid:
            table_rows.append([r['patient_id'], r['name'], aid])

    if not table_rows:
        print("No assigned doctors found for that query.")
    else:
        print_star_table('Doctor assignments', headers, table_rows)


def list_rooms_available():
    print("\n" + Style.BRIGHT + Fore.CYAN + "--- Rooms availability ---" + Style.RESET_ALL)
    try:
        from models import db
        if db.db_exists():
            rows = db.list_rooms()
            # if the DB has rows, use them; otherwise fall back to file-based data
            if rows:
                table_rows = [[rid, "Available" if avail else "Occupied"] for rid, avail in rows]
                print_star_table('Rooms', ['RoomID', 'Status'], table_rows)
                return
    except Exception:
        pass

    try:
        table_rows = []
        with open(ROOMS_FILE, "r") as f:
            for line in f:
                rid, avail = line.strip().split(",")
                status = "Available" if avail == "True" else "Occupied"
                table_rows.append([rid, status])
        if table_rows:
            print_star_table('Rooms', ['RoomID', 'Status'], table_rows)
        else:
            print('No rooms found.')
    except FileNotFoundError:
        print("No rooms data found.")


def show_doctors_timings():
    print("\n" + Style.BRIGHT + Fore.CYAN + "--- Doctor Timings ---" + Style.RESET_ALL)
    try:
        from models import db
        if db.db_exists():
            # show all timings in db
            # simple print of timings table
            cur_t = []
            conn = None
            try:
                import sqlite3
                conn = sqlite3.connect(os.path.join(DATA_DIR, 'clinic.db'))
                cur = conn.cursor()
                cur.execute("SELECT doctor_id,day,start,end FROM timings ORDER BY doctor_id")
                cur_t = cur.fetchall()
            finally:
                if conn:
                    conn.close()
            # if DB had no timings, let the file fallback run below
            if cur_t:
                table_rows = [[d, day, s, e] for d, day, s, e in cur_t]
                print_star_table('Doctor timings', ['DoctorID', 'Day', 'Start', 'End'], table_rows)
                return
    except Exception:
        pass

    try:
        with open(TIMINGS_FILE, 'r') as f:
            rows = [r.strip() for r in f if r.strip()]
            if not rows:
                print("No timings found.")
                return
            table_rows = [line.split(',') for line in rows]
            print_star_table('Doctor timings', ['DoctorID', 'Day', 'Start', 'End'], table_rows)
    except FileNotFoundError:
        print("No timings data found.")


def add_patient_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Add new patient ---" + Style.RESET_ALL)
    pid = prompt_patient_id("Patient ID: ")
    name = input("Name: ")
    age = input("Age: ")
    gender = input("Gender: ")
    disease = input("Disease: ")
    p = Patient(pid, name, age, gender, disease)
    p.save_to_file()

    # Optionally schedule with an available doctor
    if input("Book an appointment now with an available doctor? (y/n): ").strip().lower().startswith('y'):
        free = available_doctors_now()
        if not free:
            print(Fore.YELLOW + "No doctors are available right now." + Style.RESET_ALL)
            return
        headers = ["ID", "Name", "Specialization", "Fee", "Room", "Status"]
        table_rows = [[d.doctor_id, d.name, d.specialization, str(d.fee), d.room or '', d.status or ''] for d in free]
        print_star_table('Available doctors (now)', headers, table_rows)
        did = prompt_doctor_id("Enter doctor ID to book (or Enter to cancel): ")
        if not did:
            return
        # schedule now
        dt = input("Appointment date & time (YYYY-MM-DD HH:MM) or press Enter to book now: ")
        if not dt.strip():
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            appt_dt = datetime.strptime(dt, "%Y-%m-%d %H:%M")
        except Exception:
            print("Invalid date/time format; appointment not scheduled.")
            return
        # validate timing
        weekday = appt_dt.strftime('%a')
        timings = load_timings_for_doctor(did)
        ok = False
        for day, s, e in timings:
            if day[:3].lower() == weekday[:3].lower() and _time_in_range(s, e, appt_dt.time()):
                ok = True
                break
        if not ok:
            print(Fore.YELLOW + "Doctor is not free at that time. Please pick another time." + Style.RESET_ALL)
            show_doctor_schedule(did)
            return
        app = Appointment(pid, did, dt)
        app.save_to_file()
        print(Fore.GREEN + "Appointment scheduled!" + Style.RESET_ALL)
        # if appointment is near now, mark busy
        if abs((appt_dt - datetime.now()).total_seconds()) < 15 * 60:
            Doctor.update_status(did, 'busy')


def add_doctor_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Add new doctor ---" + Style.RESET_ALL)
    did = prompt_doctor_id("Doctor ID: ")
    name = input("Name: ")
    age = input("Age: ")
    gender = input("Gender: ")
    specialization = input("Specialization: ")
    fee = input("Consultation fee (e.g. 50.0): ")

    # choose room from available
    avail_rooms = []
    try:
        from models import db
        if db.db_exists():
            avail_rooms = [r for r, a in db.list_rooms() if a]
    except Exception:
        try:
            with open(ROOMS_FILE, 'r') as f:
                for line in f:
                    r, a = line.strip().split(',')
                    if a == 'True':
                        avail_rooms.append(r)
        except Exception:
            pass

    assigned_room = None
    if avail_rooms:
        print("Available rooms:")
        for r in avail_rooms:
            print(" -", r)
        assign = input("Assign one of these room IDs to this doctor (or press Enter to skip): ")
        if assign.strip() in avail_rooms:
            assigned_room = assign.strip()
            update_room_status(assigned_room, False)

    d = Doctor(did, name, age, gender, specialization, fee or 0.0, assigned_room, 'available')
    d.save_to_file()
    print("Now add working timings for this doctor (empty line to finish):")
    while True:
        t = input('Timing (e.g. Mon 09:00-13:00): ').strip()
        if not t:
            break
        try:
            day, times = t.split()
            start, end = times.split('-')
            add_timing_for_doctor(did, day, start, end)
        except Exception:
            print('Invalid format; use Mon 09:00-13:00')


def add_doctor(did: str, name: str, age: str, gender: str, spec: str):
    d = Doctor(did, name, age, gender, spec)
    d.save_to_file()
    return d


def add_room(room_id: str, is_available: bool = True):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ROOMS_FILE, "a") as f:
        f.write(f"{room_id},{'True' if is_available else 'False'}\n")
    try:
        from models import db
        if db.db_exists():
            db.add_room(room_id, is_available)
    except Exception:
        pass


def add_room_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Add new Room ---" + Style.RESET_ALL)
    rid = input("Room ID (e.g. R10): ")
    avail = input("Is room available? (y/n): ")
    add_room(rid, avail.strip().lower().startswith('y'))
    print(Fore.GREEN + "Room added!" + Style.RESET_ALL)


def update_room_status(room_id: str, new_status: bool):
    db_ok = False
    # try sqlite update (if available) but still update file for compatibility
    try:
        from models import db
        if db.db_exists():
            db_ok = db.update_room(room_id, new_status)
    except Exception:
        db_ok = False

    # update file as well (ensure file-backed data stays in sync for tests)
    try:
        lines = []
        found = False
        with open(ROOMS_FILE, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                rid, avail = line.strip().split(',')
                if rid == room_id:
                    lines.append(f"{rid},{'True' if new_status else 'False'}")
                    found = True
                else:
                    lines.append(line.strip())
        if not found:
            # no such room in file — if DB reported success return that, otherwise False
            return db_ok
        with open(ROOMS_FILE, 'w') as f:
            for l in lines:
                f.write(l + '\n')
        # return True if either DB or file update succeeded
        return True if (found or db_ok) else False
    except FileNotFoundError:
        return False


def update_room_status_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Update Room status ---" + Style.RESET_ALL)
    rid = input("Room ID to update: ")
    status = input("Set to (a)vailable or (o)ccupied? (a/o): ")
    ok = update_room_status(rid, status.strip().lower().startswith('a'))
    print(Fore.GREEN + "Room status updated." + Style.RESET_ALL if ok else Fore.RED + "Room not found." + Style.RESET_ALL)


def remove_patient_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Remove patient ---" + Style.RESET_ALL)
    pid = prompt_patient_id("Patient ID to remove: ")
    try:
        # try sqlite
        from models import db
        if db.db_exists():
            # no delete helper in db layer, use file fallback for now
            pass
    except Exception:
        pass
    try:
        kept = []
        removed = False
        with open(PATIENTS_FILE, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith(pid + ','):
                    kept.append(line.rstrip())
                else:
                    removed = True
        with open(PATIENTS_FILE, 'w') as f:
            for line in kept:
                f.write(line + '\n')
        print(Fore.GREEN + f"Patient {pid} removed." + Style.RESET_ALL if removed else Fore.YELLOW + f"Patient {pid} not found." + Style.RESET_ALL)
    except FileNotFoundError:
        print(Fore.RED + "Patient storage not found." + Style.RESET_ALL)


def schedule_appointment_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Schedule Appointment ---" + Style.RESET_ALL)
    pid = prompt_patient_id("Patient ID: ")
    did = prompt_doctor_id("Doctor ID: ")
    date = input("Appointment Date (YYYY-MM-DD HH:MM): ")
    app = Appointment(pid, did, date)
    app.save_to_file()
    print(Fore.GREEN + "Appointment scheduled!" + Style.RESET_ALL)


def load_timings_for_doctor(doctor_id: str):
    # prefer sqlite
    try:
        from models import db
        if db.db_exists():
            rows = db.get_timings(doctor_id)
            if rows:
                return rows
    except Exception:
        pass
    # file fallback
    out = []
    try:
        with open(TIMINGS_FILE, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split(',')
                if parts[0] == doctor_id:
                    out.append((parts[1], parts[2], parts[3]))
    except FileNotFoundError:
        pass
    return out


def _time_in_range(start_str: str, end_str: str, check_time):
    fmt = "%H:%M"
    s = datetime.strptime(start_str, fmt).time()
    e = datetime.strptime(end_str, fmt).time()
    if s <= e:
        return s <= check_time <= e
    return check_time >= s or check_time <= e


def doctor_is_available_now(doctor_id: str):
    try:
        d = Doctor.find_by_id(doctor_id)
        if not d:
            return False
        if d.status and d.status.lower() in ['busy', 'break', 'off']:
            return False
        now = datetime.now()
        weekday = now.strftime('%a')
        for day, s, e in load_timings_for_doctor(doctor_id):
            if day[:3].lower() == weekday[:3].lower() and _time_in_range(s, e, now.time()):
                return True
    except Exception:
        pass
    return False


def available_doctors_now():
    docs = Doctor.load_all()
    return [d for d in docs if doctor_is_available_now(d.doctor_id)]


def show_doctor_schedule(doctor_id: str):
    ts = load_timings_for_doctor(doctor_id)
    if not ts:
        print("No schedule found for this doctor.")
        return
    print(f"Schedule for {doctor_id}:")
    for day, s, e in ts:
        print(f" - {day}: {s} to {e}")


def add_timing_for_doctor(doctor_id: str, day: str, start: str, end: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        from models import db
        if db.db_exists():
            db.add_timing(doctor_id, day, start, end)
            return
    except Exception:
        pass
    with open(TIMINGS_FILE, 'a') as f:
        f.write(f"{doctor_id},{day},{start},{end}\n")


def remove_timing_for_doctor(doctor_id: str, day: str, start: str, end: str):
    try:
        from models import db
        if db.db_exists():
            return db.remove_timing(doctor_id, day, start, end)
    except Exception:
        pass
    try:
        with open(TIMINGS_FILE, 'r') as f:
            lines = [l.rstrip() for l in f if l.strip()]
    except FileNotFoundError:
        return False
    new_lines = []
    removed = False
    for ln in lines:
        parts = ln.split(',')
        if len(parts) < 4:
            new_lines.append(ln)
            continue
        did, dday, s, e = parts[0], parts[1], parts[2], parts[3]
        if did == doctor_id and dday == day and s == start and e == end:
            removed = True
            continue
        new_lines.append(ln)
    with open(TIMINGS_FILE, 'w') as f:
        for l in new_lines:
            f.write(l + '\n')
    return removed


def edit_doctor_schedule_interactive(doctor_id: str):
    print(f"\n✍️  Edit schedule for {doctor_id}")
    while True:
        print("1. Add timing")
        print("2. Remove timing")
        print("3. List timings")
        print("4. Back")
        ch = input("Choice: ")
        if ch == '1':
            t = input('Enter timing (e.g. Mon 09:00-13:00): ').strip()
            if not t:
                continue
            try:
                day, times = t.split()
                start, end = times.split('-')
                add_timing_for_doctor(doctor_id, day, start, end)
                print('✅ Timing added.')
            except Exception:
                print('Invalid format. Use Mon 09:00-13:00')
        elif ch == '2':
            t = input('Enter timing to remove (e.g. Mon 09:00-13:00): ').strip()
            try:
                day, times = t.split()
                start, end = times.split('-')
                ok = remove_timing_for_doctor(doctor_id, day, start, end)
                print('✅ Removed.' if ok else 'Timing not found.')
            except Exception:
                print('Invalid format.')
        elif ch == '3':
            show_doctor_schedule(doctor_id)
        elif ch == '4':
            break
        else:
            print('Invalid choice')


def change_doctor_fee_interactive(doctor_id: str):
    d = Doctor.find_by_id(doctor_id)
    if not d:
        print('Doctor not found')
        return
    print(f"Current fee for {d.doctor_id} - {d.name}: {d.fee}")
    new_fe = input('New fee (e.g. 100.0): ')
    try:
        fval = float(new_fe)
    except Exception:
        print('Invalid fee format')
        return
    ok = Doctor.update_fee(doctor_id, fval)
    print('✅ Fee updated.' if ok else 'Failed to update fee')


def list_appointments():
    print("\n" + Style.BRIGHT + Fore.CYAN + "--- Appointments ---" + Style.RESET_ALL)
    rows = Appointment.list_appointments()
    if not rows:
        print("No appointments found.")
        return []
    headers = ["#", "PatientID", "DoctorID", "Date", "Status"]
    table_rows = [[str(i), r.get('patient_id'), r.get('doctor_id'), r.get('date'), r.get('status')] for i, r in enumerate(rows)]
    print_star_table('Appointments', headers, table_rows)
    return rows


def add_appointment_and_assign_room(patient_id: str, doctor_id: str, date_str: str, room_id: str = None):
    """Programmatic helper — create appointment, record it, assign room to doctor and mark room occupied."""
    # check doctor exists
    d = Doctor.find_by_id(doctor_id)
    if not d:
        return False, "Doctor not found"

    # check room availability
    if room_id:
        # check DB first
        room_ok = False
        try:
            from models import db
            if db.db_exists():
                rows = db.list_rooms()
                room_ok = any(r == room_id and a for r, a in rows)
        except Exception:
            room_ok = False

        if not room_ok:
            try:
                with open(ROOMS_FILE, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        r, a = line.strip().split(',')
                        if r == room_id and a == 'True':
                            room_ok = True
                            break
            except FileNotFoundError:
                pass

        if not room_ok:
            return False, "Room not available"

    app = Appointment(patient_id, doctor_id, date_str)
    app.save_to_file()

    # assign room to doctor and mark room occupied
    if room_id:
        try:
            Doctor.update_room(doctor_id, room_id)
        except Exception:
            pass
        update_room_status(room_id, False)

    return True, "Appointment created"


def add_appointment_and_assign_room_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Add Appointment & assign Room ---" + Style.RESET_ALL)
    pid = prompt_patient_id('Patient ID: ')
    did = prompt_doctor_id('Doctor ID: ')
    date = input('Date & time (YYYY-MM-DD HH:MM): ')

    # list available rooms
    avail_rooms = []
    try:
        from models import db
        if db.db_exists():
            avail_rooms = [r for r, a in db.list_rooms() if a]
    except Exception:
        try:
            with open(ROOMS_FILE, 'r') as f:
                for line in f:
                    r, a = line.strip().split(',')
                    if a == 'True':
                        avail_rooms.append(r)
        except Exception:
            pass

    chosen_room = None
    if avail_rooms:
        print('Available rooms:')
        for r in avail_rooms:
            print(' -', r)
        chosen = input('Pick room (or press Enter to skip): ').strip()
        if chosen in avail_rooms:
            chosen_room = chosen

    ok, msg = add_appointment_and_assign_room(pid, did, date, chosen_room)
    if ok:
        print(Fore.GREEN + msg + Style.RESET_ALL)
    else:
        print(Fore.RED + msg + Style.RESET_ALL)


def reschedule_appointment(index: int, new_date: str):
    return Appointment.reschedule(index, new_date)


def reschedule_appointment_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Reschedule Appointment ---" + Style.RESET_ALL)
    rows = list_appointments()
    if not rows:
        return
    try:
        idx = int(input('Appointment number to reschedule: '))
    except ValueError:
        print('Invalid number')
        return
    nd = input('New date & time (YYYY-MM-DD HH:MM): ')
    ok = reschedule_appointment(idx, nd)
    print(Fore.GREEN + 'Rescheduled.' + Style.RESET_ALL if ok else Fore.RED + 'Failed to reschedule.' + Style.RESET_ALL)


def assign_doctor_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Assign Doctor to Patient ---" + Style.RESET_ALL)
    pid = prompt_patient_id("Patient ID: ")
    did = prompt_doctor_id("Doctor ID: ")
    # prefer db
    try:
        from models import db
        if db.db_exists():
            ok = db.assign_doctor_to_patient(pid, did)
            print(Fore.GREEN + "Doctor assigned." + Style.RESET_ALL if ok else Fore.RED + "Failed to assign doctor." + Style.RESET_ALL)
            return
    except Exception:
        pass
    # file fallback
    try:
        Patient.assign_doctor(pid, did)
        print(Fore.GREEN + "Doctor assigned." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Failed to assign doctor: {e}" + Style.RESET_ALL)


def update_appointment_status_interactive():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "--- Update Appointment Status ---" + Style.RESET_ALL)
    rows = list_appointments()
    if not rows:
        return
    try:
        idx = int(input("Enter appointment number to update: "))
    except ValueError:
        print("Invalid number")
        return
    statuses = ["scheduled", "in-progress", "completed", "busy", "break"]
    print("Choose new status:")
    for i, s in enumerate(statuses, start=1):
        print(f"{i}. {s}")
    try:
        sidx = int(input("Enter status number: ")) - 1
        if sidx < 0 or sidx >= len(statuses):
            print("Invalid status")
            return
        new_status = statuses[sidx]
        ok = Appointment.update_status(idx, new_status)
        if ok:
            print(Fore.GREEN + "Appointment status updated." + Style.RESET_ALL)
            # try update doctor status based on appointment
            try:
                rows2 = Appointment.list_appointments()
                if idx < len(rows2):
                    doc = rows2[idx].get('doctor_id')
                    if new_status == 'completed':
                        Doctor.update_status(doc, 'available')
                    elif new_status in ('in-progress', 'busy'):
                        Doctor.update_status(doc, 'busy')
                    elif new_status == 'break':
                        Doctor.update_status(doc, 'break')
            except Exception:
                pass
        else:
            print(Fore.RED + "Failed to update appointment status." + Style.RESET_ALL)
    except ValueError:
        print("Invalid input.")


def list_free_slots_for_doctor(doctor_id: str, date_str: str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        print("Invalid date format")
        return
    weekday = dt.strftime('%a')
    timings = load_timings_for_doctor(doctor_id)
    day_slots = []
    for day, s, e in timings:
        if day[:3].lower() == weekday[:3].lower():
            start = datetime.strptime(s, "%H:%M")
            end = datetime.strptime(e, "%H:%M")
            cur = start
            while cur + timedelta(hours=1) <= end:
                day_slots.append((cur.time().strftime('%H:%M'), (cur + timedelta(hours=1)).time().strftime('%H:%M')))
                cur = cur + timedelta(hours=1)
    if not day_slots:
        print("No working hours for this doctor on that date.")
        return
    appts = Appointment.list_appointments()
    occupied = set()
    for a in appts:
        if a.get('doctor_id') == doctor_id:
            try:
                adt = datetime.strptime(a.get('date'), "%Y-%m-%d %H:%M")
            except Exception:
                continue
            if adt.date() == dt.date():
                occupied.add(adt.time().strftime('%H:%M'))
    # present in a table
    headers = ["Start", "End", "Status"]
    table_rows = [[s, e, "Occupied" if s in occupied else "Free"] for s, e in day_slots]
    print_star_table(f"Free slots for Dr {doctor_id} on {date_str}", headers, table_rows)


def doctor_billing_menu():
    while True:
        print("\n--- Billing & Fees ---")
        print("1. List doctors and fees")
        print("2. Generate simple consultation bill for a patient")
        print("3. Back")
        ch = input("Choice: ")
        if ch == '1':
            docs = Doctor.load_all()
            if not docs:
                print('No doctors found.')
            else:
                headers = ["ID", "Name", "Fee"]
                table_rows = [[d.doctor_id, d.name, str(d.fee)] for d in docs]
                print_star_table('Doctors & Fees', headers, table_rows)
        elif ch == '2':
            pid = prompt_patient_id('Patient ID: ')
            did = prompt_doctor_id('Doctor ID: ')
            d = Doctor.find_by_id(did)
            if not d:
                print('Doctor not found.')
                continue
            bill = Billing(pid, 1, float(d.fee))
            bill.save_to_file()
            print(f"Bill generated: {bill.total}")
        elif ch == '3':
            break
        else:
            print('Invalid')


def doctor_menu():
    while True:
        print("\n" + Style.BRIGHT + Fore.CYAN + "--- Doctors Menu ---" + Style.RESET_ALL)
        print("1. Add doctor")
        print("2. See available doctors (now)")
        print("3. List all doctors")
        print("4. Update doctor status")
        print("5. View doctor schedule")
        print("6. Edit doctor's schedule (add/remove timings)")
        print("7. Change doctor's fee")
        print("8. Back")
        ch = input('Choice: ')
        if ch == '1':
            add_doctor_interactive()
        elif ch == '2':
            free = available_doctors_now()
            if not free:
                print(Fore.YELLOW + 'No doctors available right now.' + Style.RESET_ALL)
            else:
                headers = ["ID", "Name", "Specialization", "Fee", "Room", "Status"]
                table_rows = [[d.doctor_id, d.name, d.specialization, str(d.fee), d.room or '', d.status or ''] for d in free]
                print_star_table('Available doctors (now)', headers, table_rows)
        elif ch == '3':
            docs = Doctor.load_all()
            if not docs:
                print(Fore.YELLOW + 'No doctors registered yet.' + Style.RESET_ALL)
            else:
                headers = ["ID", "Name", "Specialization", "Fee", "Room", "Status"]
                table_rows = [[d.doctor_id, d.name, d.specialization, str(d.fee), d.room or '', d.status or ''] for d in docs]
                print_star_table('All doctors', headers, table_rows)
        elif ch == '4':
            did = prompt_doctor_id('Doctor ID: ')
            ns = input('New status (available/busy/break/off): ')
            ok = Doctor.update_status(did, ns)
            print('Updated' if ok else 'Doctor not found')
        elif ch == '5':
            did = prompt_doctor_id('Doctor ID: ')
            show_doctor_schedule(did)
        elif ch == '6':
            did = prompt_doctor_id('Doctor ID to edit schedule: ')
            edit_doctor_schedule_interactive(did)
        elif ch == '7':
            did = prompt_doctor_id('Doctor ID to change fee: ')
            change_doctor_fee_interactive(did)
        elif ch == '8':
            break
        else:
            print('Invalid choice')


def patient_menu():
    while True:
        print("\n" + Style.BRIGHT + Fore.CYAN + "--- Patients Menu ---" + Style.RESET_ALL)
        print('1. Add patient')
        print('2. Remove patient')
        print('3. List patients')
        print('4. Back')
        ch = input('Choice: ')
        if ch == '1':
            add_patient_interactive()
        elif ch == '2':
            remove_patient_interactive()
        elif ch == '3':
            list_patients()
        elif ch == '4':
            break
        else:
            print('Invalid choice')


def appointment_menu():
    while True:
        print("\n" + Style.BRIGHT + Fore.CYAN + "--- Appointments Menu ---" + Style.RESET_ALL)
        print('1. List appointments')
        print('2. Free slots for a doctor on a date')
        print('3. Add appointment and assign room')
        print('4. Reschedule appointment')
        print('5. Billing & fees (list + generate simple bill)')
        print('6. Update appointment status')
        print('7. Back')
        ch = input('Choice: ')
        if ch == '1':
            list_appointments()
        elif ch == '2':
            did = prompt_doctor_id('Doctor ID: ')
            date = input('Date (YYYY-MM-DD): ')
            list_free_slots_for_doctor(did, date)
        elif ch == '3':
            add_appointment_and_assign_room_interactive()
        elif ch == '4':
            reschedule_appointment_interactive()
        elif ch == '5':
            doctor_billing_menu()
        elif ch == '6':
            update_appointment_status_interactive()
        elif ch == '7':
            break
        else:
            print('Invalid choice')


def rooms_menu():
    while True:
        print("\n" + Style.BRIGHT + Fore.CYAN + "--- Rooms Menu ---" + Style.RESET_ALL)
        print('1. List rooms and availability')
        print('2. Add room')
        print('3. Update room status')
        print('4. Back')
        ch = input('Choice: ')
        if ch == '1':
            list_rooms_available()
        elif ch == '2':
            add_room_interactive()
        elif ch == '3':
            update_room_status_interactive()
        elif ch == '4':
            break
        else:
            print('Invalid choice')


def main_menu():
    while True:
        title = "🏥 ================= Qasim's Clinic ================= 🏥"
        print('\n' + Style.BRIGHT + Fore.BLUE + title + Style.RESET_ALL)
        print(Fore.YELLOW + '🔐 Main — choose a section:' + Style.RESET_ALL)
        print('1. Doctors 👩‍⚕️👨‍⚕️')
        print('2. Patients 🧑‍🤝‍🧑')
        print('3. Appointments 📅')
        print('4. Rooms 🛏️')
        print('5. Exit')
        choice = input('Enter section choice: ')
        if choice == '1':
            doctor_menu()
        elif choice == '2':
            patient_menu()
        elif choice == '3':
            appointment_menu()
        elif choice == '4':
            rooms_menu()
        elif choice == '5':
            print('Goodbye! 👋')
            break
        else:
            print('Invalid choice.')


if __name__ == '__main__':
    ensure_data_files()
    print('\nWelcome to Qasim\'s Clinic 👋')
    if check_password():
        main_menu()

# Qasim's Clinic — Hospital Management CLI

Small CLI app demonstrating a file-based hospital management flow with three main sections: Doctors, Patients, and Appointments.

🔒 Password-protected front page (default `admin123`) — change `PASSWORD` in `main.py` for production.

Key features
- Clean main menu with 3 sections: Doctors, Patients, Appointments. Also a Rooms menu.
- Doctors:
- Doctors:
  - Add a doctor along with weekly timings (e.g. "Mon 09:00-13:00"), assign a room, and set consultation fees.
  - Edit a doctor's weekly timings (add / remove) and change consultation fees from the Doctors menu.
  - View available doctors right now (computed from local PC time + doctor's status).
  - Update a doctor's current status (available, busy, break, off).
- Patients:
  - Add / Remove / List patients.
  - When adding a patient, you can pick an available doctor or schedule for a future date/time; the system validates the doctor's weekly schedule.
- Appointments:
  - Schedule and list appointments. Appointments store a small status value (scheduled, in-progress, completed, busy, break).
  - Update appointment status — when an appointment is marked completed or in-progress it will update the doctor's status accordingly.
  - Free slots: list hourly free/occupied slots for a doctor on a chosen date (based on doctor schedule + existing appointments).
  - Billing: list doctors and fees and generate a simple consultation bill saved in `data/billing.txt`.
- Rooms:
  - Default rooms created: Surgery1, Surgery2, Surgery3, MedLab1, MedLab2, R23, R24, R25, R26, R29.
  - Add new rooms, assign a room to a doctor when adding (this marks the room occupied), and change room availability.

Storage
- All data is saved under `data/` (auto-created). Files include: `patients.txt`, `doctors.txt`, `appointments.txt`, `rooms.txt`, `doctor_timings.txt`, `billing.txt`.
Storage
- All data is saved under `data/` (auto-created). Files include: `patients.txt`, `doctors.txt`, `appointments.txt`, `rooms.txt`, `doctor_timings.txt`, `billing.txt`.
- New: a small SQLite database is used at `data/clinic.db` (created automatically). The CLI prefers the sqlite DB for reads/writes where possible and keeps file-format as a fallback for backwards compatibility.

Running
1. Make sure you have Python 3.8+ installed.
2. From the project root run:

```powershell
python main.py
```

3. Enter the password when prompted (default `admin123`).

Tests
- Unit tests are in the `tests/` folder. Run them via:

```powershell
python -m unittest -q
```

Notes
- This is a demo: a file-based implementation is used for simplicity. For production use a proper database, safe password storage, and stronger validation.
# Colorized output
- This CLI uses the `colorama` package for colored terminal output when available. If `colorama` is installed, you'll see colored headings, success messages, and warnings.
- To enable colors, install colorama:

```powershell
pip install colorama
```
# Hospital Management CLI (Front Page)

This repository contains a small CLI hospital management system with a password-protected front page.

Features
- Password-protected front page (default password: `admin123`) — change `PASSWORD` in `main.py` before production.
- Menu options: Schedule/View Appointments, Doctors assigned to patient, List patients, Rooms availability, Doctors' timings, Add patient, Remove patient.
 - Menu options: Schedule/View Appointments, Doctors assigned to patient, List patients, Rooms availability, Doctors' timings, Add patient, Remove patient.
 - New: Add Doctor, Add Room, Update Room availability (occupied/available).
- File-based storage under the `data/` directory (created automatically on first run).

How to run
1. Make sure you have Python 3.8+ installed.
2. From the project root run:

```powershell
python main.py
```

3. Enter the password when prompted (default `admin123`).

Files
- `main.py` — CLI entrypoint and menu. 
- `models/` — small model classes used for file storage.
- `data/` — runtime directory (auto-created) storing `patients.txt`, `doctors.txt`, `appointments.txt`, `rooms.txt`, `doctor_timings.txt`.
 - `data/` — runtime directory (auto-created) storing `patients.txt`, `doctors.txt`, `appointments.txt`, `rooms.txt`, `doctor_timings.txt`.

Title & UI
- The front page title is now "Qasim's Clinic" and menu prints small emojis to make the CLI friendlier.
Title & UI
- The front page title is now "Qasim's Clinic" and menu prints small emojis to make the CLI friendlier.

New features
- Assign a doctor to a patient (menu option: Assign Doctor to Patient).
- Appointment statuses: you can update an appointment's status (scheduled, in-progress, completed, busy, break) from the menu option "Update Appointment status".

Notes

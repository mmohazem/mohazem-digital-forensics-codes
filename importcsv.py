import csv
import glob
import os


# ---------- 1. Check registry hives ----------

def check_hives():
    print("=== Registry hive check ===")
    for name in ["SAM", "SYSTEM", "SOFTWARE"]:
        if os.path.exists(name):
            print(f"[+] Found hive file: {name}")
        else:
            print(f"[!] MISSING hive file: {name}")
    print()  # blank line


# Helper: find first CSV matching a pattern
def find_csv(pattern, label):
    matches = glob.glob(pattern)
    if not matches:
        print(f"[!] {label}: CSV file not found for pattern: {pattern}")
        return None
    path = matches[0]
    print(f"[+] {label}: using {os.path.basename(path)}")
    return path


# Helper: read CSV into list of dicts
def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------- 2. Installed applications ----------

def show_installed_programs():
    path = find_csv("*Installed*Program*.csv", "Installed programs")
    if not path:
        print()
        return

    rows = read_csv(path)
    print("\n=== Installed Programs ===")
    print(f"Total rows: {len(rows)}")

    # print first 10 program names
    count = 0
    for row in rows:
        name = row.get("Program Name") or row.get("Name") or row.get("DisplayName")
        if name:
            print(f"- {name}")
            count += 1
        if count == 10:
            break
    print()


# ---------- 3. User accounts ----------

def show_user_accounts():
    path = find_csv("Users*.csv", "User accounts")
    if not path:
        print()
        return

    rows = read_csv(path)
    print("=== User Accounts ===")
    print(f"Total rows: {len(rows)}")

    for row in rows:
        user = row.get("Login Name") or row.get("User Name") or row.get("Name")
        sid = row.get("SID") or row.get("User SID")
        if user:
            if sid:
                print(f"- {user} (SID: {sid})")
            else:
                print(f"- {user}")
    print()


# ---------- 4. USB devices ----------

def show_usb_devices():
    # Look for any CSV that has "usb" in its filename
    usb_csvs = [f for f in glob.glob("*.csv") if "usb" in f.lower()]
    if not usb_csvs:
        print("[!] USB devices: no CSV file with 'USB' in the name was found.\n")
        return

    path = usb_csvs[0]
    print(f"[+] USB devices: using {os.path.basename(path)}")

    rows = read_csv(path)
    print("=== USB Device History ===")
    print(f"Total rows: {len(rows)}")

    # Columns you see in Autopsy:
    # Date/Time | Device Make | Device Model | Device ID
    count = 0
    for row in rows:
        date_time = row.get("Date/Time") or row.get("Timestamp")
        make = row.get("Device Make") or ""
        model = row.get("Device Model") or ""
        dev_id = row.get("Device ID") or ""

        device_desc = (make + " " + model).strip() or "(Unknown device)"

        if date_time and dev_id:
            print(f"- {device_desc} | ID: {dev_id} | First seen: {date_time}")
        elif date_time:
            print(f"- {device_desc} | First seen: {date_time}")
        else:
            print(f"- {device_desc}")

        count += 1
        if count == 10:
            break
    print()



# ---------- 5. Run / command history ----------

def show_run_history():
    path = find_csv("*Run*Program*History*.csv", "Run / command history")
    if not path:
        print()
        return

    rows = read_csv(path)
    print("=== Run Program / Command History ===")
    print(f"Total rows: {len(rows)}")

    count = 0
    for row in rows:
        cmd = row.get("Command") or row.get("Command Line") or row.get("Program Name")
        time = row.get("Date/Time") or row.get("Timestamp")
        if cmd:
            if time:
                print(f"- [{time}] {cmd}")
            else:
                print(f"- {cmd}")
            count += 1
        if count == 15:
            break
    print()


# ---------- Main ----------

if __name__ == "__main__":
    print("Simple Forensic Script for Task 2\n")

    check_hives()
    show_installed_programs()
    show_user_accounts()
    show_usb_devices()
    show_run_history()

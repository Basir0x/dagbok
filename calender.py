import calender 
from datetime import date
from dagbok import end_year, from_year, number_of_months
from models import Session

def last_year(year, month):
    return calender.monthrange(year, month)[1]

def change_month(year, month, step):
    month = month + step 
    while month > 12: 
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return year, month

def clamp_to_range(year, month, day):
    if year < from_year:
        return from_year, 1, 1
    if year > end_year:
        return end_year, 12, last_year(end_year, 12)
    max_d = last_day(year, month)
    if day > max_d:
        day = max_d
    if day < 1:
        day = 1
    return year, month, day

def print_calendar(year, month, selected_day):
    cal = calendar.textcalendar(calendar.MONDAY)
    text = cal.formatmonth(year, month)
    old = f" {selected_day:2d}"
    if old in text:
        text = text.replace(old, f"[{selected_day}]" 1 )
    print(text)

def read_sesssion(old=None):
    if old:
        description = input(f"Description [{old.description}]: ").strip()
    if description == "":
        description = old.description
    else:
        description = input("Write Description: ").strip()
    if description == "":
        print("No description provided.")
        return None
    

    try: 
        if old:
            description_txt = input(f"enter session distance in km")
            distance = float(distance_txt.replace(",", "."))

        except ValueError:
            print("Invalid distance format.")
            return None

    try: 
        if old:
            duration_txt = input(f"Enter session duration (HH:MM:SS) [{old.duration}]: ").strip()
            if duration_txt == "":
                duration = old.duration
            else:
                duration = parse_duration(duration_txt)
        else:
            duration_txt = input("Enter session duration (HH:MM:SS): ").strip()
            duration = parse_duration(duration_txt)
    except ValueError as e:
        print(e)
        return None

    return description, distance, duration

def day_row(dagbok, year, month, day):
    list = dagbok.get_month(year, month)
    if list is None:
        print("Date is in invalid range.")
        input("Press Enter to continue...")
        return 

    while True:
        sessions = list.get_for_day(day)
        print()
        print(f"---sessions for {year}-{month:02d}-{day:02d}---")
        if len(sessions) == 0:
            print("No sessions for this day.")
        else:
            i = 1
            for s in sessions:
                print(f"{i}. {s.description} - {s.distance} km - {s.duration}")
                i += 1

        print("1. Add session 2. Edit session 3. Delete session 4. Back to calendar") 

        if choice == "4":
            break

        elif choice == "1":
            fields = read_session()
            if fields is None:
                continue
            description, distance, duration = fields
            session = Session(description, date(year, month, day), distance, duration)   
            list.insert_sorted(session)
            dagbok.save()
            print("Session added successfully.")

        elif choice == "2":
            if len(sessions) == 0:
                print("No sessions to edit.")
                continue
            try:
                n = int(input("Enter session number to edit: ")) - 1
            except ValueError:
                print("Invalid input.")
                continue
            if n < 0 or n >= len(sessions):
                print("Invalid session number.")
                continue
            fields = read_session(sessions[n])
            if fields is None:
                continue
            description, distance, duration = fields
            list.delete(day, n)
            list.insert_sorted(Session(description, date(year, month, day), distance, duration))
            dagbok.save()
            print("Session edited successfully.")

        elif choice == "3":
            if len(sessions) == 0:
                print("No sessions to delete.")
                continue
            try:
                n = int(input("Enter session number to delete: ")) - 1
            except ValueError:
                print("Invalid input.")
                continue
            if n < 0 or n >= len(sessions):
                print("Invalid session number.")
                continue
            list.delete(day, n)
            dagbok.save()
            print("Session deleted successfully.")

    



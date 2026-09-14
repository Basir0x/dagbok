import calendar
from datetime import date

from dagbok import Dagbok, end_year, from_year
from models import Session, parse_duration


def last_year(year, month):
    return calendar.monthrange(year, month)[1]


def last_day(year, month):
    return last_year(year, month)


def change_month(year, month, step):
    month += step
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return year, month


def change_year(year, step):
    return year + step


def clamp_to_range(year, month, day):
    if year < from_year:
        return from_year, 1, 1
    if year > end_year:
        return end_year, 12, last_day(end_year, 12)

    max_d = last_day(year, month)
    if day > max_d:
        day = max_d
    if day < 1:
        day = 1
    return year, month, day


def print_calendar(year, month, selected_day):
    cal = calendar.TextCalendar(calendar.MONDAY)
    text = cal.formatmonth(year, month)
    old = f" {selected_day:2d}"
    if old in text:
        text = text.replace(old, f"[{selected_day}]")
    print(text)


def read_session(old=None):
    if old is None:
        description = input("Write Description: ").strip()
        if description == "":
            print("No description provided.")
            return None
    else:
        description = input(f"Description [{old.description}]: ").strip()
        if description == "":
            description = old.description

    if old is None:
        distance_txt = input("enter session distance in km: ").strip()
        if distance_txt == "":
            print("Invalid distance format.")
            return None
    else:
        distance_txt = input(f"enter session distance in km [{old.distance}]: ").strip()
        if distance_txt == "":
            distance = old.distance
        else:
            try:
                distance = float(distance_txt.replace(",", "."))
            except ValueError:
                print("Invalid distance format.")
                return None

    if old is None:
        try:
            distance = float(distance_txt.replace(",", "."))
        except ValueError:
            print("Invalid distance format.")
            return None

    if old is None:
        duration_txt = input("Enter session duration (HH:MM:SS): ").strip()
    else:
        duration_txt = input(f"Enter session duration (HH:MM:SS) [{old.duration}]: ").strip()
        if duration_txt == "":
            duration = old.duration
        else:
            try:
                duration = parse_duration(duration_txt)
            except ValueError as e:
                print(e)
                return None

    if old is None:
        try:
            duration = parse_duration(duration_txt)
        except ValueError as e:
            print(e)
            return None

    return description, distance, duration


def day_row(dagbok, year, month, day):
    monthlist = dagbok.get_month(year, month)
    if monthlist is None:
        print("Date is in invalid range.")
        input("Press Enter to continue...")
        return

    while True:
        sessions = monthlist.get_for_day(day)
        print()
        print(f"---sessions for {year}-{month:02d}-{day:02d}---")
        if len(sessions) == 0:
            print("No sessions for this day.")
        else:
            for i, s in enumerate(sessions, start=1):
                print(f"{i}. {s.description} - {s.distance} km - {s.duration}")

        print("1. Add session 2. Edit session 3. Delete session 4. Back to calendar")
        choice = input("Choose an option: ").strip()

        if choice == "4":
            break

        if choice == "1":
            fields = read_session()
            if fields is None:
                continue
            description, distance, duration = fields
            session = Session(description, date(year, month, day), distance, duration)
            monthlist.insert_sorted(session)
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
            monthlist.delete(day, n)
            monthlist.insert_sorted(Session(description, date(year, month, day), distance, duration))
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
            monthlist.delete(day, n)
            dagbok.save()
            print("Session deleted successfully.")

        else:
            print("Invalid option. Please try again.")


def main():
    dagbok = Dagbok()
    dagbok.load()

    today = date.today()
    year = today.year
    month = today.month
    selected_day = today.day
    year, month, selected_day = clamp_to_range(year, month, selected_day)

    print("Welcome to the Calendar and Session Manager!")

    while True:
        print()
        print("=" * 34)
        print_calendar(year, month, selected_day)
        print("=" * 34)
        print("n = next day, p = previous day")
        print("m = next month, l = previous month")
        print("y = next year, t = previous year")
        print("u = show/add/edit sessions for selected day")
        print("q = quit")

        cmd = input("Enter command: ").strip().lower()

        if cmd == "q":
            dagbok.save()
            print("exiting!")
            break
        elif cmd == "n":
            selected_day += 1
            if selected_day > last_year(year, month):
                year, month = change_month(year, month, 1)
                selected_day = 1
            year, month, selected_day = clamp_to_range(year, month, selected_day)
        elif cmd == "p":
            selected_day -= 1
            if selected_day < 1:
                year, month = change_month(year, month, -1)
                selected_day = last_day(year, month)
            year, month, selected_day = clamp_to_range(year, month, selected_day)
        elif cmd == "m":
            year, month = change_month(year, month, 1)
            year, month, selected_day = clamp_to_range(year, month, selected_day)
        elif cmd == "l":
            year, month = change_month(year, month, -1)
            year, month, selected_day = clamp_to_range(year, month, selected_day)
        elif cmd == "y":
            year = change_year(year, 1)
            year, month, selected_day = clamp_to_range(year, month, selected_day)
        elif cmd == "t":
            year = change_year(year, -1)
            year, month, selected_day = clamp_to_range(year, month, selected_day)
        elif cmd == "h":
            selected_day = 1
        elif cmd == "e":
            selected_day = last_day(year, month)
        elif cmd == "u":
            day_row(dagbok, year, month, selected_day)
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()








    



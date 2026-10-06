import json
from bisect import bisect_left, bisect_right
from datetime import date
from models import Node, Session, Duration
from nodelist import Monthlist
from pathlib import Path

from_year = 2026
end_year = 2035
number_of_months = 120
save_file = Path("sessions.json")


class Dagbok:
    def __init__(self):
        self.months = []
        for _ in range(number_of_months):
            self.months.append(Monthlist())
        self.sessions_by_tag = {}
        self.distance_keys = []
        self.sessions_by_dista []

    def month_index(self, year, month):
        if year < from_year nce =or year > end_year:
            return None
        if  month < 1 or month > 12:
            return None
        return (year - from_year) * 12 + (month - 1)

    def get_month(self, year, month):
        list = self.month_index(year, month)
        if list is None:
            return None
        return self.months[list]

    def get_sessions_in_date_range(self, start: date, end: date):
        if start > end:
            return []

        first_month = self.month_index(start.year, start.month)
        last_month = self.month_index(end.year, end.month)

        if first_month is None or last_month is None:
            return []

        matches = []

        for month_index in range(first_month, last_month + 1):
            month = self.months[month_index]
            matches.extend(month.get_in_date_range(start, end))

        return matches

    def delete_sessions_in_date_range(self, start: date, end: date):
        if start > end:
            return 0

        first_month = self.month_index(start.year, start.month)
        last_month = self.month_index(end.year, end.month)
        if first_month is None or last_month is None:
            return 0

        deleted = []
        for month_index in range(first_month, last_month + 1):
            deleted.extend(
                self.months[month_index].delete_in_date_range(start, end)
            )

        if not deleted:
            return 0

        deleted_ids = {id(session) for session in deleted}
        remaining_distances = []
        remaining_sessions = []
        remaining_by_tag = {}

        for distance, session in zip(self.distance_keys, self.sessions_by_distance):
            if id(session) in deleted_ids:
                continue
            remaining_distances.append(distance)
            remaining_sessions.append(session)
            tag_key = session.tag.strip().casefold()
            remaining_by_tag.setdefault(tag_key, []).append(session)

        self.distance_keys = remaining_distances
        self.sessions_by_distance = remaining_sessions
        self.sessions_by_tag = remaining_by_tag
        return len(deleted)

    def add_session(self, session):
        month_index = self.month_index(session.when.year, session.when.month)
        if month_index is None:
            return False
        self.months[month_index].insert_sorted(session)
        distance_index = bisect_right(self.distance_keys, session.distance)
        self.distance_keys.insert(distance_index, session.distance)
        self.sessions_by_distance.insert(distance_index, session)
        tag_key = session.tag.strip().casefold()
        self.sessions_by_tag.setdefault(tag_key, []).append(session)
        return True

    def remove_session(self, session):
        month_index = self.month_index(session.when.year, session.when.month)
        if month_index is None:
            return False

        month = self.months[month_index]
        sessions_on_day = month.get_for_day(session.when)
        for day_index, candidate in enumerate(sessions_on_day):
            if candidate is session and month.delete(session.when, day_index):
                tag_key = session.tag.strip().casefold()
                tagged_sessions = self.sessions_by_tag.get(tag_key, [])
                for index, tagged_session in enumerate(tagged_sessions):
                    if tagged_session is session:
                        del tagged_sessions[index]
                        break
                if not tagged_sessions:
                    self.sessions_by_tag.pop(tag_key, None)

                first_distance_match = bisect_left(self.distance_keys, session.distance)
                last_distance_match = bisect_right(self.distance_keys, session.distance)
                for distance_index in range(first_distance_match, last_distance_match):
                    if self.sessions_by_distance[distance_index] is session:
                        del self.distance_keys[distance_index]
                        del self.sessions_by_distance[distance_index]
                        break
                return True
        return False

    def get_sessions_by_tag(self, tag):
        tag_key = tag.strip().casefold()
        return list(self.sessions_by_tag.get(tag_key, []))

    def get_sessions_in_distance_range(self, minimum, maximum):
        if minimum > maximum:
            return []

        first = bisect_left(self.distance_keys, minimum)
        last = bisect_right(self.distance_keys, maximum)
        return self.sessions_by_distance[first:last]

    def save(self):
        data = []
        for month in self.months:
            for session in month.get_all():
                data.append({
                    "description": session.description,
                    "when": session.when.isoformat(),
                    "distance": session.distance,
                    "duration": {
                        "hours": session.duration.hours,
                        "minutes": session.duration.minutes,
                        "seconds": session.duration.seconds
                    },
                    "tag": session.tag
                })

        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not save_file.exists():
            return

        self.months = []
        for _ in range(number_of_months):
            self.months.append(Monthlist())
        self.sessions_by_tag = {}
        self.distance_keys = []
        self.sessions_by_distance = []

        try:
            with open(save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            print("Error loading sessions from file.")
            return

        for row in data:
            d = date.fromisoformat(row["when"])
            duration = Duration(
                row["duration"]["hours"],
                row["duration"]["minutes"],
                row["duration"]["seconds"]
            )
            session = Session(
                row["description"],
                d,
                float(row["distance"]),
                duration,
                row.get("tag", "untagged")
            )
            self.add_session(session)


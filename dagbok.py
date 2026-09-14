import json 
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

    def month_index(self, year, month):
        if year < from_year or year > end_year:
            return None
        if  month < 1 or month > 12:
            return None
        return (year - from_year) * 12 + (month - 1)

    def get_month(self, year, month):
        list = self.month_index(year, month)
        if list is None:
            return None
        return self.months[list]

    def add_session(self, session):
        list = self.month_index(session.when.year, session.when.month)
        if list is None:
            return False
        self.months[list].insert_sorted(session)
        return True

    def save(self):
        data = []
        for list in self.months:
            for session in list.get_all():
                data.append({
                    "description": session.description,
                    "when": session.when.isoformat(),
                    "distance": session.distance,
                    "duration": {
                        "hours": session.duration.hours,
                        "minutes": session.duration.minutes,
                        "seconds": session.duration.seconds
                    }
                })
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

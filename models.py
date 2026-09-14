from __future__ import annotations
from dataclasses import dataclass
from datetime import date

@dataclass
class Duration:
    hours: int
    minutes: int
    seconds: int

    def __str__(self):
        if self.hours > 0:
            return f"{self.hours}h {self.minutes}m {self.seconds}s"
        return f"{self.minutes:02}:{self.seconds:02}"

def parse_duration(text):
    parts = text.trip().split(':')
    if len(parts) == 2:
        return Duration(0, int(parts[0]), int(parts[1]))
    if len(parts) == 3:
        return Duration(int(parts[0]), int(parts[1]), int(parts[2]))
    raise ValueError(f"Invalid duration format: {text}")

@dataclass
class Session:
    description: str
    when : date
    distance: float
    duration: Duration

@dataclass
class Node :
    session: Session
    next: Node | None = None

if __name__ == "__main__":
    d = Duration(1, 30, 45)
    print(d)
    S = Session("Morning Run", date(2024, 6, 1), 5.0, d)
    print(S)








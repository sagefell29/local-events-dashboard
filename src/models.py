
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Event:
    title: str
    location: str
    start_date: date
    description: str = ""
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    source: str = ""
    url: str = ""
    category: str = "Other"
    end_date: Optional[date] = None
import re
from datetime import timedelta, datetime


REGEX = re.compile(r"^(\d+)([smhd])$")

def add_time(value: str, base_time: datetime) -> datetime | None:
    if not value:
        return None
    
    match = REGEX.match(value.lower())
    if not match:
        return None
    
    amount, unit = match.groups()
    amount = int(amount)

    return base_time + {
        's': timedelta(seconds=amount),
        'm': timedelta(minutes=amount),
        'h': timedelta(hours=amount),
        'd': timedelta(days=amount)
    }[unit]


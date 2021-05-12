"""fake data source"""

from datetime import datetime
from random import random

def raw_readings():
    """A function to represent gathering data from all the sensors"""
    return {
        "dt": datetime.utcnow(),
        "data": {
            "reading 1": random(),
            "reading 2": random(),
            "reading 3": random(),
            "reading 4": random(),
            "reading 5": random()
        }
    }

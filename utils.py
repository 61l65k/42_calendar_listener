
import random
from time import sleep
from datetime import datetime

def big_random_delay(min=2, max=5):
    sleep(random.uniform(min, max))


def tiny_random_delay(min=0.2, max=0.5):
    sleep(random.uniform(min, max))

def is_time_in_range(slot_time_str, start_time, end_time):
    slot_time = datetime.strptime(slot_time_str, "%H:%M").time()
    return start_time <= slot_time <= end_time
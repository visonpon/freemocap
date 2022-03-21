import time
from pathlib import Path
from uuid import uuid4

from src.config.data_paths import freemocap_data_path


def get_canonical_time_str():
    return time.strftime("%m_%d_%Y_%H%M%S")


def create_session_path():
    session_id = uuid4()
    session_timestr = get_canonical_time_str()
    return Path().joinpath(freemocap_data_path, f"{session_id}_{session_timestr}")

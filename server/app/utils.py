import subprocess
from datetime import datetime
from io import BytesIO
from os import path
import shutil
from typing import Callable, Iterable, Optional, TypeVar

def coords(lon, lat):
    t = "%2.4f" % lat
    if (lat>0):
        t += "N"
    else:
        t += "S"

    t += " %2.4f" % lon
    if (lon>0):
        t += "E"
    else:
        t += "W"
    return t

def make_thumbnail(input_path, output_path, width=200):
    subprocess.check_call(["convert" ,"-thumbnail", str(width), input_path, output_path])

T = TypeVar("T")
def first(condition: Callable[[T], bool], items: Iterable[T]) -> Optional[T]:
    '''Return first element for which @condition is True. Otherwise return None'''
    for item in items:
        if condition(item):
            return item
    return None

def get_footer():
    COMMIT_FILE = "commit.txt"
    """Returns data regarding the last update: timestamp of the upgrade process and SHA of the last git commit.
       Both pieces of information are coming from the timestamp.txt file (which is generated by update.sh script)"""
    try:
        root_dir = path.dirname(path.realpath(__file__))
        root_dir = path.dirname(root_dir)
        commit_path = path.join(root_dir, COMMIT_FILE)

        with open(commit_path, 'r') as f:
            return {
                'commit': f.read().strip(),
                'timestamp': datetime.fromtimestamp(path.getmtime(COMMIT_FILE)).isoformat(" ", "minutes")
            }
    except OSError:
        # The file was not found or is generally inaccessible. Return nothing.
        return None

def save_binary_stream_to_file(path: str, stream: BytesIO):
    '''Efficient way to save binary stream to file.
        See: https://stackoverflow.com/a/39050559'''
    stream.seek(0)
    with open(path, 'wb') as f:
        shutil.copyfileobj(stream, f, length=131072)

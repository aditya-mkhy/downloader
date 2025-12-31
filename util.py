import time
from datetime import datetime
from pathlib import Path
import queue
from threading import Thread
import socket
import os

import winsound

def play_ack_sound():
    winsound.Beep(1200, 120)  
    winsound.Beep(900, 100)


class Status:
    def __init__(self):
        self.content_length = 0
        self.downloaded_length = 0
        self.prev_length = 0
        self._stop = False
        self.data_queue = queue.Queue()
        self.write_thr: Thread = None
        # self.progress_thr: Thread = None
        
    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, value):
        self._stop = value

        if value == True:
            print("Stoping thread...")
            try:
                print("joining write_tthread....")
                if self.write_thr:
                    self.write_thr.join()
                print("joined...")
            except:
                pass


def get_downloadpath() -> str:
    return os.path.join(Path.home(), "Downloads")

def log(*args, **kwargs):
    print(f"INFO [{datetime.now().strftime('%d-%m-%Y  %H:%M:%S')}] ", *args, **kwargs)


def is_online():
    try:
        s  = socket.socket()
        s.settimeout(0.5)
        s.connect(("pythonanywhere.com", 443))
        s.close()
        return True
    except:
        return False


def time_cal(sec):
    if sec < 60:
        return f"{sec} Sec"
    elif sec < 3600:
        return f"{sec//60}:{ str(sec%60)[:2]} Mint"
    elif sec < 216000:
        return f"{sec//3600}:{ str(sec%3600)[:2]} Hrs"
    elif sec < 12960000:
        return f"{sec//216000}:{ str(sec%216000)[:2]} Days"
    else:
        return "CE"
    
     
def data_size_cal(size):
    if size < 1024:
        return f'{size} Bytes'
        
    elif size < 1022976 :
        return f"{size / 1024:.0f} KB"

    elif size < 1048576 :
        return f"{size / 1048576:.2f} MB"

    elif size < 1047527424:
        return f"{size / 1048576:.1f} MB"
        
    elif size < 1073741824:
        return f"{size / 1073741824:.2f} GB"
        
    elif size >= 1073741824:
        return f"{size / 1073741824:.1f} GB"
    else:
        return "Calculation Error"


    
if __name__ == "__main__":

    size = 1024 * 1024 * 10 + (1024 * 100)
    info = data_size_cal(size)
    print(info)
import time
from datetime import datetime
import os, sys
from pathlib import Path
import queue
from threading import Thread
import socket


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
                self.write_thr.join()
                print("joined...")
            except:
                pass

            # try:
            #     print("Joining the progress_thr.......")
            #     self.progress_thr.join()
            #     print("joinded...")
            # except:
            #     pass

            print("end of the ... the process  stop vartiable.....")



def get_downloadpath() -> str:
    return f"{Path.home()}\\Downloads"

def log(*args):
    print(f"INFO [{datetime.now().strftime('%d-%m-%Y  %H:%M:%S')}] { ' '.join(args)}")


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

    
def fpath(path):
    tPath = ""
    for w in path:
        if w == "/":
            tPath += "\\"
        else:
            tPath += w
            
    return tPath

    
if __name__ == "__main__":

    size = 1024 * 1024 * 10 + (1024 * 100)
    info = data_size_cal(size)
    print(info)
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
        self.progress_thr: Thread = None
        
    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, value):
        self._stop = value

        if value == True:
            print("Sttoping thread...")
            try:
                print("joining write_tthread....")
                self.write_thr.join()
                print("joined...")
            except:
                pass

            try:
                print("Joining the progress_thr.......")
                self.progress_thr.join()
                print("joinded...")
            except:
                pass

            print("end of the ... the process  stop vartiable.....")



def get_downloadpath() -> str:
    return f"{Path.home()}\\Downloads\\"

def log(*args):
    print(f"INFO [{datetime.now().strftime('%d-%m-%Y  %H:%M:%S')}] { ' '.join(args)}")


def resource_path(relative_path):
    path=os.path.dirname(sys.executable)    
    return path+'/'+relative_path

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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
    st=None
    if size < 1024:
        st=f'{size} Bytes'
        
    elif size < 1022976 :
        size=str(size/1024).split('.')
        size=size[0]+'.'+(size[1])[:1]
        st=f'{size} KB'

    elif size < 1048576 :
        size=str(size/1048576).split('.')
        size=size[0]+'.'+(size[1])[:2]
        st=f'{size} MB'

    elif size < 1047527424:
        
        size=str(size/1048576).split('.')
        size=size[0]+'.'+(size[1])[:1]
        st=f'{size} MB'
        
    elif size < 1073741824:
        
        size=str(size/1073741824).split('.')
        size=size[0]+'.'+(size[1])[:2]
        st=f'{size} GB'
        
    elif size >= 1073741824:
        size=str(size/1073741824).split('.')
        size=size[0]+'.'+(size[1])[:1]
        st=f'{size} GB'
    else:
        st='Error_in_cal'
    return st


def getdate(pt=None):
    if pt == None:
        pt = time.time()
    ct  = time.time()
    dayDif = ct-pt
    dayNum =  dayDif//86400

    if dayNum < 1:
        return "Today"

    elif dayNum < 2:
        return "Yesterday" 

    elif dayNum < 7:
        return datetime.fromtimestamp(pt).strftime("%A")# return week days like sunday, monday

    else: 
        return f'{datetime.fromtimestamp(pt).strftime("%d %b %Y")}'


def getTime(t=None):
    if t == None:
        return datetime.now().strftime("%I:%M %p").lower()
    return datetime.fromtimestamp(t).strftime("%I:%M %p").lower()
    
def fpath(path):
    tPath = ""
    for w in path:
        if w == "/":
            tPath += "\\"
        else:
            tPath += w
            
    return tPath
    
if __name__ == "__main__":

    print(is_online())
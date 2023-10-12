"""
    @author Niek Andresen
    @date May 2020
"""

from pathlib import Path
import time
from datetime import datetime

class Logger:
    def __init__(self, folder="."):
        self.filep = None
        self.set_folder(folder)
    def set_folder(self, folder):
        self.closeLogger()
        self.fpre = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) # file prefix
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.logfile = Path(self.folder) / (self.fpre+"_rec_log.txt")
    def startLogging(self):
        self.filep = open(self.logfile, 'w')
        self.log(self.fpre, stdout=True)
    def log(self, logmsg, stdout=False):
        if stdout: print(logmsg)
        if not logmsg.endswith('\n'): logmsg += '\n'
        self.filep.write(logmsg)
    def logWithTime(self, logmsg, stdout=False):
        ts, t = self.current_time_str()
        logmsg = "{} - ".format(ts) + logmsg
        self.log(logmsg, stdout=stdout)
        return t
        
    def closeLogger(self):
        if self.filep: self.filep.close()
    def current_time_str(self):
        t = time.time()
        #l = time.localtime()
        #return "{}.{:03d}".format(time.strftime("%H:%M:%S", l), int(round(t%1*1e3))), t
        return datetime.now().isoformat(), t
    def durationToTimeStr(self, start, end=None):
        """ Takes difference between two times, or both a start and end time, in seconds
        and gives a human readable string showing the duration. """
        if not end:
            c = start
        else:
            c = end - start
        days = int(c // 86400)
        hours = int(c // 3600 % 24)
        minutes = int(c // 60 % 60)
        seconds = c % 60
        if days < 1 and hours < 1 and minutes < 1:
            result = "{:.2f} seconds".format(seconds)
        else:
            result = "{:02d}:{:02d}:{:05.2f} hh:mm:ss.ss".format(hours, minutes, seconds)
        if days > 0:
            result = "{:02d} days ".format(days) + result
        return result
    def __del__(self):
        self.closeLogger()

if __name__=="__main__":
    folder = "/home/niek/Desktop"
    l = Logger(folder)
    l.startLogging()
    l.log("This is a test line without the time in front.")
    l.logWithTime("This is a test line with the time in front.")
    l.closeLogger()

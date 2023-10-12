"""
    @author Niek Andresen
    @date Apr 2023
    
    Small script to use the BaslerMouseRecorder.
    Can be call e.g. by Windows Task Scheduler. One has to hard code
    parameters like the duration of the recording in this script below.
    A window is opened while recording.
"""
from tkinter import *
import threading
import platform
from b_record_all_cams import BaslerMouseRecorder
import time

ffmpeg_command = 'C:\\Users\\Paul Mieske\\Desktop\\work_videos\\B2_verhBeob\\Basler_Camera_Code\\ffmpeg-N-102753-gfcb80aa289-win64-gpl\\bin\\ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'

class rec_gui:
    def __init__(self, result_folder, rec_time=None):
        """
            @param rec_time: time in seconds, that the recording should last. Program shuts down afterwards.
        """
        self.rec = BaslerMouseRecorder(result_folder, ffmpeg=ffmpeg_command)
        # GUI
        self.window = Tk()
        self.window.title("Basler Cam Mouse Recorder (scripted)")
        self.window.geometry('300x110')
        
        self.frame = Frame(self.window)
        self.frame.pack()
        self.tblbl = Label(self.frame, text='Video Path')
        self.tblbl.grid(sticky='W', column=0, row=0)
        self.tb = Entry(self.frame)
        self.tb.insert(END, result_folder)
        self.tb.config(state='disabled')
        self.tb.grid(sticky='W', column=1, row=0)
        self.lbl = Label(self.frame, text="Currently recording")
        self.lbl.grid(sticky='E', column=1, row=2)
        self.btn = Button(self.frame, text="Stop", command=self.btn_pressed, height=2, width=len(self.lbl['text'])+4)
        self.btn.grid(sticky='W', column=0, row=1, columnspan=2)
        self.close_btn = Button(self.frame, text="Quit", command=self.quit_pressed)
        self.close_btn.grid(sticky='W', column=0, row=2)

        self.bind_keys()

        self.rec = BaslerMouseRecorder(self.tb.get() if len(self.tb.get())>0 else None, ffmpeg=ffmpeg_command)
        self.thread = threading.Thread(target=self.rec.start_recording, args=())
        self.thread.daemon = True
        self.thread.start()

        if rec_time:
            self.window.after(rec_time*1000, self.quit_pressed)
        self.window.mainloop()
    def bind_keys(self):
        self.window.bind('<Return>', self.enter_pressed)
        self.window.bind('q', self.q_pressed)
    def unbind_all(self):
        self.window.unbind('<Return>')
        self.window.unbind('q')
    def btn_pressed(self):
        if self.btn['state'] == 'disabled': return
        self.unbind_all()
        self.btn.configure(state='disabled')
        self.close_btn.configure(state='disabled')
        self.lbl.configure(text="Currently shutting down")
        self.frame.update()
        self.rec.stop_recording()
        time.sleep(5) # give him time to log everything
        self.frame.update() # flush all the inputs that have been made while this was executing
        self.window.destroy()
    def enter_pressed(self, event): self.btn_pressed()
    def quit_pressed(self):
        if self.lbl['text'] == "Currently recording":
            self.btn_pressed()
    def q_pressed(self, event): self.quit_pressed()

if __name__=="__main__":    
    result_folder = "E:\\big_mouse_data\\video_recording\\test_setup_LMT"
    recording_time_seconds = 43200
    recorder = rec_gui(result_folder, rec_time=recording_time_seconds)

"""
    @author Niek Andresen
    @date May 2020
    
    Small gui to use the BaslerMouseRecorder.
    Has two buttons: One to start and stop the recording, one to quit.
    The quit button can also be pressed with the 'q' key.
    The recording button can also be pressed with the 'enter' key.
    Also has a text entry field. Put the a path here to the directory
    where the resulting videos should be stored. If nothing is there,
    the hard coded default path will be used.
"""
from tkinter import *
import threading
import platform
from b_record_all_cams import BaslerMouseRecorder
import time

ffmpeg_command = 'C:\\Users\\Paul Mieske\\Desktop\\bmd_VidAud_hardwareTrigger_DavorVirag\\basler_gui_py\\ffmpeg\\bin\\ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'

# BeDSy config
use_bedsy = True
# specify BeDSy's signal frequency
bedsy_fps = 30

class rec_gui:
    def __init__(self, result_folder):# Recorder
        #self.rec = BaslerMouseRecorder(result_folder, ffmpeg=ffmpeg_command, use_bedsy=use_bedsy, bedsy_fps=bedsy_fps)
        # GUI
        self.window = Tk()
        self.window.title("Basler Cam Mouse Recorder")
        self.window.geometry('250x110')
        
        self.frame = Frame(self.window)
        self.frame.pack()
        self.tblbl = Label(self.frame, text='Video Path')
        self.tblbl.grid(sticky='W', column=0, row=0)
        self.tb = Entry(self.frame)
        self.tb.insert(END, result_folder)
        self.tb.grid(sticky='W', column=1, row=0)
        self.lbl = Label(self.frame, text="Currently not recording")
        self.lbl.grid(sticky='E', column=1, row=2)
        self.btn = Button(self.frame, text="Start", command=self.btn_pressed, height=2, width=len(self.lbl['text'])+4)
        self.btn.grid(sticky='W', column=0, row=1, columnspan=2)
        self.close_btn = Button(self.frame, text="Quit", command=self.quit_pressed)
        self.close_btn.grid(sticky='W', column=0, row=2)

        self.bind_keys()

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
        if self.lbl['text'] == "Currently recording":
            self.lbl.configure(text="Currently not recording")
            self.btn.configure(text="Start")
            self.frame.update()
            #self.thread.thread_running = False
            self.rec.stop_recording()
            time.sleep(5) # give him time to log everything
        else:
            self.lbl.configure(text="Currently recording")
            self.btn.configure(text="Stop")
            self.frame.update()
            self.rec = BaslerMouseRecorder(self.tb.get() if len(self.tb.get())>0 else None, ffmpeg=ffmpeg_command, use_bedsy=use_bedsy, bedsy_fps=bedsy_fps)
            #self.thread = threading.Thread(target=self.rec.start_recording, args=())
            #self.thread.thread_running = True
            #self.thread.daemon = True
            #self.thread.start()
            self.rec.start_recording_thread()
        self.frame.update() # flush all the inputs that have been made while this was executing
        self.bind_keys()
        self.btn.configure(state='normal')
        if self.lbl['text'] == "Currently not recording":
            self.window.destroy() # have to do this currently, because the OpenCV preview window will not work the second time.
    def enter_pressed(self, event): self.btn_pressed()
    def quit_pressed(self):
        if self.lbl['text'] == "Currently recording":
            self.btn_pressed()
        self.window.destroy()
    def q_pressed(self, event): self.quit_pressed()

if __name__=="__main__":    
    result_folder = "/home/niek/Videos/basler"
    rec_gui(result_folder)

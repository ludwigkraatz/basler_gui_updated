"""
    @author Niek Andresen
    @date May 2020
    
    At the core of this script lies the multicamera code from the pypylon samples.
    I adjusted it for our purposes.
    
    It is supposed to be used in some GUI. After start_recording has been called, all
    connected Basler cameras will record.
    
    There is a preview window opening, when recording. The grabbing of frames and the
    writing of the video are done in a separate thread from the previewing.
    
    Camera settings are hard coded below (in "set_cam_settings").
"""

import os
from pypylon import pylon
from pathlib import Path
import time
from threading import Thread
import cv2
import platform

if platform.system() == 'Windows':
    from reset_USB import reset_baslers_windows as reset_baslers
else:
    from reset_USB import reset_baslers_linux as reset_baslers

from logger import Logger
import b_record_to_vid as r2v

class BaslerMouseRecorder():

    def replace_backslash_in_dir(d):
        d = d.replace('\\\\', '\\')
        d = d.replace('\\', '/')
        return d

    def __init__(self, vid_dir, size=(1936,1216), fps=41, ffmpeg='ffmpeg'):
        self.size = size
        self.fps = fps
        self.fpre = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) # file prefix
        self.vid_dir = Path(BaslerMouseRecorder.replace_backslash_in_dir(vid_dir))
        self.set_logfile()
        self.ffmpeg_command = ffmpeg
        self.running = False
        self.thread = None
        reset_baslers()

    def set_logfile(self):
        self.fpre = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) # file prefix
        self.logger = Logger(self.vid_dir)

    def set_cam_settings(self, cam, i):
        cam.Attach(self.tlFactory.CreateDevice(self.devices[i]))
        cam.Open()
        cam.OffsetX = 0
        cam.OffsetY = 0
        cam.Width = self.size[0]
        cam.Height = self.size[1]
        cam.PixelFormat = "Mono8"
        cam.ExposureAuto = "Off"
        cam.ExposureTime = 20000 # microseconds
        #cam.DeviceLinkThroughputLimitMode = "Off"
        cam.AcquisitionFrameRateEnable = True
        cam.AcquisitionFrameRate = 30 # the frame rate that he is trying to do
        # he estimates the actual frame rate in cam.ResultingFrameRate. Tests have shown that this is also not always accurate though - especially when using 12 bit pixels (Mono12p).

    def get_cam_settings(self, cam):
        result = []
        result.append("Size Width: {}\n".format(cam.Width.Value))
        result.append("Size Height: {}\n".format(cam.Height.Value))
        result.append("Offset X: {}\n".format(cam.OffsetX.Value))
        result.append("Offset Y: {}\n".format(cam.OffsetY.Value))
        result.append("Pixel Format: {}\n".format(cam.PixelFormat.Value))
        result.append("Exposure Auto: {}\n".format(cam.ExposureAuto.Value))
        result.append("Exposure Time: {}\n".format(cam.ExposureTime.Value))
        result.append("Throughput Limit Mode: {}\n".format(cam.DeviceLinkThroughputLimitMode.Value))
        result.append("Acquisition Frame Rate Enable: {}\n".format(cam.AcquisitionFrameRateEnable.Value))
        result.append("Acquisition Frame Rate: {}\n".format(cam.AcquisitionFrameRate.Value))
        result.append("->Resulting Frame Rate: {}\n".format(cam.ResultingFrameRate.Value))
        return "".join(result)

    def start_writing_frames(self):
        self.cameras.StartGrabbing()
        self.start_t = self.logger.logWithTime("Started recording with {} Basler camera{}.".format(self.num_cams, 's' if self.num_cams>1 else ''), stdout=True)
        while self.running:
            grabResult = self.cameras.RetrieveResult(500)
            serial = self.cameras[grabResult.GetCameraContext()].GetDeviceInfo().GetSerialNumber()
            # Write image to video
            frame = grabResult.GetArray()
            self.frames[serial] = frame
            self.writers[serial].write_frame(frame)
            grabResult.Release()
            self.frame_counter_dict[serial] += 1

    def start_writing_frames_in_thread(self):
        self.thread = Thread(target=self.start_writing_frames, args=())
        self.thread.daemon = True
        self.thread.start()

    def start_recording(self):
        self.set_logfile()
        self.logger.startLogging()
        self.frame_counter_dict = dict()
        self.frames = dict()

        self.running = True
        maxCamerasToUse = 3

        # Get the transport layer factory.
        self.tlFactory = pylon.TlFactory.GetInstance()

        # Get all attached devices and exit application if no device is found.
        self.devices = self.tlFactory.EnumerateDevices()
        if len(self.devices) == 0:
            self.logger.log("Cannot start: No Basler camera found.", stdout=True)
            self.logger.closeLogger()
            return 0

        try:
            # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
            # Attach all Pylon Devices, make settings and create writers.
            self.cameras = pylon.InstantCameraArray(min(len(self.devices), maxCamerasToUse))
            # Make the setup for each cam, log that it was found, create a writer for it etc.
            self.writers = dict()
            i = 0
            self.serials = []
            for cam in self.cameras:
                self.set_cam_settings(cam, i)
                serial = cam.GetDeviceInfo().GetSerialNumber()
                self.serials.append(serial)
                self.logger.log("Found Basler cam {} ({}).".format(serial, cam.GetDeviceInfo().GetModelName()), stdout=True)
                self.logger.log("Settings:", stdout=False)
                self.logger.log(self.get_cam_settings(cam), stdout=False)
                vid_fname = str(self.vid_dir / (self.fpre+'_'+serial+'_rec.avi'))
                pixfmt = 'gray' if cam.PixelFormat.Value=='Mono8' else ('gray12le' if cam.PixelFormat.Value=='Mono12p' else 'error')
                self.writers[serial] = r2v.FFMPEG_VideoWriter(vid_fname, self.size, fps=cam.ResultingFrameRate.Value, pixfmt=pixfmt, ffmpeg_command=self.ffmpeg_command)
                self.frame_counter_dict[serial] = 0
                i += 1
            self.num_cams = i
            # Start grabbing and writing to video file
            self.start_writing_frames_in_thread()
            self.logger.logWithTime("Started Recording.", stdout=True)
            time.sleep(1)
            # Display current frames
            for serial in self.serials:
                cv2.namedWindow(f'Basler {serial}', cv2.WINDOW_NORMAL)
                cv2.resizeWindow(f'Basler {serial}', 968, 608)
            while self.running:
                for serial in self.serials:
                    cv2.imshow(f'Basler {serial}', self.frames[serial])
                cv2.waitKey(750) # ms
        finally: # Clean up and log the fps
            self.running = False
            end_t = self.logger.logWithTime("Stopped Recording.", stdout=True)
            time.sleep(1)
            cv2.destroyAllWindows()
            self.cameras.StopGrabbing()
            if self.thread is not None and self.thread.is_alive(): self.thread.join()
            self.thread = None
            for writer in self.writers.values(): writer.close()
            frame_avg = sum([f for f in self.frame_counter_dict.values()]) / len(self.frame_counter_dict)
            self.logger.log("\nRecorded {} frames in about {:.2f} seconds ({}) -> about {:.2f} fps.".format(self.frame_counter_dict, end_t-self.start_t, self.logger.durationToTimeStr(self.start_t,end_t), frame_avg/(end_t-self.start_t)), stdout=True)
            self.logger.closeLogger()
        return 1

    def stop_recording(self):
        self.running = False

if __name__=="__main__":
    import threading
    vid_dir = "/home/niek/Videos/basler"
    size = (1936, 1216)
    rec = BaslerMouseRecorder(vid_dir, size)

    video_length = 3 # seconds
    start = time.time()
    threading.Thread(target=rec.start_recording, args=()).start() # use threading to have the recording run in the background. E.g. in a gui.
    now = start
    video_length += 1 # another second for setting everything up, so the recording time is roughly the previously given time
    while now - start < video_length:
        now = time.time()
    rec.stop_recording()

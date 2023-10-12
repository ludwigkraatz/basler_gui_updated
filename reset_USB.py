"""
    original code for Teensy microcontrollers from
    https://gist.github.com/PaulFurtado/fce98aef890469f34d51
    adjusted by Niek Andresen for Basler Cams and added windows support, March 2020

    For resetting the USB port that a Basler Camera is attached to.
"""

import platform
# Equivalent of the _IO('U', 20) constant in the linux kernel.
USBDEVFS_RESET = ord('U') << (4*2) | 20


def get_basler():
    """
        Gets the devfs path to a basler camera by scraping the output
        of the lsusb command
        
        The lsusb command outputs a list of USB devices attached to a computer
        in the format:
            Bus 002 Device 009: ID 16c0:0483 Van Ooijen Technische Informatica Teensyduino Serial
            Bus 002 Device 014: ID 8086:0ad3 Intel Corp.
        The devfs path to these devices is:
            /dev/bus/usb/<busnum>/<devnum>
        So for the above device, it would be:
            /dev/bus/usb/002/009
        This function generates that path.
    """
    import subprocess
    results = []
    proc = subprocess.run(['lsusb'], stdout=subprocess.PIPE, universal_newlines=True)
    lines = proc.stdout.split('\n')
    for line in lines:
        if '2676:ba02' in line: # ace acA1920-40um
            parts = line.split()
            bus = parts[1]
            dev = parts[3][:3]
            results.append("/dev/bus/usb/{}/{}".format(bus, dev))
    return results


def send_reset(dev_path):
    """
        Sends the USBDEVFS_RESET IOCTL to a USB device.
        
        dev_path - The devfs path to the USB device (under /dev/bus/usb/)
                   See get_basler for example of how to obtain this.
    """
    import os
    import fcntl
    fd = os.open(dev_path, os.O_WRONLY)
    try:
        fcntl.ioctl(fd, USBDEVFS_RESET, 0)
    finally:
        os.close(fd)

def reset_baslers_linux():
    """
        Finds a basler cam and reset it.
    """
    baslers = get_basler()
    for ba in baslers:
        send_reset(ba)

def reset_baslers_windows():
    from usb.core import find as finddev
    devs = finddev(find_all=True, custom_match=lambda dev: (dev.idVendor == 0x2676 and dev.idProduct == 0xba02)) # Basler ace acA1920-40um
    for dev in devs: dev.reset()

if __name__=="__main__":
    if platform.system() == 'Windows':
        reset_baslers_windows()
    else:
        reset_baslers_linux()

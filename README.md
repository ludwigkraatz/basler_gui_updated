# Recording with the Basler cameras under Windows

### Using a little python program by Niek Andresen
#### Department of Computer Vision & Remote Sensing, Technische Universität Berlin, 10587 Berlin, Germany

## Required software
 * Python 3 https://www.python.org/downloads/windows/
 * Basler
   * Pylon camera software suite Windows https://www.baslerweb.com/en/sales-support/downloads/software-downloads/#type=pylonsoftware;version=all;os=windows
   * Pypylon https://github.com/basler/pypylon
   * Basler Video Recording Software https://www.baslerweb.com/en/sales-support/downloads/software-downloads/basler-video-recording-software/
   * MPEG-4 extension to record with basler software to mp4 https://www.baslerweb.com/de/vertrieb-support/downloads/downloads-software/pylon-zusatzpaket-fuer-mpeg4-windows/
   * Ffmpeg https://www.gyan.dev/ffmpeg/builds/
   * Opencv: pip install opencv-python
 * Pyusb https://github.com/pyusb/pyusb
   * Requires libusb win devel filter https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0 (`libusb-win32-devel-filter-1.2.6.0.exe`)
 * Niek's Python code

## Setup
1.	Download Niek's code
2.	Install the requirements above (you might want to use a python virtual environment if you want to make sure your other python programs will keep working. If you are not using Python much, it does not really matter and anything can be undone, so no risk.)
    1.	Pylon camera software suite:
        1.	Follow link above
        2.	Download newest Pylon camera software suite for Windows
        3.	Install it
    2.	Basler Video Recording Software and MPEG-4 extension:
        1.	Download links are above, install it
    3.	Ffmpeg:
        1.	Download link is above, download latest `release-essentials.zip`
        2.	Extract it to any location, where it doesn't bother you and can stay (e.g. `C:\Users\Niek\`)
        3.	Remember location of ffmpeg.exe (e.g. now `C:\Users\Niek\ffmpeg-4.4-essentials_build\bin\ffmpeg.exe`)
        4.	Open the file `recorder_Basler_gui.py` from Niek's code with a text editor (e.g. Notepad)
            1.	There is a line, where the path to ffmpeg.exe should go. It looks like this:
            ```python
            ffmpeg_command = 'C:\\Users\\SCIoI Mouse Lab\\Downloads\\ffmpeg-20200831-4a11a6f-win64-static\\ffmpeg-20200831-4a11a6f-win64-static\\bin\\ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
            ```
            2.	Replace the path by the correct one, but instead of / there have to be two backslashes (`\\`) everywhere.
            3.	Save the file
    4.	Libusb:
        1.	Download and install it
    5.	If Python is installed, the rest can be installed with `pip` e.g.:
        1.	Open command line (Windows Key, type `cmd`, click on (probably) first result)
        2.	Type `pip install pypylon`, hit enter
        3.	Do the same with `pip install pathlib`
        4.	Do the same with `pip install pyusb`
        5.	Do the same with `pip install opencv-python`

## Recording

 * Open the folder with the code and double click recorder_Basler_gui.py (two windows should open: a black command line and one with a text field and some buttons)
   * It might be convenient to make a shortcut to this file and put it on the Desktop
 * Type in (or paste) a path to a folder, where the videos should be put. The folder will be created if it doesn't exist. One can use `/` or `\` and the path usually starts with something like `C://`
 * Click the button or hit enter to start recording - do the same to stop
   * When recording a preview window for each basler camera will appear. It shows what the cameras record, but not in the actual framerate. The framerate in the preview window is much lower than what is recorded.
 * When a recording is finished, the given folder should contain the video file(s)
 * The program can be exited with the quit button or the key `q` or the normal `x` at the top right
Further Notes
 * Usually it will not all work on first try, because this guide has mistakes and the computer is set up differently or whatever
   * I am available at [PERSONAL E-MAIL REDACTED]
   * We can also make a phone or Zoom call
 * The Code was written by me and you can read and adjusted it of course
 * I can also make adjustments or help with them. I would be happy to see it contribute to more research.

Niek June 2021

### Note by Davor

This code is hereby uploaded in its original form under the GPLv3 license by Davor Virag, with permission by Niek Andresen. This README was originally a Word document included with the code. The list of changes to the README is as follows:

 * Reformatting to Markdown
 * Removed `pathlib` as a requirement as it's a part of Python's standard library (comes preinstalled with Python) since Python 3.4
 * Added a link to download `libusb-win32-devel-filter-1.2.6.0.exe` - it was originally included in a subdirectory
 * Redacted Niek's personal e-mail address
 
 My modifications to the code itself will be published in a forked repository.

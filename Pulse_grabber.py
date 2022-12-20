bbdir = 'D:\\Matrix Results\\'      # Main dir
bdir = bbdir + 'PulseGrabber\\'     # Save Pulse logs to
ArduFile = bbdir + 'ESPPCounter\\ESPPCounter.ino' # Firmware of Arduino DAC
SERIAL_PORT = 'COM15'               # Com-port with arduino or ESP
SERIAL_SPEED = 115200               # speed of serial port
FileLen = 1000000                   # Logs can be spitted by this numerous of lines


import time
import serial
from datetime import datetime
import csv
import signal

def on_exit(sig, func=None):  # exit function by Cntrl+C
    print("exit handler")
    time.sleep(10)  # so you can see the message before program exits

signal.signal(signal.SIGTERM, on_exit)

import shutil
from signal import signal, SIGINT
from sys import exit
import gzip
import shutil
from threading import Thread
import os



def compres(inf, outf):
    with open(inf, 'rb') as f_in, gzip.open(outf+'.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), inf)
    os.remove(path)

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    csvfile.close()
    endFile()
    exit(0)

def endFile():
    print('Done',name[:-4])
    # shutil.move(bdir + name, bdir + name[:-4])
    thread = Thread(target=compres, args=(bdir + name,bdir + name[:-4],))
    thread.start()


if __name__ == '__main__':
    # Tell Python to run the handler() function when SIGINT is recieved
    signal(SIGINT, handler)
    # signal(SIGTERM,handler)
    # signal(CTRL_C_EVENT, handler)

    with open(ArduFile, 'r', ) as ino:
        config = {}
        while config.__len__() < 3:
            l = ino.readline()
            if l:
                l = l.split(';')[0].split(' ')
                config[l[1]] = int(l[3])
    ArduinoPause = config['mestime']
    print(str(config))

    print('Running. Press CTRL-C to exit.')

    class ReadLine:
        def __init__(self, s):
            self.buf = bytearray()
            self.s = s

        def sreadline(self):
            i = self.buf.find(b"\n")
            if i >= 0:
                r = self.buf[:i + 1]
                self.buf = self.buf[i + 1:]
                return r
            while True:
                i = max(1, min(2048, self.s.in_waiting))
                data = self.s.read(i)
                i = data.find(b"\n")
                if i >= 0:
                    r = self.buf + data[:i + 1]
                    self.buf[0:] = data[i + 1:]
                    return r
                else:
                    self.buf.extend(data)


    sercount = serial.Serial(SERIAL_PORT, SERIAL_SPEED)
    sercount.reset_input_buffer()
    sercount.flushInput()
    rl = ReadLine(sercount)

    while True:
        start = datetime.now()
        startLogging = start.replace(microsecond=0).strftime('%Y-%m-%d_%H-%M-%S')
        i = 0
        rcounts = 0
        old = datetime.now()
        name = startLogging + '.csv.tmp'
        with open(bdir + name, 'w', newline='') as csvfile:
            LogWriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            LogWriter.writerow(['Noise', 'MaxCountsScale', 'Integration Time'])
            LogWriter.writerow([config['noise'], config['maxValue'], ArduinoPause])
            LogWriter.writerow(['Time', 'RawValue'])
            try:
                while i < FileLen:
                    data = rl.sreadline()[:-2].decode('utf-8')
                    if data:
                        data = int(data)
                        i += 1
                        if data != 0:
                            LogWriter.writerow([datetime.now().isoformat(), data])
                        else:
                            LogWriter.writerow([datetime.now().isoformat(), 0])



            except KeyboardInterrupt:
                sercount.close()
        endFile()

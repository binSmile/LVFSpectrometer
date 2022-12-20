
import time
from datetime import datetime

import serial
import numpy as np
import pandas as pd
from _testcapi import Generic
from matplotlib import pyplot as plt



# [5846.0, 2944, 30.627535994394872]

def test013():
    ser.write(b'013,on')
    time.sleep(1)
    ser.write(b'013,off')
    time.sleep(1)
    ser.write(b'013,on')
    time.sleep(2)
    ser.write(b'013,off')


def Move(steps):
    print('Move to: ', steps)
    p0 = GetState()
    steps = int(steps)
    paim = p0 + steps
    ser.flushInput()
    ser.flushOutput()
    COMMAND = bytes('002,move,%s' % steps, 'utf8')
    ser.write(COMMAND)
    try:
        i = 0
        print('paim: ', paim)
        while GetState() != paim:
            # print('Get')
            i+=1
            # print(GetState())
            time.sleep(0.2)
            if i >= 1000:
                print('Long Operation! Brake!')
                StepperBrake()
                break

    except KeyboardInterrupt:
        print("KeyboardInterrupt has been catched!")
        StepperBrake()
    print('Stepper at ', GetState())


def GoHome():
    print('Write 0 if stepper at the home or -1 if stepper at the end.')
    steps = 1
    while steps != 0:
        steps = 0
        steps = int(input('How many steps I need to do: '))
        if steps == -1:
            Move(16 * PulsePerRev - 1)
        Move(-steps)

    COMMAND = bytes('002,reset', 'utf8')
    ser.write(COMMAND)
    print('Okey. We at home.')


def GetCounts(exposition):
    time.sleep(exposition)
    return 0


def DoPointSpectra(points, exposition, LVFLen, name='Test'):
    # GoHome()
    HomePosition = GetState()
    start = datetime.now()

    i = 1
    spacer = LVFLen / points
    print('Get point 1')
    Acquisition(1)
    Spectra = [[GetState()] + Acquisition(exposition)]
    for l in range(points):
        i += 1
        print('Get point %s' % i)
        Move(spacer)
        data = [GetState()] + Acquisition(exposition)
        Spectra += [data]
    print('GoHome')
    Move(-GetState()+HomePosition)

    Spectra = pd.DataFrame(Spectra,
                           columns=['Pos', 'Int', 'Num', 'Std', 'Mean'])
    # Spectra.set_index('Pos', inplace=True)

    x = [3280, 7360]
    y = [733 + 12.1, 468 + 12.1]
    a, b = np.polyfit(x, y, 1)
    Spectra['W'] = Spectra['Pos'] * a + b
    Spectra = Spectra.set_index('W')

    startLogging = start.replace(microsecond=0).strftime('%Y-%m-%d_%H-%M-%S')
    name = startLogging + '_'+ name
    Spectra.to_excel(specdir + name + '.xlsx')

    plt.errorbar(Spectra.index, 'Int', yerr='Std', data=Spectra)
    mins = max(Spectra['Int'].min(),0)
    maxs = max(Spectra['Int'].max(),1)
    plt.vlines(745, mins, maxs,colors='k')
    plt.vlines(480, mins, maxs,colors='k')
    plt.hlines(Spectra['Int'].mean(), 880, 745,colors='k')
    plt.title(name)
    plt.suptitle("Exposition: %s" % exposition)
    plt.savefig(specdir + name + '.png')
    with open(specdir+name+'_info.txt','w') as info:
        info.write('Exposition,%s' % exposition)

    print('Gotcha!')
    print(name)
    return Spectra


def SetSpeed(speed):
    COMMAND = bytes('002,setspeed,%s' % speed, 'utf8')
    ser.write(COMMAND)


def StepperBrake():
    COMMAND = bytes('002,brake', 'utf8')
    ser.write(COMMAND)


def SetAccel(Accel):
    COMMAND = bytes('002,setaccel,%s' % Accel, 'utf8')
    ser.write(COMMAND)


def GoToEnd():
    Move(16 * PulsePerRev - 1)


def GetState():
    ser.readline()
    ser.flushInput()
    ser.flushOutput()
    # COMMAND = bytes('002,Current', 'utf8')
    # ser.write(COMMAND)
    try:
        time.sleep(0.2)
        buff = ser.readline()
        reading = int(buff.decode('utf8')[:-2])
    except:
        ser.flushInput()
        ser.flushOutput()
        time.sleep(1)
        buff = ser.readline()
        print('pause at get state')
        reading = int(buff.decode('utf8')[:-2])
    # print('State: ',reading)
    return reading


def Acquisition(atime):
    # atime in seconds
    i = 0
    t_end = time.time() + atime

    Acq = np.array([])
    while time.time() < t_end:
        sercount.flushInput()
        sercount.flushOutput()
        data = sercount.readline()[:-2].decode('utf-8')

        try:
            Acq = np.append(Acq, int(data))
        except:
            print('Miss Value')
    # return [median, Num, Std]
    print(np.median(Acq), np.mean(Acq), len(Acq), Acq.std())
    return [np.median(Acq), len(Acq), Acq.std(),np.mean(Acq)]


def FalseGet():
    sercount.flushInput()
    sercount.flushOutput()
    sercount.readline()[:-2].decode('utf-8')


if __name__ == '__main__':
    bbdir = 'C:\\Users\\al\\ExtDrive\\GlobalProjects\\STM-Electroluminescence\\ExpData\\Omicron results\\'
    bdir = bbdir + 'PulseGrabber\\'
    specdir = bbdir + 'Specs\\'
    # ArduFile = bbdir + 'PulseCounterProgramm\\PulseCounterProgramm.ino'

    LVFport = 'COM8'
    ser = serial.Serial(LVFport, 2000000, timeout=1)
    PulsePerRev = 800
    print('Step Driver set at 800 pulse/rev')

    PCounterPort = 'COM7'
    sercount = serial.Serial(PCounterPort, 115200, timeout=1)

    # test013()
    # GoHome()

    # LVFLen = 16 * PulsePerRev * 0.95
    LVFLen = 500
    FullLen = 7360
    # Move(10000)

    # spec = DoPointSpectra(points=50,exposition=1,LVFLen=LVFLen)
    # DoPointSpectra(points=5,exposition=1,LVFLen=100)
    # GoToEnd()
    if True == True:
        # Spectra = DoPointSpectra(points=5,exposition=60,LVFLen=7000,name='Test')
        print('Position on AVR: %d' % GetState())
        GoHome()
        SpecName = 'STM-LE_Au-Au_10nA_-2.5V' #input('Spec name:')
        Spectra = DoPointSpectra(points=20,exposition=2,LVFLen=12000,name=SpecName)
        # plt.errorbar(Spectra.index, 'Int', yerr='Std', data=Spectra)


    # ser.close()

import time
from datetime import datetime
import serial
import numpy as np
import pandas as pd
from _testcapi import Generic
from matplotlib import pyplot as plt


def test013():
    """
    Test script for blinking LED on Ardunino
    :return: None
    """
    ser.write(b'013,on')
    time.sleep(1)
    ser.write(b'013,off')
    time.sleep(1)
    ser.write(b'013,on')
    time.sleep(2)
    ser.write(b'013,off')


def Move(steps):
    """
    Just move
    :param steps: forward for positive, and backward for negative
    :return: None
    """
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
    """
    Function for manual approaching to home position
    :return:
    """
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



def DoPointSpectra(points, exposition, LVFLen, name='Test'):
    """
    Main function for getting spectrum
    :param points:     stops counts on the move range
    :param exposition: time in seconds signal collection
    :param LVFLen:     range of move along LVF
    :param name:       name for save file
    :return: DataFrame with spectra in each point
    """
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
    """
    Acuisituion of intensity from pulse counter.
    :param atime: time in sec
    :return: [np.median(Acq), len(Acq), Acq.std(), np.mean(Acq)]
    """

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
    """It need sometime, when you don't use serial port during the long time, you must flush it, before normal working"""
    sercount.flushInput()
    sercount.flushOutput()
    sercount.readline()[:-2].decode('utf-8')


if __name__ == '__main__':
    bbdir = 'C:\\..\\GlobalProjects\\STM-Electroluminescence\\ExpData\\Omicron results\\'
    bdir = bbdir + 'PulseGrabber\\'
    specdir = bbdir + 'Specs\\'

    LVFport = 'COM8'        # Port to move controller
    PulsePerRev = 800       # Step Driver regime
    PCounterPort = 'COM7'   # Port to Pulse counter

    # LVFLen = 16 * PulsePerRev * 0.95
    LVFLen = 500            # Length of holder shadow in steps
    FullLen = 7360          # Length of usefull part of LVF


    # Connect to pulse mover
    ser = serial.Serial(LVFport, 2000000, timeout=1)
    print('Step Driver set at %s pulse/rev' % PulsePerRev )
    # Connect to pulse counter
    sercount = serial.Serial(PCounterPort, 115200, timeout=1)

    # test013()
    # GoHome()


    Move(10000)

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

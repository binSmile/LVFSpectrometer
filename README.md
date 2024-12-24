# LVFSpectrometer
[<img src="https://images2.imgbox.com/a9/fb/PXq0IYTD_o.jpg" width="400">
](https://www.youtube.com/watch?v=VhedL_mU17M)




 Spectrometer based on linear variable filter with pulse-counter

The main idea was born, from need on spectral measurements of really weak light source (Scanning Tunneling Microscopy Light Emission).


My system consist of several parts:
- IDQuantique ID120 Single photo counter, Avalanced Photo Diode (APD) (with LV-TTL output)
- Optical system based on Thorlab's Cage system with several mirrors, beam splitter (90:10) and laser diode for illumination of collection point
- ESP8266 used as TTL pulse counter from APD (also used as DAC) 
- Linear Variable Filter (LVF) by Ocean Optics (now Ocean Insight) for 300-750 nm range.
- Arduino UNO used for movement step motor control
- Step driver TB6600
- 3D printed LVF holder.


Let's describe each part.
## DAC and pulse counter
In folder **Controllers**, you found ESPPulseCounter.ino - firmware for ESP8266. 
Previously it works on Arduino too, but it has some lags and minimal pulses integration time was 20 ms. ESP8266 - works better, the best time is 7 ms.
Before flashing firmware to ESP, you should set integration time, and minimum and maximum counting levels in Hz (counts per second), which correspond to 0V and 5V levels on DAC.

The main problem of counting pulses from is very short pulses from APD. Output pulse width is 25 **ns**. 
For counting, I use M74HC4040 (or SN74HC4040N) 12-Bit Asynchronous Binary Counters. And collect the number by MCP23017, 16-bit input/output port expander.  The ESP reads the number for one clock from port-extender. After that, the number was sent to serial and to MCP4725 12-bit DAC.
The DAC output was connected with Omicron Microscope to Aux2-port.
The layout of interconnection you can see in ESPPulseCounter-connection.svg

### Pulse_grabber.py
At the first time, I used simple python serial port grabber for collection information about intensity. At start of the script, it read a file with ESP firmware and store in file the values of DAC settings (such as min/max counts and integration time). These values may be used by some scripts for analyzing of Omicron Experimental Data.
This program writes counts to txt file and zip it in the end of work.

## Linear Variable Filter
I had a linear Variable Filter by Ocean Optics (You can read more here [https://www.oceaninsight.com/products/sampling-accessories/solid-sampling/linear-variable/lvf-hh/?qty=1](Ocean Insight)). 

## 3D-models
<img src="https://raw.githubusercontent.com/binSmile/LVFSpectrometer/main/models/images/LVF%20mover%20and%20holder.jpg" alt="drawing" width="400"/>
You can find models created in SolidWorks, I share to you the holder of LVF filter, and cage-holder for step-motor actuator.
If you plan to use it,  I recommend to you: paint model to black color,  and modify it for decreasing of shadows on light path. Also, in one of edge position, you will have touch of LVF-holder  with cage.

## Actuator
I bought  an assembled actuator with step motor from Aliexpress . It has DC 4-9 V  power supply. And it has driven by TB6600 step driver. I use 1/800 regime on driver, and it means, that driven shaft will have 12800 steps for 90 mm rod. 

## Arduino Move controller
You can find MoveControl.ino with Arduino Uno firmware and MoveControl-connection with connection layout. Also, I applied [GyverStepper2](https://alexgyver.ru/gyverstepper/). This is an excellent lib for stepper control.
For controlling of Arduino by serial, I used a simple communication  language presented is SerialCommunication-example sketch.

### Wires
- D4 to ENA+
- D3 to DIR+
- D2 to PUL+

### Commands for move controlling
Comand's structure is:
"Device","Comand","Value"
In this case the device number is **002**

- **002,brake,0** - stop
- **002,move,777** move on 777 steps forward
- **002,setspeed,-666** backward movement with speed 666 steps per piece of time
- **002,reset,0** set zero position 0

#### Service commands:
- **002,ready,0** return **m** - move, **r** - ready
- **002,Current,0** curent position
- **002,getStatus,0** 
- **002,setaccel,333** - you can set acceleration in step per sec^2. Set Zero is means movement with maximal speed, without smooth acceleration.



## SpecAcquisition.py
This is main programm for spectra Acusition.
Usually, I start it from console and use comand interface for experiment proceeding.
Todo: check stable work with long acqusition, more then 10 minutes.

### Main functions
- **GoHome()** - Function for manual approaching to home position. Setup doesn't have end move buttons.
- **DoPointSpectra(points=20,exposition=2,LVFLen=12000,name=SpecName)** - this command do 20 stops during 12000 steps lenght of movement, with 2 second acuqsition on each stop.

## SpecReader.py
Simple plotter of measured spectra.




## File tree
```
.
├── controllers                           - firmwares
│   ├── ESPPulseCounter-connection.svg    - wire connection DAC
│   ├── ESPPulseCounter.ino - ESP arduino - like firmware for pulse-counter DAC
│   ├── MoveControl-connection.svg        - wire connection of LVF mover
│   ├── MoveControl.ino                   - firmware for LVF mover
│   └── SerialCommunication-example.ino   - example of simple commmunication between PC and arduino.
├── models                                - directory with 3d-models for printing of LVF-holder.
│   ├── IDQ-LD.SLDASM
│   └── ...
├── README.md
├── Pulse_grabber.py                      - Loging of pulses from counter
├── SpecAcquisition.py                    - programm for Spectum acqusition with LFV
└── SpecReader.py                         - Simple plotter
```

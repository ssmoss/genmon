#!/usr/bin/env python
# ------------------------------------------------------------
#    FILE: serialtest.py
# PURPOSE:
#
#  AUTHOR: Jason G Yates
#    DATE: 12-Apr-2017
# Free software. Use at your own risk.
# MODIFICATIONS:
# -------------------------------------------------------------------------------


import os
import sys
import time

import serial


# ------------ VersionTuple -----------------------------------------------------
def VersionTuple(value):

    value = removeAlpha(value)
    return tuple(map(int, (value.split("."))))


# ----------  removeAlpha--------------------------------------------------------
# used to remove alpha characters from string so the string contains a
# float value (leaves all special characters)
def removeAlpha(inputStr):
    answer = ""
    for char in inputStr:
        if not char.isalpha() and char != " " and char != "%":
            answer += char

    return answer.strip()


# ------------------- Open Serial Port ------------------------------------------
def OpenSerialPort(name, rate):

    # Starting serial connection

    if VersionTuple(serial.__version__) < VersionTuple("3.3"):
        NewSerialPort = serial.Serial()
    else:
        NewSerialPort = serial.Serial(exclusive=True)

    print("Using python serial library V" + serial.__version__)
    NewSerialPort.port = name

    if NewSerialPort.is_open == True:
        print(
            "The serial port is already opened. The serial port is in use, please stop genmon and retry."
        )
    NewSerialPort.baudrate = rate
    NewSerialPort.bytesize = serial.EIGHTBITS  # number of bits per bytes
    NewSerialPort.parity = serial.PARITY_NONE  # set parity check: no parity
    NewSerialPort.stopbits = serial.STOPBITS_ONE  # number of stop bits
    NewSerialPort.timeout = 4  # non-block read
    NewSerialPort.xonxoff = False  # disable software flow control
    NewSerialPort.rtscts = False  # disable hardware (RTS/CTS) flow control
    NewSerialPort.dsrdtr = False  # disable hardware (DSR/DTR) flow control
    NewSerialPort.writeTimeout = 2  # timeout for write

    # Check if port is open
    if NewSerialPort.is_open == False:
        try:
            NewSerialPort.open()
            print("Serial port opened")
        except Exception as e:
            print("error opening serial port: " + str(e))
            print("\nTry stopping genmon.\n")
            return 0
    else:
        print(
            "Serial port already opened. The serial port is in use. Please stop genmon and retry."
        )
        return 0

    NewSerialPort.flushInput()  # flush input buffer, discarding all its contents
    NewSerialPort.flushOutput()  # flush output buffer, aborting current output

    return NewSerialPort


# ------------------GetErrorInfo-------------------------------------------------
def GetErrorInfo():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    lineno = exc_tb.tb_lineno
    return fname + ":" + str(lineno)


# ------------------- Command-line interface for monitor ------------------------
if __name__ == "__main__":  # usage SerialTest.py [port]

    device = "/dev/serial0" if len(sys.argv) < 2 else sys.argv[1]

    baudrate = 9600

    print(
        "\nNote: Genmon must NOT be running for this test to work properly. If Genmon is running this test will not function properly,"
    )
    print("\nLoopback testing for serial port " + device + "...\n")

    try:

        # Starting serial connection
        serialPort = OpenSerialPort(device, baudrate)

        if serialPort == 0:
            print("Error opening Serial Port " + device)
            sys.exit(1)

        TestString = "Testing 1 2 3\n"

        print("write data: sent test string")
        serialPort.write(TestString.encode())
        time.sleep(0.05)
        print("waiting to received data....")
        ReceivedString = serialPort.readline()

        if TestString != ReceivedString.decode("UTF-8"):
            print(
                "FAILED: Sent data does not match receive. Received %d bytes"
                % len(ReceivedString)
            )
        else:
            print("PASSED! Loopback successful")
        serialPort.close()

    except Exception as e1:
        print("error communicating...: " + str(e1) + " " + GetErrorInfo())

    sys.exit(1)

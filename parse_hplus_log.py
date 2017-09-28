#encoding=utf-8

# HPLUS Log parser
# Author João Paulo Barraca <jpbarraca@gmail.com>
#

import os
import sys
import btsnoop.btsnoop.btsnoop as bts
from struct import unpack
import binascii
import re
import logging
import ctypes

def getFloat(b4, b3, b2, b1):
    number =  (((b1 + (b2 * 256)) + ((b3 * 256) * 256)) + (((b4 * 256) * 256) * 256))
    return ctypes.c_float(number & 0xFFFFFFFF).value / 1000000.0

def getShort(msb, lsb):
    return (msb & 0xFF) * 256 + (lsb & 0xFF)

def getByte(b):
    return b & 0xFF

def parseMessage_Sleep(data):
    year = data[2] * 256 + data[1]
    month = data[3]
    day = data[4]

    sleep_enter_time = getShort(data[6], data[5])
    sleep_spindles_time = getShort(data[8], data[7])
    sleep_deep_time = getShort(data[10], data[9])
    sleep_rem_time = getShort(data[12], data[11])
    sleep_wakeup_time = getShort(data[14], data[13])
    sleep_wakeup_count = getShort(data[16], data[15])
    sleep_start_hour = data[17]
    sleep_start_minute = data[18]

    total_sleep_time = sleep_enter_time + sleep_spindles_time + \
    sleep_deep_time + sleep_rem_time + sleep_wakeup_time
    total_sleep_hours = total_sleep_time / 60
    sleep_start_hour = data[17]
    sleep_start_minute = data[18]

    print "SLEEP: " + str(year)+"-"+str(month) + "-" + str(day) + \
        " enter_time=" + str(sleep_enter_time) + \
        " sleep_spindles_time=" + str(sleep_spindles_time) +\
        " sleep_rem_time=" + str(sleep_rem_time) + \
        " sleep_wakeup_time=" + str(sleep_wakeup_time) + \
        " sleep_deep_time=" + str(sleep_deep_time) + \
        " sleep_wakeup_count=" + str(sleep_wakeup_count) + \
        " sleep_total_time=" + str(total_sleep_hours) + ":" + str(total_sleep_time % 60) + \
        " sleep_start_time=" + \
        str(sleep_start_hour) + ":" + str(sleep_start_minute)

def parseMessage_DaySlot(data):
    slot = getShort(data[4], data[5])
    heartRate = data[1] & 0xFF
    steps = getShort(data[2], data[3])

    atemp = data[6]
    secondsInactive = data[7] & 0xFF

    print "DAY_SLOT_DATA: Slot: %d, Steps: %d, InactiveSeconds: %d, HeartRate: %d, ATemp: %d" % (slot, steps, secondsInactive, heartRate, atemp)

def parseMessage_DaySlot_Multiple(data):
    print "DAY_SLOT_DATA_MULTIPLE: ",
    if len(data) < 19:
        print "UNKNOWN " + str(data)
        return
    print

    for n in [4, 10, 16]:

        slot = data[n]
        heartRate = data[n - 3] & 0xFF
        steps = getShort(data[n - 2], data[n - 1])

        atemp = data[n + 1]
        active = data[n + 2] & 0xFF

        print "\tSub: %d Slot: %d, Steps: %d, Active: %d, HeartRate: %d, ATemp: %d" % (n, slot, steps, active, heartRate, atemp)

def parseMessage_DayStats(data):
    distance = (data[4] * 256 + data[3]) / 100.0  # in KM

    x = getShort(data[6], data[5])
    y = getShort(data[8], data[7])
    calories = x + y

    steps = data[2] * 256 + data[1]

    heartRate = data[11] & 0xFF

    activeTime = getShort(data[14], data[13])
    battery = data[9]

    bpm = data[11]

    if data[11] == 255:
        bpm = 0

    print 'REALTIME: steps: %d, calories: %d, distance: %d, bpm: %d, battery: %d, activeTime: %d' % (steps, calories, distance, bpm, battery, activeTime)

def parseMessage_Hello(payload):
    print "HELLO"

def parseMessage_SetDate(payload):
    year = (abs(payload[1]) * 256) + abs(payload[2]) % 256
    month = abs(payload[3])
    day = abs(payload[4])
    print "SET_DATE: %02d-%02d-%04d" % (day, month, year)

def parseMessage_SetTime(payload):
    print "SET_TIME: %02d:%02d:%02d" % (payload[1], payload[2], payload[3])

    
def parseMessage_SetWeek(payload):
    print "SET_WEEK_DAY: %s"  % ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][payload[1]]
    
def parseMessage_SetTimeMode(payload):
    print "SET_TIME_MODE: ", 
    if payload[1] == 0x01:
        print "24H"
    else:
        print "AM/PM"
    
def parseMessage_SetGender(payload):
    print "SET_GENDER: ", 
    if payload[1] == 0x01:
        print "Make"
    else:
        print "Female"
    
def parseMessage_SetAge(payload):
    print "SET_AGE: %d" % (payload[1])
    
def parseMessage_SetHeight(payload):
    print "SET_HEIGHT: %d - %s" % (abs(payload[1]), payload)

def parseMessage_SetWeight(payload):
    print "SET_WEIGHT: %d" % (payload[1])

def parseMessage_SetGoal(payload):
    print "SET_GOAL: %d" % ((payload[1] << 8) + payload[2])

def parseMessage_SetLanguage(payload):
    print "SET_LANGUAGE:", 
    if payload[1] == 2:
        print "EN"
    elif payload[1] == 1:
        print "CN"
    else: 
        print "UNKNOWN - %d" % payload[1]
    
def parseMessage_SetScreenTime(payload):
    print "SET_SCREENTIME: %d" % payload[1]

def parseMessage_SetUnits(payload):
    print "SET_UNITS:", 
    if payload[1] == 0:
        print "METRIC"
    elif payload[1] == 1:
        print "IMPERIAL"
    else: 
        print "UNKNOWN - %d" % payload[1]

def parseMessage_SetAllDayHR(payload):
    print "SET_ALLDAY_HR:", 
    if payload[1] == 0x0a:
        print "ON"
    elif payload[1] == 0:
        print "OFF"
    else: 
        print "UNKNOWN - %d" % payload[1]

def parseMessage_GetDeviceID(payload):
    print "GET_DEVICE_ID"
    
def parseMessage_GetVersion(payload):
    print "GET_VERSION"
    

def parseMessage_GetCurrentData(payload):
    print "GET_CURRENT_DATA"

def parseMessage_GetActiveDay(payload):
    print "GET_ACTIVE_DAY_SLOT: %02d:%02d until %02d:%02d" % (payload[1], payload[2], payload[3], payload[4])

def parseMessage_GetSleepData(payload):
    print "GET_SLEEP_DATA"
    
def parseMessage_GetDayData(payload):
    print "GET_DAY_DATA"

def parseMessage_SetConfStart1(payload):
    print "SET_CONF_START1"

def parseMessage_Unknown1(payload):
    pass

def parseMessage_SetDisplayText(payload):
    m = ""
    for c in payload[3:]:
        m += chr(c)

    print "SET_DISPLAY_TEXT: Slot %d of %d: %s - %s" % (payload[2], payload[1], m, payload[3:])


def parseMessage_SetIncomingMessage(payload):
    print "SET_INCOMING_MESSAGE: %d" % (payload[1]), 
    if len(payload) >= 1 and payload[1] != 86 and payload[1] != 170:
        print "UNKNOWN - %d" % payload[1]

def parseMessage_DaySummary(data):
    year =  (data[10] & 0xFF) * 256 + (data[9] & 0xFF)
    month = data[11] & 0xFF
    day = data[12] & 0xFF

    steps = getShort(data[2], data[1])
    distance = getShort(data[4], data[3]) * 10
    activeTime = getShort(data[14], data[13])
    calories = getShort(data[6], data[5])
    calories += getShort(data[8], data[7])

    maxHeartRate = data[15] & 0xFF
    minHeartRate = data[16] & 0xFF
    print "DAY_SUMMARY: %02d-%02d-%02d Steps=%d Distance=%d ActiveTime=%d Calories=%d MaxHR=%d MinHR=%d" % (day, month, year, steps, distance, activeTime, calories, maxHeartRate, minHeartRate)

def parseMessage_Version(payload):
    major = 0
    minor = 0
    hw_major = 0
    hw_minor = 0
    unicode_support = False
    
    if len(payload) >= 11:
        major = payload[10] & 0xFF
        minor = payload[9] & 0xFF
        hw_major = payload[2] & 0xFF
        hw_minor = payload[1] & 0xFF
        unicode_support = (payload[3] != 0)
        s = ""
        for c in payload[11:]:
            s += chr(c)
        print "VERSION: SW %d.%d HW %d.%d Unicode=%s - %s - %s" % (major, minor, hw_major, hw_minor, unicode_support, payload, s)
    else:
        major = payload[2] & 0xFF
        minor = payload[1] & 0xFF
        print "VERSION: SW %d.%d - %s" % (major, minor, payload)

def parseMessage_SetConf1(payload):
    print "SET_CONF1"
    
def parseMessage_SetConf(payload):
    if len(payload) == 2:
        print "SET_CONF_START"
    else:
        print "SET_CONF_END"
    
def parseMessage_SetSIT(payload):
    print "SET_SIT: %s" % payload

def parseMessage_UnknownMessage(payload):
    m = []
    s = ""
    
    for c in payload:
        m.append("%02x" % c)
        s += chr(c)

    print "UNKNOWN MESSAGE: %s" % m

def parseMessage_SetMessageState(payload):
    print "SET_INCOMING_MESSAGE_STATE %d" % payload[1]

def parseMessage_GPSCoordinates(payload):
    index = payload[1]
    total = payload[2]
    current = payload[3]

    if current == 1:
        year = getShort(payload[5], payload[4])
        month = payload[6]
        day = payload[7]
        hour = payload[8]
        minute = payload[9]
        second = payload[10]
        latitude = getFloat(payload[15], payload[14], payload[13], payload[12])
        longitude = getFloat(payload[19], payload[18], payload[17], payload[16])
        print "GPS Index=%d Total=%d Curr=%d Date=%4d-%02i-%02i Time=%02d:%02d:%02d Latitude=%f Longitude=%f" % (index, total, current, year, month, day, hour, minute, second, latitude, longitude)
    else:
        latitude = getFloat(payload[7], payload[6], payload[5], payload[4])
        longitude = getFloat(payload[11], payload[10], payload[9], payload[8])
        print "GPS Index=%d Total=%d Curr=%d Latitude=%f Longitude=%f" % (index, total, current, latitude, longitude)

def parseMessage_SetIncomingCallNumber(payload):
    m = ""
    for c in payload[3:]:
        m += chr(c)

    print "SET_INCOMING_CALL_NUMBER %s - %s" %  (m, payload[1:])



def parseMessage(payload):
    s = " >"
    if payload[0] == 0x1b:
        s = "< "

    data = ""
    hexdata = ""
    
    payload = payload[3:]

    for i,c in enumerate(payload):
        if  c < 32:
            data += "."
        else:
            data += chr(c)
    
        hexdata += "{:02x}".format(abs(c))+" "
        payload[i] = abs(c)
    
    if len(payload) == 0:
        return
    
    print "%s " % s, 

    #print "RAW: %s %s - %s" % (s, hexdata, data)

    if payload[0] == 0x00:
        parseMessage_UnknownMessage(payload)
    elif payload[0] == 0x01:
        parseMessage_Hello(payload)
    elif payload[0] == 0x04:
        parseMessage_SetHeight(payload)
    elif payload[0] == 0x05:
        parseMessage_SetWeight(payload)
    elif payload[0] == 0x07:
        parseMessage_SetIncomingMessage(payload)
    elif payload[0] == 0x08:
        parseMessage_SetDate(payload)
    elif payload[0] == 0x09:
        parseMessage_SetTime(payload)
    elif payload[0] == 0x0b:
        parseMessage_SetScreenTime(payload)
    elif payload[0] == 0x0c:
        parseMessage_SetAlarm(payload)
    elif payload[0] == 0x15:
        parseMessage_GetDayData(payload)
    elif payload[0] == 0x16:
        parseMessage_GetCurrentData(payload)
    elif payload[0] == 0x17:
        parseMessage_GetVersion(payload)
    elif payload[0] == 0x18:
        parseMessage_Version(payload)
    elif payload[0] == 0x19:
        parseMessage_GetSleepData(payload)
    elif payload[0] == 0x1a:
        parseMessage_Sleep(payload)
    elif payload[0] == 0x23:
        parseMessage_SetIncomingCallNumber(payload)
    elif payload[0] == 0x22:
        parseMessage_SetLanguage(payload)
    elif payload[0] == 0x24:
        parseMessage_GetDeviceID(payload)
    elif payload[0] == 0x26:
        parseMessage_SetGoal(payload)
    elif payload[0] == 0x27:
        parseMessage_GetActiveDay(payload)
    elif payload[0] == 0x2a:
        parseMessage_SetWeek(payload)
    elif payload[0] == 0x2c:
        parseMessage_SetAge(payload)
    elif payload[0] == 0x2d:
        parseMessage_SetGender(payload)
    elif payload[0] == 0x2e:
        parseMessage_Version(payload)
    elif payload[0] == 0x33:
        parseMessage_DayStats(payload)
    elif payload[0] == 0x35:
        parseMessage_SetAllDayHR(payload)
    elif payload[0] == 0x36:
        parseMessage_DaySummary(payload)
    elif payload[0] == 0x38:
        parseMessage_DaySlot(payload)
    elif payload[0] == 0x39:
        parseMessage_DaySlot(payload)
    elif payload[0] == 0x3e:
        parseMessage_SetDisplayText(payload)
    elif payload[0] == 0x43:
        parseMessage_SetDisplayText(payload)
    elif payload[0] == 0x47:
        parseMessage_SetTimeMode(payload)
    elif payload[0] == 0x48:
        parseMessage_SetUnits(payload)
    elif payload[0] == 0x4d:
        parseMessage_SetConf1(payload)
    elif payload[0] == 0x4f:
        parseMessage_SetConf(payload)
    elif payload[0] == 0x51:
        parseMessage_SetSIT(payload)
    elif payload[0] == 0x52:
        parseMessage_DaySlot_Multiple(payload)
    elif payload[0] == 0x53:
        parseMessage_GPSCoordinates(payload)
    elif payload[0] == 0x40:
        parseMessage_SetMessageState(payload)
    else:
        parseMessage_UnknownMessage(payload)


def main():
    if len(sys.argv) == 1:
        print "Usage: python %s <logfile>" % sys.argv[0]
        sys.exit(-1)
    
    print "Processing file: %s" % sys.argv[1]

    with open(sys.argv[1], "r") as f:
        data = f.read()
        records = []
    
        if data[2] == ':' and data[5] == ':':
            print "Detected Gadgetbridge Debug file"
            data = data.split('\n')
            for line in data:
                if not ': 0x' in line and not ':  0x' in line:
                    continue
            
                payload = []
                if "writing to characteristic: 14702856-620a-3973-7c78-9cfff0876abd:" in line:
                    i = line.index(": 0x")
                    payload = [0x00, 0, 0]
                elif "changed: 14702853-620a-3973-7c78-9cfff0876abd value:" in line:
                    i = line.index(":  0x")
                    payload = [0x1b, 0, 0]
                else:
                    continue

                line = line[i:].replace(' 0x ', ' 0x0')
                line = line.split(' ')
                try:
                    for r in line[1:]:
                        if "0x" in r:
                            payload.append(int(r, 16))
                except:
                    logging.exception(line)
                    sys.exit(-1)
                parseMessage(payload)   

        else:
            print "Detected Btsnoop file"
            records = bts.parse(sys.argv[1])
            print "Records found: %d" % (len(records))

            for record in records:

                payload = unpack('%db' % len(record[4]), record[4])

                if len(record[4]) < 10:
                    continue

                payload = list(payload)

                if payload[9] != 0x1b and payload[9] != 0x12:
                    continue
                
                payload = payload[9:]
                parseMessage(payload)       

        f.close()
        sys.exit(0)



if __name__ == "__main__":
    main()

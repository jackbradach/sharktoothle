#!/usr/bin/env python3

# Sets up the data link to the nRF52 sniffer device.
import io
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.protocols import basic

from enum import IntEnum

import sys
from twisted.logger import globalLogBeginner, Logger
from twisted.logger import jsonFileLogObserver, textFileLogObserver
from twisted.logger import Logger
from zope.interface import provider

from NordicSniffer.sniffer import *
from NordicSniffer.packets import *
from NordicSniffer.pcapng import *

from sharktoothle.ui import SharktoothLE_TUI


import urwid
from urwid import Columns, Filler, Pile, BoxAdapter, LineBox, AttrWrap, Text, Padding

# TODO - packet classes should do nothing with the hardware.
# Move packet buffer to upper level class.

# TODO - add allbacks for packet received vs integrate more with Twister?
# TODO: Iterable on decoded packets!

# packet flow widgets, showing simply eye candy for "packets are flowing", eg a
# 1 pixel/packet/s (maybe vary intensity?).  Scale the time base to look interesting
# (shoot for portal 2 endindg music scnene with the data packet window flowing back and forth)
#
#  Another view should show pkt/s vs seconds in a bargraph histogram.
#
#  Track packets (req/resp)
#  decode gatt and save examples
#  allow dummy data to light up the dials
#
log = Logger(namespace="main")

class SharkToothLE():
    palette = [
        ('header', 'white', 'light blue', 'standout'),
        ('body', 'light green', 'dark gray'),
        ('packet_header', 'light cyan', 'dark blue'),
        ('packet', 'white', 'dark cyan')
    ]

    def __init__(self, port='/dev/ttyUSB0'):
        #globalLogBeginner.beginLoggingTo([jsonFileLogObserver(sys.stdout)])
        globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
        self._sniffer = NordicSniffer(port=port)
        # self.setup_sniffer()

        ui = SharktoothLE_TUI()
        ui.setup_screen()
        self._ui = ui

    # def setup_sniffer(self):
    #     p = Section(linktype=LINKTYPE_BLUETOOTH_LE_LL)
    #     p.shb.options.add([
    #         Option(pcapng.SHB_OPTION_HARDWARE, "Nordic NRF52 Bluetooth LE Sniffer"),
    #         Option(pcapng.SHB_OPTION_OS, "Linux"),
    #         Option(pcapng.SHB_OPTION_USERAPPL, "SharkToothLE")
    #         ])
    #     p.idb.options.add([
    #         Option(OptionCode.IF_NAME, "ttyUSB0"),
    #         Option(OptionCode.IF_DESCRIPTION, "Nordic BLE Sniffer Firmware")
    #         ])
    #     self._pktsec = p



    def twisted_callback(self):
        print("callback!")
        scr.refresh()

    def run(self):
        self.loop.set_alarm_in(1/60, self.update_screen)
        self.loop.run()

    def unhandled_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
    #    print("Key: {}".format(key))
        return True

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port_path):
        # TODO: test if port exists?
        self._port = port_path


if __name__ == "__main__":
    st = SharkToothLE('/dev/ttyUSB0')
    st.run()

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

from NordicSniffer import *
from NordicUartPacket import *
from NordicSlipPacket import NordicSlipPacket
from NordicSnifferPacket import *
from BleLinkLayerPacket import *
from PacketBuffer import *

import urwid
from urwid import Columns, Filler, Pile, BoxAdapter, LineBox, AttrWrap, Text, Padding
from PacketWidgets import *
from pcapng import *
import pcapng

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




class NerfLink():
    palette = [
        ('header', 'white', 'light blue', 'standout'),
        ('body', 'light green', 'dark gray'),
        ('packet_header', 'light cyan', 'dark blue'),
        ('packet', 'white', 'dark cyan')
    ]
    def __init__(self, port='/dev/ttyUSB0'):
        #globalLogBeginner.beginLoggingTo([jsonFileLogObserver(sys.stdout)])
        globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
        self.log = Logger(namespace="NerfLink")
        self.cnt = 0
        self.port = port
        self._sniffer = NordicSniffer(port=port, callback=self.interact)
        self.setup_screen()
        self.setup_sniffer()

    def setup_screen(self):
        text_header = (u"Nerf FiddyTwo")
        header = AttrWrap(Text(text_header), 'header')
        self.pktlist = PacketFrame()
        pktlist = BoxAdapter(AttrWrap(self.pktlist, 'packet'), 20)
        pktlist = Padding(LineBox(pktlist, title="UART Packets"), align='center', left=2, right=2)
        buttons = Padding(ButtonPanel(), align='center', left=2)
        pile = Pile([header, Columns([(16, BoxAdapter(Filler(buttons, valign='middle'),20)), pktlist])])
        top = Filler(pile, valign='top')

        self.evl = urwid.TwistedEventLoop()
        self.loop = urwid.MainLoop(top, self.palette,
                      unhandled_input=self.unhandled_input, event_loop=self.evl)

    def setup_sniffer(self):
        p = Section(linktype=LINKTYPE_BLUETOOTH_LE_LL)
        p.shb.options.add([
            Option(pcapng.SHB_OPTION_HARDWARE, "Nordic NRF52 Bluetooth LE Sniffer"),
            Option(pcapng.SHB_OPTION_OS, "Linux"),
            Option(pcapng.SHB_OPTION_USERAPPL, "SharkToothLE")
            ])
        p.idb.options.add([
            Option(OptionCode.IF_NAME, "ttyUSB0"),
            Option(OptionCode.IF_DESCRIPTION, "Nordic BLE Sniffer Firmware")
            ])
        self._pktsec = p

    def update_screen(self, loop, data):
        pl = self.pktlist

        for pkt in self._sniffer.pbuf:
            self.cnt = self.cnt + 1
            self._pktsec.add_packet(EnhancedPacketBlock(pkt.data))

        with open('test.pcapng', 'wb') as f:
            f.write(self._pktsec.as_bytearray)

        #loop.set_alarm_in(1/30, self.update_screen)

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

    def interact(self):
        sniffer = self._sniffer
        c = scr.getch()
        self._win.addstr(0, 0, "meh", curses.A_BOLD)
        self._win.refresh()
        if c != -1:
            scr.addstr(str(c) + ' ')

            scr.refresh()

if __name__ == "__main__":
    nl = NerfLink('/dev/ttyUSB0')
    nl.run()

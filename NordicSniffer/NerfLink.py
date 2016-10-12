# Sets up the data link to the nRF52 sniffer device.

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.protocols import basic
from enum import IntEnum

from NordicSniffer import *
from NordicUartPacket import *
from NordicSlipPacket import NordicSlipPacket
from NordicSnifferPacket import *
from BleLinkLayerPacket import *
from PacketBuffer import *

# TODO - packet classes should do nothing with the hardware.
# Move packet buffer to upper level class.

# TODO - add allbacks for packet received vs integrate more with Twister?
# TODO: Iterable on decoded packets!

class NerfLink():
    cnt = 0

    def __init__(self, port='/dev/ttyUSB0'):
        self.port = port
        self._sniffer = NordicSniffer(port)

    def run(self):
        self._sniffer.run()

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port_path):
        # TODO: test if port exists?
        self._port = port_path

    def dataReceived(self, data):
        self.pbuf.add(data)

        for pkt in self.pbuf:
        #    print("packet #{}: {}".format(self.cnt, pkt))
            self.cnt = self.cnt + 1
            if (pkt is None):
                raise RuntimeError("Got a None packet?")
            print("UART: {}".format(pkt))
            if pkt.id_name=='EVENT_PACKET':
                sniff = NordicSnifferPacket(pkt.payload)
                if (sniff is None):
                    raise RuntimeError("Got a none event?")
                print("SNIFF: {}".format(sniff))

                ble_ll = BleLinkLayerPacket(sniff.payload)
                print("BLE_LL: {}".format(ble_ll))

        #packets = self.pbuf.get()

        if (self.cnt >= 30):
            reactor.stop()
        #for uart_pkt in self.ns.get():
        #    print(uart_pkt)
        #    if (uart_pkt.getId() == NordicUartPacketIds.EVENT_PACKET):
        #        sniff_pkt = NordicSnifferPacket(uart_pkt.getPayload())
        #        ble_ll_pkt = BleLinkLayerPacket(sniff_pkt.getPayload())
        #        print(sniff_pkt)
        #        print(ble_ll_pkt)
        #
        #    print("---")

if __name__ == "__main__":
    nl = NerfLink('/dev/ttyUSB0')
    nl.run()

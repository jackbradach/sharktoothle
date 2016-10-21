from twisted.internet import reactor, task
from twisted.internet.serialport import SerialPort
from twisted.protocols import basic
from twisted.logger import Logger
from .packets import SnifferPacket, BleLinkLayerPacket, SlipPacket, UartPacket
from .PacketBuffer import *

log = Logger(namespace="NordicSniffer")


class NordicSniffer(basic.LineReceiver):
    # Default port is USB0, add detect and reconnect?  Twisted
    # may handle that.
    def __init__(self, port="/dev/ttyUSB0", baud=460800, callback=None):
        self.setRawMode()
        self._seq_id = None
        self._serial_buffer = bytearray()
        self._packet_buffer = []
        self._pbuf = PacketBuffer()
        self.port = port
        self.baud = baud
        SerialPort(self, self.port, reactor, baudrate=460800)

    def __repr__(self):
        return "NordicSniffer({})".format(self._port)

    def __str__(self):
        str_repr = ("<NordicSniffer; " +
                    "port={}>".format(self._port))

    def stop(self):
        reactor.stop()

    # TODO - implement as Twisted deferred? (so it can catch the reply)
    def send_ping(self):
        self._log.debug("ping!")
        pass

    def send_pkt(self, packet):
        pass

    def scan(self):
        pkt = UartPacket()
        pkt.id = UartPacketIds.REQ_SCAN_CONT
        pkt.payload = []
        self._log.debug("SCAN!")
        reactor.callFromThread(self.send_ping)
        pass

    @property
    def baud(self):
        return self._baud

    @baud.setter
    def baud(self, rate):
        # TODO: this should re-init the link and can fail.
        self._baud = rate

    @property
    def port(self):
        """communication port used to communicate with sniffer"""
        return self._port

    @port.setter
    def port(self, port):
        """set communications port for sniffer use"""
        self._port = port
        # TODO - this should re-init twister!

    @port.deleter
    def port(self):
        """clears communication port (with cleanup)"""
        reactor.stop()
        self._port = None

    @property
    def seq_id(self):
        return self._seq_id

    # TODO - jbradach - 2016/10/11 - something is making some the UART packets
    # TODO - sequencing incorrect.  Make sure it's the firmware not sending vs
    # TODO - the API dropping them somewhere.
    @seq_id.setter
    def seq_id(self, new_seq_id):
        log = self._log
        if self.seq_id is not None:
            if new_seq_id != (self.seq_id + 1):
                exp_seq = self.seq_id + 1
                log.debug("Dropped packet(s) #{}-{}".format(exp_seq, new_seq_id-1))
        self._seq_id = new_seq_id

    @property
    def pbuf(self):
        return self._pbuf

    # Callbacks for Twisted
    def connected(self):
        print("Connected to sniffer")

    def connectionLost(self, reason):
        print("Sniffer connection lost")

    def rawDataReceived(self, recv_data):
        new_pkt_count = self._pbuf.add(recv_data)

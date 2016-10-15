from enum import IntEnum
from time import time
import struct
import re

class Packet:
    def __init__(self, data, timestamp=time()):
        self._timestamp = timestamp
        self._data = data

    def __repr__(self):
        return "{}({})".format(self.__class__, self._data)

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def data(self):
        return self._data

class SnifferPacket(Packet):
    HLEN = 0
    FLAGS = 1
    CHANNEL = 2
    RSSI = 3
    EC = 4
    TD = 6

    def __init__(self, data):
        if data is None or len(data) == 0:
            raise ValueError("Missing Sniffer packet data!")
        super().__init__(data)

    def __str__(self):
        dir_str = "\"M->S\"" if self.dir else "\"S->M\""
        repString = ("<NordicSnifferPacket; " +
                     "channel={:d}, ".format(self.channel) +
                     "crc_ok={:d}, ".format(self.crc_ok) +
                     "dir={:s}, ".format(dir_str) +
                     "ec={:d}, ".format(self.ec) +
                     "encrypted={:d}, ".format(self.encrypted) +
                     "hlen={:d} bytes, ".format(self.hlen) +
                     "mic_ok={:d}, ".format(self.mic_ok) +
                     "rssi={:d}dB, ".format(self.rssi) +
                     "tdiff={:d}>".format(self.tdiff) )
        return repString

    @property
    def channel(self):
        return self.header[self.CHANNEL]

    @property
    def crc_ok(self):
        return ((self.flags & 0x1) == 0x1)

    @property
    def dir(self):
        """packet direction (0 = Slave->Master, 1 = Master->Slave)"""
        return ((self.flags & 0x2) == 0x2)

    @property
    def ec(self):
        """event counter"""
        ec_offset = self.EC
        raw_ec = self.header[ec_offset:ec_offset+2]
        return int.from_bytes(raw_ec, byteorder='little')

    @property
    def encrypted(self):
        """packet is encrypted"""
        return ((self.flags & 0x4) == 0x4)

    @property
    def flags(self):
        """raw flags byte"""
        return self.header[self.FLAGS]

    @property
    def header(self):
        return self.data[:self.hlen]

    @property
    def hlen(self):
        """header length"""
        return self.data[self.HLEN]

    @property
    def mic_ok(self):
        """packet MIC OK flag"""
        return self.flags & 0x08

    @property
    def packet(self):
        return self.packet

    @property
    def payload(self):
        return self.data[self.hlen:]

    @property
    def rssi(self):
        """rssi (in -dB)"""
        return -self.header[self.RSSI]

    @property
    def tdiff(self):
        """difference in time between this and previous sniffer packet"""
        td_offset = self.TD
        rawTD = self.header[td_offset:td_offset+4]
        return int.from_bytes(rawTD, byteorder='little')

class BleLinkLayerPacket(Packet):
    AA = 0
    HEADER = 4
    LEN = 5
    PADDING = 6
    PAYLOAD = 6

    def __init__(self, data):
        # Documentation says the radio adds a padding byte
        # that needs to be stripped out; so *zap*
        del data[self.PADDING]
        super().__init__(data)

    def __str__(self):
        aa = "{:02x}:{:02x}:{:02x}:{:02x}".format(*self.aa)
        repString = ("<BleLinkLayerPacket; " +
                     "aa=[{:s}], ".format(aa) +
                     "crc=[{}], ".format(self.crc.hex()) +
                     "crc_calc=[{}], ".format(self.crc_ok()) +
                     "header={}>".format(self.header))
        return repString

    @property
    def aa(self):
        """access address"""
        aa_offset = self.AA
        raw_access_address = self.data[aa_offset:aa_offset+4]
        raw_access_address.reverse()
        aa = list(raw_access_address)
        return aa

    @property
    def header(self):
        hdr_offset = self.AA+4
        raw_hdr = int.from_bytes(self.data[hdr_offset:hdr_offset+2], byteorder='big')
        pdu = {}
        pdu['type'] = (raw_hdr & 0xF000) >> 12
        pdu['length'] = (raw_hdr & 0xFC) >> 2
        pdu['rxadd'] = (raw_hdr & 0x100) >> 16
        pdu['txadd'] = (raw_hdr & 0x200) >> 17
        return pdu

    @property
    def crc(self):
        """extracts the 3-byte CRC from the end of the packet"""
        crc = self.data[-3:]
        return crc

    # Calculate CRC over packet, compare to end
    # FIXME - jbradach - this doesn't do anything close to the correct thing
    def crc_ok(self):
        """verify crc on packet"""
        import crcmod
        # These values came from dr. koopman's big page of CRC
        # https://users.ece.cmu.edu/~koopman/crc/
        crc_poly = 0x100065b
        crc_bitrev = 0x1b4c001
        crc_fnc = crcmod.Crc(crc_poly, initCrc=crc_bitrev, rev=True)
        payload = self.data[self.HEADER:-3]
        crc = crc_fnc.update(payload)
    #    print("crc: {} vs {}".format(hex(crc.digest()), self.crc))
        return crc

    @property
    def payload(self):
        payload = self.data[self.PAYLOAD:-3]
        return payload


class NordicUartPacketIds(IntEnum):
    REQ_FOLLOW = 0x00
    EVENT_FOLLOW = 0x01
    EVENT_CONNECT = 0x05
    EVENT_PACKET = 0x06
    REQ_SCAN_CONT = 0x07
    EVENT_DISCONNECT = 0x09
    SET_TEMPORARY_KEY = 0x0C
    PING_REQ = 0x0D
    PING_RESP = 0x0E
    SWITCH_BAUD_RATE_REQ = 0x13
    SWITCH_BAUD_RATE_RESP = 0x14
    SET_ADV_CHANNEL_OP_SEQ = 0x17
    GO_IDLE = 0xFE

class UartPacket(Packet):
    HLEN_OFFSET = 0
    PLEN_OFFSET = 1
    PVER_OFFSET = 2
    PC_OFFSET = 3
    ID_OFFSET = 5

    HLEN_DEFAULT = 6
    PROTOVER_DEFAULT = 1

    def __init__(self, data=None):
        # TODO - validate the packet!
        if data is None:
            self._data = bytearray()
            self._payload = bytearray()
            self._hlen = NordicUartPacket.HLEN_DEFAULT
            self._protover = NordicUartPacket.PROTOVER_DEFAULT
            self._count = 0
        else:
            self._data = bytearray(data)
            self._hlen = data[NordicUartPacket.HLEN_OFFSET]
            self.id = data[NordicUartPacket.ID_OFFSET]
            self._payload = data[self.hlen:]
            self._protover = data[NordicUartPacket.PVER_OFFSET]
            pc_offset = NordicUartPacket.PC_OFFSET
            raw_pc = self._data[pc_offset:pc_offset+2]
            self._count = int.from_bytes(raw_pc, byteorder='little')

    def __repr__(self):
        return "NordicUartPacket({})".format(self.data)

    def __str__(self):
        packet_id = self.id
        if packet_id == NordicUartPacketIds.EVENT_PACKET:
            data = "[NRF_BLE_PACKET]"
            #data = NordicSnifferPacket(self.getPayload())
        elif packet_id == NordicUartPacketIds.PING_RESP:
            data = "[FW_VERSION = 0x{}]".format(self.payload.hex())
        else:
            data = "[{}]".format(self.payload.hex())

        repString = ("<NordicUart object; " +
                     "cnt={:d}, ".format(self.pc) +
                     "hlen={:d}, ".format(self.hlen) +
                     "id=\"{:s}\", ".format(self.id.name) +
                     "plen={:d}>".format(self.plen) )
        return repString

    @property
    def hlen(self):
        """header length"""
        return self._hlen

    @property
    def id(self):
        "packet type id"
        return self._id

    @id.setter
    def id(self, pkt_type):
        self._id = NordicUartPacketIds(pkt_type)

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, data):
        self._payload = data
        self._plen = len(data)

    @property
    def pc(self):
        "packet count"
        return self._count

    @property
    def plen(self):
        """payload length"""
        return len(self._payload)

    @property
    def protover(self):
        """protocol version"""
        return self._protover

class SlipPacket(Packet):
    SLIP_START = 0xAB
    SLIP_END = 0xBC
    SLIP_ESC = 0xCD
    SLIP_ESC_START = 0xAC
    SLIP_ESC_END = 0xBD
    SLIP_ESC_ESC = 0xCE
    SLIP_PKT_REGEX = b"\xab(?P<packet>.*?)(?!\xcd)\xbc"

    re_slip_pkt = re.compile(SLIP_PKT_REGEX, re.DOTALL | re.MULTILINE)

    def __init__(self, data):
        self.__init__(data)

    @classmethod
    def find(cls, pbuf):
        """Consumes the head of the packet buffer and spits out a
        sniffer packet that has had the NordicSlipPacket codes removed."""
        packets = NordicSlipPacket._extract_packets(pbuf)
        return packets

    @classmethod
    def _extract_packets(cls, pbuf):
        packets = []
        m = NordicSlipPacket.re_slip_pkt.finditer(pbuf)

        new_end = None
        for pkt in m:
            new_end = pkt.end()
            unesc_pkt = cls._unescape_packet(pkt.group('packet'))
            nsp = NordicSlipPacket(unesc_pkt)
            packets.append(nsp)

        # Remove processed data from packet buffer
        if (new_end is not None):
            del pbuf[:new_end]

        return packets

    @staticmethod
    def _unescape_packet(pkt):
        decode = {b'\xAC':b'\xAB',
                  b'\xBD':b'\xBC',
                  b'\xCE':b'\xCD'}
        repl = lambda matchob: (
            decode[matchob.group('esc')]
        )

        regexp = b'\xCD(?P<esc>.)'

        stripped = re.sub(regexp, repl, pkt, re.DOTALL | re.MULTILINE)
        return stripped

    @staticmethod
    def _escape_packet(pkt):
        decode = {b'\xAB':b'\xAC',
                  b'\xBC':b'\xBD',
                  b'\xCD':b'\xCE'}
        repl = lambda matchob: (
            decode[matchob.group('esc')]
        )
        # XXX - jbradach - implement me; needs to match on
        # all three.
        regexp = b'\xCD(?P<esc>.)'

        stripped = re.sub(regexp, repl, pkt, re.DOTALL | re.MULTILINE)
        return stripped

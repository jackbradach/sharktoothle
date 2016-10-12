from enum import IntEnum
import re


# TODO: Implement stream semantics?

class NordicSlipPacket():
    SLIP_START = 0xAB
    SLIP_END = 0xBC
    SLIP_ESC = 0xCD
    SLIP_ESC_START = 0xAC
    SLIP_ESC_END = 0xBD
    SLIP_ESC_ESC = 0xCE
    SLIP_PKT_REGEX = b"\xab(?P<packet>.*?)(?!\xcd)\xbc"

    re_slip_pkt = re.compile(SLIP_PKT_REGEX, re.DOTALL | re.MULTILINE)

    def __init__(self, packet_buffer):
        self.data = bytearray(packet_buffer)

    def __repr__(self):
        return "NordicSlipPacket({})".format(self.data)

    def getData(self):
        return self.data

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

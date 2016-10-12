from enum import IntEnum

class NordicSnifferPacket:
    HLEN = 0
    FLAGS = 1
    CHANNEL = 2
    RSSI = 3
    EC = 4
    TD = 6

    def __init__(self, data):
        if data is None or len(data) == 0:
            raise ValueError("Missing Sniffer packet data!")

        self.data = data

    def __repr__(self):
        return "NordicSnifferPacket({})".format(self.data)

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

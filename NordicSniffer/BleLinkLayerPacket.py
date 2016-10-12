
class BleLinkLayerPacket:
    AA = 0
    HEADER = 4
    LEN = 5
    PADDING = 6
    PAYLOAD = 6

    def __init__(self, data):
        if data is None or len(data) == 0:
            raise ValueError("Missing BLE LL packet data!")

        # Documentation says the radio adds a padding byte
        # that needs to be stripped out; so *zap*
        del data[self.PADDING]
        self._data = bytearray(data)

    def __repr__(self):
        return "BleLinkLayerPacket({})".format(self.data)

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
    # FIXME - jbradach - this doesn't work anywhere close to correct
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
    def data(self):
        return self._data

    @property
    def payload(self):
        payload = self.data[self.PAYLOAD:-3]
        return payload

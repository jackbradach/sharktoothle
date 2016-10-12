from enum import IntEnum
from NordicSnifferPacket import NordicSnifferPacket

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

class NordicUartPacket:
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
        else:
            self._data = bytearray(data)
            self._hlen = data[NordicUartPacket.HLEN_OFFSET]
            self.id = data[NordicUartPacket.ID_OFFSET]
            self._payload = data[self.hlen:]
            self._protover = data[NordicUartPacket.PVER_OFFSET]

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
        payload = self.data[self.hlen:]
        return payload

    @payload.setter
    def payload(self, data):
        self._payload = payload
        self._plen = len(payload)

    @property
    def pc(self):
        "packet count"
        pc_offset = NordicUartPacket.PC_OFFSET
        raw_pc = self.data[pc_offset:pc_offset+2]
        count = int.from_bytes(raw_pc, byteorder='little')
        return count

    @property
    def plen(self):
        """payload length"""
        return len(self._payload)

    @property
    def protover(self):
        """protocol version"""
        return self._protover

    @property
    def data(self):
        return self._data

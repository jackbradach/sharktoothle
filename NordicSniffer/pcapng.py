from struct import pack
from time import time
from enum import IntEnum, unique

@unique
class BlockType(IntEnum):
    IDB = 1
    PB  = 2
    SPB = 3
    NRB = 4
    ISB = 5
    EPB = 6
    SHB = 0x0A0D0D0A

@unique
class OptionCode(IntEnum):
    IF_NAME = 2
    IF_DESCRIPTION = 3
    IF_IPV4ADDR = 4
    IF_IPV6ADDR = 5
    IF_MACADDR = 6
    IF_EUIADDR = 7
    IF_SPEED = 8
    IF_TSRESOL = 9
    IF_TZONE = 10
    IF_FILTER = 11
    IF_OS = 12
    IF_FCSLEN = 13
    IF_TSOFFSET = 14

LINKTYPE_BLUETOOTH_LE_LL=251

SHB_OPTION_HARDWARE = 2
SHB_OPTION_OS = 3
SHB_OPTION_USERAPPL = 4


def pad_to_width(data, width=4):
    """Pads data with '\0's so it aligns to width"""
    if (len(data) == 0 or (len(data) % width == 0)):
        return data
    return data + b'\0' * (width - (len(data) % width))

#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                          Block Type                           |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                      Block Total Length                       |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# /                          Block Body                           /
# /              variable length, padded to 32 bits               /
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                      Block Total Length                       |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class Block:

    def __init__(self, block_body, align=4):
    #    self._block_type = block_type
        self._update(block_body, align)

    def __getitem__(self, item):
        return self._data[item]

    def _update(self, new_body, align):
        bt = self._block_type.to_bytes(align, byteorder='little')
        self.body = new_body

    @property
    def block_type(self):
        return self._block_type

    @property
    def as_bytearray(self):
        bt = pack("@I", self._block_type)
        body = pad_to_width(self._body)
        btl = pack("@I", len(self._body) + 12)
        return (bt + btl + body + btl)


#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#    +---------------------------------------------------------------+
#  0 |                   Block Type = 0x0A0D0D0A                     |
#    +---------------------------------------------------------------+
#  4 |                      Block Total Length                       |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  8 |                      Byte-Order Magic                         |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 12 |          Major Version        |         Minor Version         |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 16 |                                                               |
#    |                          Section Length                       |
#    |                                                               |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 24 /                                                               /
#    /                      Options (variable)                       /
#    /                                                               /
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                      Block Total Length                       |
#    +---------------------------------------------------------------+
class SectionHeaderBlock(Block):
    _block_type = BlockType.SHB
    _bom = 0x1A2B3C4D

    def __init__(self, data_block=None, majver=1, minver=0):
        if data_block:
            self._section_length = pack('@q', len(data_block.as_bytearray))
        else:
            self._section_length = pack('@q', 0)
        self._majver = majver
        self._minver = minver
        self._options = OptionList()
        super().__init__(b'')

    @property
    def options(self):
        return self._options

    @property
    def bom(self):
        """Byte-Order Magic: magic number, whose value is the hexadecimal
        number 0x1A2B3C4D. This number can be used to distinguish sections
        that have been saved on little-endian machines from the ones saved
        on big-endian machines."""
        return self._bom

    @property
    def as_bytearray(self):
        bom = pack("@I", self._bom)
        majver = pack("@H", self._majver)
        minver = pack("@H", self._minver)
        seclen = self._section_length
        options = self._options.as_bytearray

        self._body = bytearray(bom + majver + minver + seclen + options)
        return super().as_bytearray

#
#     0                   1                   2                   3
#     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#    +---------------------------------------------------------------+
#  0 |                    Block Type = 0x00000001                    |
#    +---------------------------------------------------------------+
#  4 |                      Block Total Length                       |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  8 |           LinkType            |           Reserved            |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 12 |                            SnapLen                            |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 16 /                                                               /
#    /                      Options (variable)                       /
#    /                                                               /
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                      Block Total Length                       |
#    +---------------------------------------------------------------+
class InterfaceDescriptionBlock(Block):
    _block_type = BlockType.IDB
    def __init__(self, linktype, snaplen=0):
        self._linktype = linktype
        self._snaplen = snaplen
        self._options = OptionList()
        pass

    @property
    def linktype(self):
        return self._linktype

    @property
    def snaplen(self):
        return self._snaplen

    @property
    def options(self):
        return self._options

    @property
    def as_bytearray(self):
        lt = pack("@H", self._linktype)
        rsvd = pack("@H", 0)
        sl = pack("@I", self._snaplen)
        options = self._options.as_bytearray
        self._body = bytearray(lt + rsvd + sl + options)
        return super().as_bytearray

#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#    +---------------------------------------------------------------+
#  0 |                    Block Type = 0x00000006                    |
#    +---------------------------------------------------------------+
#  4 |                      Block Total Length                       |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  8 |                         Interface ID                          |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 12 |                        Timestamp (High)                       |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 16 |                        Timestamp (Low)                        |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 20 |                    Captured Packet Length                     |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 24 |                    Original Packet Length                     |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# 28 /                                                               /
#    /                          Packet Data                          /
#    /              variable length, padded to 32 bits               /
#    /                                                               /
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    /                                                               /
#    /                      Options (variable)                       /
#    /                                                               /
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                      Block Total Length                       |
#    +---------------------------------------------------------------+
class EnhancedPacketBlock(Block):
    _block_type = BlockType.EPB
    def __init__(self, pkt_data, timestamp=int(time()), iface_id=0):
        self._iface_id = iface_id
        self._timestamp = timestamp
        self._pkt_data = pkt_data
        self._options = OptionList()
        # TODO - jbradach - 2016/10/15 - come up with a sensible way to
        # extract these?  Maybe just have a property to override them.
        self._cap_pkt_len = len(pkt_data)
        self._orig_pkt_len = len(pkt_data)

    @property
    def linktype(self):
        return self._linktype

    @property
    def snaplen(self):
        return self._snaplen

    @property
    def options(self):
        return self._options

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def cap_pkt_len(self):
        return self._cap_pkt_len

    @property
    def orig_pkt_len(self):
        return self._orig_pkt_len

    @property
    def pkt_data(self):
        return self._pkt_data

    @property
    def iface_id(self):
        return self._iface_id

    @property
    def as_bytearray(self):
        iface_id = pack("@I", self._iface_id)
        ts_high = pack("@I", self._timestamp >> 32)
        ts_low = pack("@I", self._timestamp & 0xFFFFFFFF)
        cpl = pack("@I", self._cap_pkt_len)
        opl = pack("@I", self._orig_pkt_len)
        pkt = pad_to_width(self._pkt_data)
        options = self._options.as_bytearray
        self._body = bytearray(iface_id + ts_high + ts_low +
                               cpl + opl + pkt + options)
        return super().as_bytearray

#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |      Option Code              |         Option Length         |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# /                       Option Value                            /
# /              variable length, padded to 32 bits               /
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# /                                                               /
# /                 . . . other options . . .                     /
# /                                                               /
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |   Option Code == opt_endofopt  |  Option Length == 0          |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class OptionList:

    def __getitem__(self, item):
        return self._data[item]

    def __init__(self):
        self._options = []

    def add(self, options):
        try:
            for option in options:
                self._options.append(option)
        except TypeError:
            self._options.append(options)
        return self

    @property
    def as_bytearray(self):
        options_list = bytearray()
        for opt in self._options:
            options_list.extend(opt.as_bytearray)
        options_list.extend(OptionEnd().as_bytearray)

        return options_list

class Option:
    def __init__(self, code, value):
        self._code = code
        self._value = bytearray(value, 'utf-8')

    @property
    def code(self):
        return self._code

    @property
    def length(self):
        return len(self._value)

    @property
    def value(self):
        return self._value

    @property
    def as_bytearray(self):
        oc = pack("@H", self._code)
        ol = pack("@H", len(self._value))
        ov = pad_to_width(self._value)
        return bytearray(oc + ol + ov)

class OptionComment(Option):
    def __init__(self, comment):
        uc = bytes(comment, 'utf-8')
        super().__init__(code=1, value=uc)

class OptionEnd(Option):
    """A special case of options; this is automatically appended
    to the end of an OptionList when it is returned as_bytearray.
    You probably don't have a good reason to instantiate it directly."""
    def __init__(self):
        super().__init__(code=0, value="")

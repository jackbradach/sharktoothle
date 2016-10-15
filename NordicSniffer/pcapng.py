from struct import pack
LINKTYPE_BLUETOOTH_LE_LL=251

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
    _block_type = 0x0A0D0D0A
    _bom = 0x1A2B3C4D

    def __init__(self, data_block=None, majver=1, minver=0):
        self._majver = majver
        self._minver = minver

        if data_block:
            self._section_length = pack('@q', len(data_block.as_bytearray))
        else:
            self._section_length = pack('@q', 0)

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

    def add(self, item):
        if isinstance(item, OptionEnd):
            raise ValueError("End option is added automatically!")

        if not isinstance(item, Option):
            raise ValueError("Expecting Option-derived object!")
        self._options.append(item)
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
        self._value = value

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
        print("code: {}, ol: {}, len(ov): {}".format(self._code, len(self._value), len(ov)))
        return bytearray(oc + ol + ov)

class OptionComment(Option):
    def __init__(self, comment):
        uc = bytes(comment, 'utf-8')
        super().__init__(code=1, value=uc)

class OptionEnd(Option):
    def __init__(self):
        super().__init__(code=0, value=b'')


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
    _block_type = 0x00000001
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

from urwid import (AttrWrap, BoxAdapter, Button, Columns, Frame, GridFlow, LineBox,
                   ListBox, Pile, SimpleFocusListWalker, Text)
from NordicUartPacket import *

class PacketFrame(Frame):
    # Frame has a Columns header and a listbox.
    # Maybe total packet count as the footer?

    def __init__(self):
        self.header = NordicUartPacketRow.get_header()
        self.plb = PacketListBox()
    #    ba = BoxAdapter(AttrWrap(self.plb, 'packet'))
        super().__init__(self.plb, AttrWrap(self.header, 'packet_header'))

    def append(self, pkt):
        self.plb.append(pkt)


class PacketListBox(ListBox):
    def __init__(self, max_buffer=50):
        self.max_buffer = max_buffer
        body = SimpleFocusListWalker([])
        super().__init__(body)

    def append(self, pkt):
        overage = len(self.body) - self.max_buffer
        del self.body[0:overage]
        row = AttrWrap(NordicUartPacketRow(pkt), 'packet')
        self.body.append(row)

class PacketRow(Columns):
    # Base class to split packet apart for showing in PacketListBox
    def __init__(self, packet):
        pass

    @classmethod
    def get_row(cls, packet):
        pass
        # Detect packet type, return appropriate row.
        # factory method

class NordicUartPacketRow(Columns):
    divchars = 0

    @classmethod
    def get_header(cls):
        cols = [
            (16, Text(u"Packet #")),
            (16, Text(u"Packet ID")),
            (16, Text(u"Payload Length"))
        ]
        return Columns(cols, dividechars=cls.divchars)

    def __init__(self, pkt):
        if not isinstance(pkt, NordicUartPacket):
            raise ValueError(u"{} doesn't derive from NordicUartPacket!".format(type(pkt)))

        cols = [
            (16, Text(u"{:d}".format(pkt.pc))),
            (16, Text(u"{:s}".format(pkt.id.name))),
            (16, Text(u"{:d} bytes".format(pkt.plen)))
        ]

        super().__init__(cols, dividechars=0)
        #Columns(widget_list, dividechars=0, focus_column=None, min_width=1, box_columns=None)


    # Render like:
    # CNT | ID | PLEN | PAYLOAD REPRESENTATION
    # Different background colors for up/down
    # different payload represnetations can have more columns...


class ButtonPanel(GridFlow):
    def __init__(self):
        buttons = [
            LineBox(Button(u"Scan")),
            LineBox(Button(u"Follow")),
            LineBox(Button(u"Send TK")),
            LineBox(Button(u"Disconnect"))
        ]

        super().__init__(buttons, cell_width=16, h_sep=1, v_sep=2, align='center')

    def pack(self, size):
        return (1, len(self.buttons))

from twisted.logger import Logger
from urwid import AttrWrap, BoxAdapter, Columns, Filler, LineBox, MainLoop, Text, TwistedEventLoop
from sharktoothle.widgets import PacketView, UartPacketRow

log = Logger(namespace="UI")

# User Interface
class SharktoothLE_TUI:
    def __init__(self, event_loop=TwistedEventLoop()):
        self._evl = event_loop
        self.setup_screen()

    def setup_screen(self):
        text_header = (u"SharktoothLE")
        header = AttrWrap(Text(text_header), 'header')
        self.pktlist = PacketView(UartPacketRow)

        pktlist = BoxAdapter(AttrWrap(self.pktlist, 'packet'), 20)
        pktlist = Padding(LineBox(pktlist, title="UART Packets"), align='center', left=2, right=2)
        buttons = Padding(ButtonPanel(), align='center', left=2)
        pile = Pile([header, Columns([(16, BoxAdapter(Filler(buttons, valign='middle'),20)), pktlist])])
        top = Filler(pile, valign='top')

        self.evl = TwistedEventLoop()
        self.loop = MainLoop(top, self.palette,
                      unhandled_input=self.unhandled_input, event_loop=self.evl)

    def update_screen(self, data):
        pl = self.pktlist

        for pkt in self._sniffer.pbuf:
            pl.append(pkt)
            self.cnt = self.cnt + 1
            self._pktsec.add_packet(EnhancedPacketBlock(pkt.data))

    #    with open('test.pcapng', 'wb') as f:
    #        f.write(self._pktsec.as_bytearray)
        self.loop.set_alarm_in(1/30, self.update_screen)

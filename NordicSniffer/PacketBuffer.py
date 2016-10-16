from packets import SlipPacket, UartPacket

class PacketBuffer():
    in_buf = bytearray()
    out_buf = []
    buffer_limit = 0

    def __init__(self, buffer_limit=65536):
        self.buffer_limit = buffer_limit

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.out_buf) == 0:
            raise StopIteration
        pkt = self.out_buf.pop(0)
        return pkt

    def add(self, rcvd_data):
        pbuf = self.in_buf
        pbuf.extend(bytearray(rcvd_data))
        headroom = self.buffer_limit - len(pbuf)
        if headroom < 0:
            print("in_buf exceeds limit by {:d} bytes, trimming".format(-headroom))
            del pbuf[:-headroom]
        pkt_cnt = self._process_in_buf()

        return pkt_cnt

    def size(self):
        return out_buf.size()

    def get(self):
        packet = None
        if len(self.out_buf) > 0:
            packet = self.out_buf.pop()
        return packet

    def _process_in_buf(self):
        """Uses the SlipPacket class to extract packets from the
        in_buffer.  These will then be converted into UartPackets
        and stored in the out_buffer."""
        packets = SlipPacket.find(self.in_buf)
        uart_pkts = []
        for pkt in packets:
            uart_pkt = UartPacket(pkt.data)
            uart_pkts.append(uart_pkt)

        self.out_buf.extend(uart_pkts)
        return len(uart_pkts)

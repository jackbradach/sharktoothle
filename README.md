# nerf-fiddytwo
Python API for Nordic RF52 BLE sniffer + Wireshark dissector

Rewrite of the Adafruit/Nordic Bluetooth LE Sniffer API and packet dissector.

Goals:
 - Rewrite Nordic-supplied dissectors to work with the tip of Wireshark.
 - Rework Python bridge to create a named pipe and allow live streaming.
 - Make it as easy to forget the internal details as possible; I really want to be able to run something like "wireshark_ble" and be looking at a live stream in Wireshark with no further fuss.
 - Build and run in a Docker container?
 - Merge anything useful that comes of this back into the main branch so others can play with it.

Current State:
 - Wireshark dissector updated to work with Wireshark 2.2.  This hasn't been tested extensively, but it opens the
   pcap files generated from the original version of the sniffer.
 - Dockerfile added to build and run Wireshark + BLE dissector in a container (w/GUI).
 - New Python API, based around Twisted is in-progress.  Currently can decode the UART, Sniffer, and BLE_LL packets.
 
Real Soon Now (tm):
 - Feature parity with existing API (needs to be able to follow and capture BLE conversations)
 - Live capture w/Wireshark
   - The intent is to make [USB Sniffer]<->[Python API]->[Pipe]->[Wireshark] work as simply as possible; ideally someone will be able to do their capture with a one-liner and have it "just work."  I already know that Wireshark's got limitations that come with feeding via pipe, so this might get interesting.
   
Maybe:
 - Support other pcap-based dissectors?
 - Support pcapng file format?
 - GUI for sending commands to the sniffer?

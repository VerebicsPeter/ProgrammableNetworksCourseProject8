#!/usr/bin/env python3
"""Receive packets on h3 and show DSCP marking from the VQ meter."""
import sys
from scapy.all import *


def get_iface():
    for iface in get_if_list():
        if "eth0" in iface:
            return iface
    print("ERROR: cannot find eth0")
    sys.exit(1)


def handle_packet(pkt):
    if IP in pkt and UDP in pkt:
        dscp = pkt[IP].tos >> 2  # DSCP is the upper 6 bits of the TOS field
        ecn  = pkt[IP].tos & 0x03
        src  = pkt[IP].src
        sport = pkt[UDP].sport

        marker = "MARKED" if dscp > 0 else "ok"
        print(f"  [{marker}] {src}:{sport} -> DSCP={dscp} ECN={ecn} len={len(pkt)}")


def main():
    iface = get_iface()
    my_mac = get_if_hwaddr(iface)

    print(f"Listening on {iface} (MAC {my_mac}) ...")
    print(f"Press Ctrl+C to stop.\n")

    sniff(
        iface=iface,
        filter="udp port 5000",
        prn=handle_packet,
        lfilter=lambda p: Ether in p and p[Ether].src != my_mac,
    )


if __name__ == "__main__":
    main()

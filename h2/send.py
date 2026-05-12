#!/usr/bin/env python3
"""Send a stream of UDP packets to h3 for VQ testing."""
import sys
import time
from scapy.all import *


DST_IP   = "10.0.0.3"
DST_MAC  = "00:00:0a:00:00:03"
DST_PORT = 5000
SRC_PORT = 5000

PAYLOAD  = "X" * 100  # 100-byte payload


def get_iface():
    for iface in get_if_list():
        if "eth0" in iface:
            return iface
    print("ERROR: cannot find eth0")
    sys.exit(1)


def main():
    count    = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1  # seconds

    iface  = get_iface()
    src_ip = get_if_addr(iface)

    pkt = (
        Ether(src=get_if_hwaddr(iface), dst=DST_MAC) /
        IP(src=src_ip, dst=DST_IP) /
        UDP(sport=SRC_PORT, dport=DST_PORT) /
        Raw(load=PAYLOAD)
    )

    print(f"Sending {count} UDP packets from {src_ip}:{SRC_PORT} -> {DST_IP}:{DST_PORT}")
    print(f"  interval={interval}s, payload={len(PAYLOAD)}B")

    for i in range(count):
        sendp(pkt, iface=iface, verbose=False)
        print(f"  [{i+1}/{count}] sent")
        time.sleep(interval)

    print("Done.")


if __name__ == "__main__":
    main()

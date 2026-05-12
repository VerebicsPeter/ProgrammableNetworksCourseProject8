# Virtual Queues

## Protocols

- Standard L2 - L4 protocols:
  - ethernet
  - ipv4
  - TCP or UDP
- In metadata we store the L4 protocol's src, dst port regardless of the protocol type

## Ingress processing

- L2 forwarding:
  - Standard logic, looks at the MAC address and decides the L2 port the packet should exist
- Per flow marking meter:
  - `vq_meter` keeps track of 8 flows at max (8 metering cells)
  - `vq_meter` uses `MeterType.bytes` to subtract the ipv4 length from its buckets
- Flow marking:
  - This is done using the `flow_marking` table
  - The table matches a specific flow by matching the full 5 tuple:
    (ipv4.srcAddr, ipv4.dstAddr, meta.l4_srcPort, meta.l4_dstPort, ipv4.protocol)
  - On a match we execute the meter (which subtract length from bucket), if the color is not green it stores 1 into `ipv4.dscp`
- L2 forwarding is always tried
- Flow marking table is only applied if the `ipv4` header is valid

## Egress processing

- TODO: we will need to drop packets here based on the VQ

## Checksum computation and Deparser

- We update the checksum because the `ipv4.dscp` might be updated
- The deparser emits the headers in the standard order

## Topology and Configuration

Topology (for now):

```text
h1 -(A)- |----|
         | S1 | -(C)- h3
h2 -(B)- |----|
```

We add 2 entries in the flow_marking table for meter index 0 and 1 with UDP flows:

```bash
table_add flow_marking mark_flow 10.0.0.1 10.0.0.3 5000 5000 17 => 0
table_add flow_marking mark_flow 10.0.0.2 10.0.0.3 5000 5000 17 => 1
```

We set the meter rates for both 0 and 1 indexes to the same rate:

```bash
meter_set_rates vq_meter 0 0.001:200 0.001:400
meter_set_rates vq_meter 1 0.001:200 0.001:400
```

Rate is in bytes per microseconds:

- yel : 0.001:200 is 1KB/s with 200 bytes bucket
- red : 0.001:400 is 1KB/s with 400 bytes bucket

TODO: Figure out how to represent alpha (the multiplier used to calculate the VQ rate relative to the real limit R)...

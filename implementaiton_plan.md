# Per-flow Virtual Queues (VQs)

## Original Task Description

- Virtual Queue
  - Have smaller service rate than the real port
  - Emulated by token/leaky buckets – see meters in P4
- One physycal queue with service rate $R$
  - Virtual queues with service rate $R*\alpha$, $\alpha$ in (0,1)
  - Virtual queue for each active flow
  - Flow identififcation – tables, or hash
  - If per-flow VQ is full, we drop the packet.

## Research and Implementation Plan 

Research Questions:
 - Can a P4 meter reasonably emulate a virtual queue running at $R*\alpha$ relative to the real rate $R$?
 - How well does hash-based vs table-based flow identification hold up under many concurrent flows?
 - Does dropping at the per-flow VQ level actually improve fairness compared to regular tail-drop?

Research Plan:
 - read the 2 papers again and read some of the related work
   - https://www.bobbriscoe.net/projects/latency/l4saqm_tr.pdf
   - https://www.bobbriscoe.net/projects/ipe2eqos/pcn/vq2lb/vq2lb_tr.pdf

Implementation Plan:

**Phase 1:** Flow identification

We need to be able to tell flows apart in the ingress pipeline.
The plan is to start with a simple 5-tuple match-action table (src ip, dst ip, src port, dst port, protocol),
then also try hashing the 5-tuple into a register array to see how it scales when there are a lot of active flows.

**Phase 2:** Virtual queue emulation.

Each **flow gets its own meter** in P4, configured at slower rate $R*\alpha$ (e.g.: start with $\alpha$ = 63/64 as suggested by Briscoe).
When a packet exceeds the virtual rate the meter returns RED, which we treat as the VQ being full.

**Phase 3:** Drop/mark logic.

If the per-flow VQ is full, we drop the packet in the egress pipeline, can also try setting ECN bits instead of dropping.

**Phase 4:** Testing. 

We'll test on Kathara using Scapy for traffic generation.
Main scenarios to cover:
 - a single flow baseline
 - multiple flows competing for the same link (to check fairness)
 
 We'll measure queue depth, link utilisation and drop rates, and compare against a no VQ baseline.

Expected Outcome
Hopefully the prototype will show that per-flow VQs can keep real queue occupancy low and distribute drops fairly across flows.

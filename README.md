# OPNsense IPv6 Prefix Update

This is a small helper to update traffic shaper rules in OPNsense for changed IPv6 prefixes.
The goal is to get to 100% dual-stack in my home network (/w stateless NAT-free IPv6) and have parity between both IPv4 and IPv6.
Many components and systems handle dynamic prefixes well, but traffic shaper turned out to be one of component without a native solution for changes in ISP-delegated IPv6 prefixes (I do not pay for static IPv4 or IPv6).

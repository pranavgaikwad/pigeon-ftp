# PFTP Client

PFTPClient implements the sending side of data transfer. It can be used to send data to multiple receivers.

It provides `rdt_send()` interface to send arbitrary data to `n` number of receivers where `n` can be configured at startup. Optionally, it can use custom `MSS (Maximum Segment Size)` and `timeout` values. 

## rdt\_send()

`rdt_send(bytes)` is the main communication primitive provided by PFTPClient. It internally buffers bytes to make fixed size `(MSS)` segments before they are transferred over an un-reliable channel. A timeout counter on each segment identifies lost segments. UDP checksum fields in segment headers provide error control.

![rdt_send()](./rdt_send.png)

## Protocol

PFTPClient ensures reliable data transfer by using Stop-and-Wait Automatic Repeat Request protocol. The `proto` package provides primitives to achieve that. See [Protocol.md](./Protocol.md)

## Header

Each segment is attached a header that has following fields

- *Seq :* a 32-bit Sequence Number
- *Checksum :* UDP checksum of segment
- *Type :* a 16-bit field that specifies this is a data packet

## Bookkeeping

PFTPClient keeps track of `ACKs` using an in-memory map indexed by remote addresses of destination hosts.  The value of the each key is a `sequence_number`. It specifies the last segment number sent to the receiver. Whenever `ACK` for a particular segment is received, it is removed from the map. The map always contains only segments that are awaiting their `ACKs`.

Continue Reading :
- [Client Design](./Client.md)
- [Server Design](./Server.md)

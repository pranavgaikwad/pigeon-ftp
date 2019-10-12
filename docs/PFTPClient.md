# PFTP Client

PFTPClient implements the sending side of data transfer. 

It provides `rdt_send()` interface to send arbitrary data to a receiver. It can be configured to use a custom `MSS (Maximum Segment Size)` value and a `timeout` value. 

## rdt\_send()

`rdt_send(bytes)` is the main communication primitive provided by PFTPClient. It internally buffers bytes to make fixed size `(MSS)` segments before they are transferred over an un-reliable channel. A timeout counter on each segment identifies lost segments. 

## Protocol

PFTPClient ensures reliable data transfer by using Stop-and-Wait Automatic Repeat Request protocol. The `proto` package provides primitives to achieve that. See [Protocol.md](./Protocol.md)

## Header

Each segment is attached a header that has following fields

- *Seq :* a 32-bit Sequence Number
- *Checksum :* UDP checksum of segment
- *Type :* a 16-bit field that specifies this is a data packet

## Bookkeeping

PFTPClient keeps track of `ACKs` using an in-memory list. Each entry in the list is a tuple : `(<receiver_addr>:string, <sequence_number>:int)`. 

`sequence_number` field specifies the last segment number sent to the receiver specified by `<receiver_addr>`. Whenever `ACK` for a particular segment is received, it is removed from the list. The list always contains only segments that are awaiting their `ACKs`.

Continue Reading :
- [Client Design](./Client.md)
- [Server Design](./Server.md)

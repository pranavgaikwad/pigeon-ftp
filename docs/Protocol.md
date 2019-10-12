# Protocol

`proto` package provides different protocol primitives. 

## make\_segment(data, type)

`make_segment()` interface provides a reliable way of creating packets of a certain `type`. Based on `type`, a suitable header will be attached to the original data.

Note that the `data` is a stream of bytes. 

There are mainly two types of segments :
- Data
- Acknowledgement

## Header 

Each segment has a custom header with three fields :
- *Number :* 32-bit sequence number
- *Checksum :* 16-bit UDP checksum
- *Type :*  16-bit field to specify `type` of the segment

## Objective

Implementing point-to-multipoint reliable data transfer protocol using the Stop-and-Wait automatic repeat request (ARQ) scheme, and carrying out a number of experiments to evaluate its performance. 

## Features

Pigeon FTP is referred to as - P2MP-FTP in this document.

### Point to multipoint file transfer

The FTP protocol provides a sophisticated file transfer service, but since it uses TCP to ensure reliable data transmission it only supports the transfer of files from one sender to one receiver. In many applications (e.g., software updates, stock quote updates, document sharing, etc) it is important to transfer data reliably from one sender to multiple receivers. You will implement P2MP-FTP, a protocol that provides a simple service: transferring a file from one host to multiple destinations. P2MP-FTP will use UDP to send packets from the sending host to each of the destinations, hence it has to implement a reliable data transfer service using some ARQ scheme; for this project, you will implement the Stop-and-Wait ARQ. Using the unreliable UDP protocol allows us to implement a “transport layer” service such as reliable data transfer in user space.

### Client Server Architecture

To keep things simple, you will implement P2MP-FTP in a client-server architecture and omit the steps of opening up and terminating a connection. The P2MP-FTP client will play the role of the sender that connects to a set of P2MP-FTP servers that play the role of the receivers in the reliable data transfer. All data transfer is from sender (client) to receivers (servers) only; only ACK packets travel from receivers to sender.

### The P2MP-FTP Client (Sender)

The P2MP-FTP client implements the sender in the reliable data transfer. When the client starts, it reads data from a file specified in the command line, and calls `rdt_send()` to transfer the data to the P2MP-FTP servers. For this project, we will assume that `rdt_send()` provides data from the file on a byte basis. The client also implements the sending side of the reliable Stop-and-Wait protocol, receiving data from `rdt_send()`, buffering the data locally, and ensuring that the data is received correctly at the server.
The client also reads the value of the maximum segment size (MSS) from the command line. The Stop-and-Wait protocol buffers the data it receives from `rdt_send()` until it has at least one MSS worth of bytes. At that time it forms a segment that includes a header and MSS bytes of data; as a result, all segments sent, except possibly for the very last one, will have exactly MSS bytes of data.

The client transmits each segment separately to each of the receivers, and waits until it has received ACKs from every receiver before it can transmit the next segment. Every time a segment is transmitted, the sender sets a timeout counter. If the counter expires before ACKs from all receivers have been received, then the sender re-transmits the segment, but only to those receivers from which it has not received an ACK yet. This process repeats until all ACKs have been received (i.e., if there are n receivers, n ACKS, one from each receiver have arrived at the sender), at which time the sender proceeds to transmit the next segment.

The header of the segment contains three fields:

- a 32-bit sequence number,
- a 16-bit checksum of the data part, computed in the same way as the UDP checksum
- a 16-bit field that has the value 0101010101010101, indicating that this is a data packet

For this project, you may have the sequence numbers start at 0.

The client implements the sending side of the Stop-and-Wait protocol as described in the book, including setting the timeout counter, processing ACK packets (discussed shortly), and retransmitting packets as necessary.

### The P2MP-FTP Server (Receiver)

The server listens on the well-known port 7735. It implements the receive side of the Stop-and-Wait protocol, as described in the book. Specifically, when it receives a data packet, it computes the checksum and checks whether it is in-sequence, and if so, it sends an ACK segment (using UDP) to the client; it then writes the received data into a file whose name is provided in the command line. If the packet received is out-of-sequence, an ACK for the last received in-sequence packet is sent; if the checksum is incorrect, the receiver does nothing.

The ACK segment consists of three fields and no data:

- the 32-bit sequence number that is being ACKed
- a 16-bit field that is all zeroes
- a 16-bit field that has the value 1010101010101010, indicating that this is an ACK packet

### Generating errors

Despite the fact that UDP is unreliable, the Internet does not in general lose packets. Therefore, we need a systematic way of generating lost packets so as to test that the Stop-and-Wait protocol works correctly (and to obtain performance measurements, as will be explained shortly).

To this end, you will implement a probabilistic loss service at the server (receiver). Specifically, the server will read the probability value p, 0 < p < 1 from the command line, representing the probability that a packet is lost. Upon receiving a data packet, and before executing the Stop-and-Wait protocol, the server will generate a random number r in (0, 1). If r ≤ p, then this received packet is discarded and no other action is taken; otherwise, the packet is accepted and processed according to the Stop-and-Wait rules.



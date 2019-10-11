# Overview

There are mainly two entities in the system : `client` and `servers`. 

- *Client :* sends data to multiple `Servers` at a time
- *Server :* receives data from the `Client`

There is only one instance of `Client` and multiple instances of `Server` running at any given time.

The `Client` runs in a loop with an objective to send a file to `n` servers. As soon as, file is sent to all the servers, the `Client` exits. 

The `Servers` on the other hand, are always running and are expecting a file from the `Client`.

More information :
- [Client Architecture](./Client.md)
- [Server Architecture](./Server.md)





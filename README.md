# PyPortCheck
Simple program to check if a machine behind a NAT has a succesfuly open port.
### Usage
```sh
$ pyportcheck.py port protocol`
```

### Example
```sh
$ pyportcheck.py 8080 TCP
Public IP: 64.23.12.56
Starting TCP server 0.0.0.0:8080
Creating TCP socket connection to 64.23.12.56:8080
Port 8080 TCP is OPEN
Shutting down TCP server
```
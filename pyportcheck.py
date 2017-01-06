import socket
import requests
import threading
import argparse
import time

PUBLIC_IP_SERVICES = ["http://api.ipify.org"]

def obtain_public_ip():
    my_ip = None
    for ip_service in PUBLIC_IP_SERVICES:
        try:
            my_ip = requests.get(ip_service).content
            break
        except Exception:
            continue
    return my_ip

def run_server(port, protocol):
    sock_type = None
    print "Starting {0} server 0.0.0.0:{1}".format(protocol, port)
    if protocol == "TCP":
        sock_type = socket.SOCK_STREAM
        serversocket = socket.socket(socket.AF_INET, sock_type)
        serversocket.bind(("0.0.0.0", port))
        serversocket.settimeout(3)
        serversocket.listen(1)
        try:
            (clientsocket, address) = serversocket.accept()
            print "Recieved connection from {0[0]}:{0[1]}".format(address)
        except socket.timeout:
            pass
        serversocket.close()
    elif protocol == "UDP":
        sock_type = socket.SOCK_DGRAM
        serversocket = socket.socket(socket.AF_INET, sock_type)
        serversocket.bind(("0.0.0.0", port))
        serversocket.settimeout(10)
        try:
            data = serversocket.recv(512)
            time.sleep(1)
            if data == "HELLO PORT":
                print "UDP packet succesfuly recieved, port {0} {1} is OPEN!".format(port, protocol)
            else: # This shouldn't ever happen
                print "UDP packet recieved with different data ???"
        except socket.timeout:
            print "UDP server timed out, port {0} {1} is likely NOT OPEN or not reachable".format(port, protocol)    
        serversocket.close()
    print "Shutting down {0} server".format(protocol)

def check_open_port(ip, port, protocol):
    server_thread = threading.Thread(target=run_server, args=(port, protocol))
    server_thread.start()
    # Give time to start server
    time.sleep(1)
    sock_type = None
    if protocol == "TCP":
        print "Creating TCP socket connection to {0}:{1}".format(ip, port)
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientsocket.connect((public_ip, port))
            time.sleep(0.2)
            clientsocket.close()
            print "Port {0} {1} is OPEN!".format(port, protocol)
        except Exception:
            print "Port {0} {1} is NOT OPEN".format(port, protocol)
            
    elif protocol == "UDP":
        print "Sending UDP packet to {0}:{1}".format(ip, port)
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientsocket.sendto("HELLO PORT", (ip, port))
        print "Waiting UDP packet to reach..."

    server_thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", metavar="port", type=int, help="Port to check")
    parser.add_argument("protocol", metavar="protocol", type=str, choices=["TCP", "UDP"], help="Protocol, either TCP or UDP")
    args = parser.parse_args()
    port = args.port
    protocol = args.protocol
    public_ip = obtain_public_ip()
    print "Public IP: {0}".format(public_ip)
    check_open_port(public_ip, port, protocol)



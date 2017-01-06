import socket
import requests
import threading
import argparse
import time

PUBLIC_IP_SERVICES = ["http://api.ipify.org"]

client_lock = threading.Lock()
shared_data = {"port_in_use" : False, "connected_to_server" : False}

"""
Obtains the current public ip using the public ip services from above
"""
def obtain_public_ip():
    my_ip = None
    for ip_service in PUBLIC_IP_SERVICES:
        try:
            my_ip = requests.get(ip_service).content
            break
        except Exception:
            continue
    return my_ip

"""
Runs TCP or UPD server in the specified port
"""
def run_server(port, protocol):
    sock_type = None
    global shared_data
    print "Starting {0} server 0.0.0.0:{1}".format(protocol, port)
    if protocol == "TCP":
        sock_type = socket.SOCK_STREAM
        serversocket = socket.socket(socket.AF_INET, sock_type)
        try:
            serversocket.bind(("0.0.0.0", port))
        except Exception:
            shared_data["port_in_use"] = True
            return
        serversocket.settimeout(5)
        serversocket.listen(1)
        try:
            (clientsocket, address) = serversocket.accept()
            client_lock.acquire()
            client_lock.release()
            print "Recieved connection from {0[0]}:{0[1]}".format(address)
            print "Port {0} {1} is OPEN!".format(port, protocol)
        except socket.timeout as ex:
            client_lock.acquire()
            client_lock.release()
            if shared_data["connected_to_server"]:
                print "Port {0} {1} looks OPEN, but it's not forwarded to this machine".format(port, protocol)
            else:
                print "Port {0} {1} is NOT OPEN".format(port, protocol)
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
            else: # We might recieve data from other client. Not what we are looking for, but it means the port is open
                print "UDP packet recieved from other client, port is OPEN"
        except socket.timeout:
            print "UDP server timed out, port {0} {1} is likely NOT OPEN or not reachable".format(port, protocol)    
        serversocket.close()
    print "Shutting down {0} server".format(protocol)

"""
Prints if the port is open or not
"""
def check_open_port(ip, port, protocol):
    global shared_data
    # Lock until the connection is terminated
    client_lock.acquire()
    server_thread = threading.Thread(target=run_server, args=(port, protocol))
    server_thread.start()
    # Give time to start server
    time.sleep(2)
    if shared_data["port_in_use"]:
        print "Couldn't check port {0} {1}, the port is already in use".format(protocol, port)
        return
    
    if protocol == "TCP":
        print "Creating TCP socket connection to {0}:{1}".format(ip, port)
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientsocket.settimeout(10)
            clientsocket.connect((ip, port))
            time.sleep(0.2)
            clientsocket.close()
            print "Connected..."
            shared_data["connected_to_server"] = True
        except socket.error as ex:
            print "Couldn't connect to {0}:{1}".format(ip, port)
    elif protocol == "UDP":
        print "Sending UDP packet to {0}:{1}".format(ip, port)
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientsocket.sendto("HELLO PORT", (ip, port))
        print "Waiting UDP packet to reach..."

    client_lock.release()
    server_thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", metavar="port", type=int, help="Port to check")
    parser.add_argument("protocol", metavar="protocol", type=str.upper, choices=["TCP", "UDP"], help="Protocol, either TCP or UDP")
    args = parser.parse_args()
    public_ip = obtain_public_ip()
    print "Public IP: {0}".format(public_ip)
    check_open_port(public_ip, args.port, args.protocol)

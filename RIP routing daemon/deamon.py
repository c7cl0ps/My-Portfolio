import sys
import socket
import time
import threading
import signal
import logging
from file_reader import read_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables
input_sockets = {}
stop_event = threading.Event()
socket_lock = threading.Lock()

# Function to safely close sockets
def safe_close(sock):
    with socket_lock:
        if sock.fileno() != -1:
            try:
                sock.close()
            except OSError:
                pass

# SIGINT (Ctrl+C) handler
def signal_handler(sig, frame):
    logging.info("Terminating the daemon...")
    stop_event.set()
    time.sleep(2)  # Allow time for threads to exit before closing sockets
    for sock in input_sockets.values():
        safe_close(sock)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Function to create a RIP entry
def make_rip_entry(routerID, next_hop, metric):
    rip_entry = bytearray([
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        (routerID >> 24) & 0xFF, (routerID >> 16) & 0xFF, (routerID >> 8) & 0xFF, routerID & 0xFF,
        (next_hop >> 24) & 0xFF, (next_hop >> 16) & 0xFF, (next_hop >> 8) & 0xFF, next_hop & 0xFF,
        (metric >> 24) & 0xFF, (metric >> 16) & 0xFF, (metric >> 8) & 0xFF, metric & 0xFF
    ])
    return rip_entry

# Function to create a RIP packet
def makeRIP_pckt(command, version, router_id, rip_entries, metric):
    router_id = int(router_id)
    rip_pckt = bytearray([
        command, version, (router_id >> 8) & 0xFF, router_id & 0xFF
    ])
    for rip_entry in rip_entries:
        rip_pckt.extend(rip_entry)
    rip_pckt.extend([
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        (metric >> 24) & 0xFF, (metric >> 16) & 0xFF, (metric >> 8) & 0xFF, metric & 0xFF
    ])
    return rip_pckt

# Function to send RIP response packets
def send_rip_response(sock, port, router_id, routing_table):
    rip_entries = [make_rip_entry(int(dest), next_hop, metric) for dest, (next_hop, metric) in routing_table.items()]
    rip_pckt = makeRIP_pckt(0x0002, 0x0002, router_id, rip_entries, 1)
    
    try:
        sock.sendto(rip_pckt, ('127.0.0.1', port))
        logging.info(f"Sent RIP response to port {port}")
    except OSError as e:
        logging.warning(f"Socket error while sending to {port}: {e}")

# Function to handle incoming packets
def handle_incoming_packets(sock, routing_table):
    while not stop_event.is_set():
        try:
            if sock.fileno() == -1:
                logging.warning(f"Socket {sock.getsockname()[1]} was closed. Exiting thread.")
                break  

            data, addr = sock.recvfrom(512)
            logging.info(f"Received packet from {addr}")
            update_routing_table(data, routing_table)

        except (ConnectionResetError, OSError) as e:
            logging.warning(f"Socket error: {e}. Exiting thread.")
            break  # Exit the thread safely

        except Exception as e:
            logging.error(f"Unexpected error: {e}")

# Function to update the routing table
def update_routing_table(packet, routing_table):
    if len(packet) < 4:
        logging.warning("Received invalid RIP packet")
        return

    command, version = packet[:2]
    if command != 0x0002 or version != 0x0002:
        logging.warning("Received invalid RIP packet")
        return

    for i in range(4, len(packet), 20):
        if i + 20 > len(packet):
            logging.warning("Received incomplete RIP entry")
            continue

        entry = packet[i:i+20]
        dest = (entry[8] << 24) | (entry[9] << 16) | (entry[10] << 8) | entry[11]
        next_hop = (entry[12] << 24) | (entry[13] << 16) | (entry[14] << 8) | entry[15]
        metric = (entry[16] << 24) | (entry[17] << 16) | (entry[18] << 8) | entry[19]

        if metric < 16:
            routing_table[dest] = (next_hop, metric)

# Main function
def main():
    global input_sockets

    if len(sys.argv) != 2:
        logging.error("Usage: python daemon.py <config_file_path>")
        sys.exit(1)

    config_file_path = sys.argv[1]
    try:
        router_id, in_ports, out_ports = read_config(config_file_path)
    except Exception as e:
        logging.error(f"Error reading configuration file: {e}")
        sys.exit(1)

    logging.info(f"Router ID: {router_id}")
    logging.info(f"Input Ports: {in_ports}")
    logging.info(f"Output Ports: {out_ports}")

    input_sockets = {port: socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for port in in_ports}
    for port, sock in input_sockets.items():
        sock.bind(("127.0.0.1", port))
        threading.Thread(target=handle_incoming_packets, args=(sock, {})).start()

    def send_periodic_updates():
        while not stop_event.is_set():
            for port in out_ports:
                send_rip_response(input_sockets[in_ports[0]], port[0], router_id, {})
            time.sleep(30)

    threading.Thread(target=send_periodic_updates).start()

    while not stop_event.is_set():
        time.sleep(1)

if __name__ == "__main__":
    main()

import sys

def check_id(router_id):
    try:
        router_id = int(router_id)
        return 1 <= router_id <= 64000
    except ValueError:
        return False

def check_in_ports(port):
    try:
        port = int(port)
        return 1024 <= port <= 64000
    except ValueError:
        return False

def check_out_ports(port, cost, router_id):
    try:
        port = int(port)
        cost = int(cost)
        router_id = int(router_id)
        return 1024 <= port <= 64000 and 1 <= router_id <= 64000 and 1 <= cost <= 15
    except ValueError:
        return False

def read_config(filename):
    router_id = None
    in_ports = []
    out_ports = []

    with open(filename, 'r') as f:
        lines = f.readlines()

    for line in lines:
        words = line.split()
        if words[0] == "router-id":
            if check_id(words[1]):
                router_id = int(words[1])
            else:
                raise ValueError("Invalid router ID")
        elif words[0] == "input-ports":
            for port in words[1:]:
                port = port.strip(', ')  # Remove any trailing commas or spaces
                if check_in_ports(port):
                    in_ports.append(int(port))
                else:
                    raise ValueError(f"Invalid input port: {port}")
        elif words[0] == "outputs":
            for output in words[1:]:
                output = output.strip(', ')  # Remove any trailing commas or spaces
                port, cost, router_id = output.split('-')
                if check_out_ports(port, cost, router_id):
                    out_ports.append((int(port), int(cost), int(router_id)))
                else:
                    raise ValueError(f"Invalid output port: {output}")

    if router_id is None or not in_ports or not out_ports:
        raise ValueError("Configuration file is missing required sections")

    return router_id, in_ports, out_ports

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file_reader.py <config_file_path>")
        sys.exit(1)

    config_file_path = sys.argv[1]
    try:
        router_id, in_ports, out_ports = read_config(config_file_path)
        print("Router ID:", router_id)
        print("Input Ports:", in_ports)
        print("Output Ports:", out_ports)
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)
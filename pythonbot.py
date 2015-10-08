import json
import socket
from Bot import Bot

run_loop = 1

with open('config.json', 'r') as f:
    config = json.load(f)

print(config['host'])

irc_bot = Bot(config['host'], config['port'], config['nick'], config['ident'], config['realname'], config["testchannel"])
s = irc_bot.connect_to_server
irc_bot.set_nick()
irc_bot.join_channel()

# Run loop.
while run_loop == 1:
    irc_bot.readbuffer = irc_bot.readbuffer + s.recv(1024).decode('utf-8')
    temp = irc_bot.readbuffer.split("\n")
    irc_bot.readbuffer = temp.pop()

    for line in temp:
        run_loop = irc_bot.parse_irc_line(line, run_loop)

s.shutdown(socket.SHUT_RDWR)
s.close()
print("Bye bye!")

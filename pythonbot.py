#!/usr/bin/python

import socket
from urllib.request import Request, urlopen


class Bot:

    def __init__(self, host, port, nick, ident, realname, testchannel):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        self.testchannel = testchannel
        self.readbuffer = ""

    def connect_to_server(self):
        s = socket.socket()
        s.connect((self.host, self.port))
        print("Connecting to freenode.")

        return s

    def set_nick(self):
        s.send(("NICK %s\r\n" % self.nick).encode('utf-8'))
        print("Sending Nick request.")
        s.send(("USER %s %s bla :%s\r\n" % (self.ident, self.host, self.realname)).encode('utf-8'))
        print("Sending User info.")

    def join_channel(self):
        s.send(("JOIN #%s\r\n" % self.testchannel).encode('utf-8'))
        print("Joining #%s." % self.testchannel)

    @staticmethod
    def ping_pong():
        s.send(("PONG %s\r\n" % line[1]).encode('utf-8'))

    def parse_irc_line(self, line, run_loop):
        print(line)
        line_split = line.split()

        if line_split[0] == "PING":
            self.ping_pong()
        elif line_split[0] == (":" + self.host) or line_split[0] == (":" + self.nick) or len(line_split) < 4:
            pass
        elif line_split[3] == (":" + self.nick):
            run_loop = self.parse_message(line_split, run_loop)
        return run_loop

    def parse_message(self, line_split, run_loop):
        sender = line_split[0].split("~")[1].split("@")[0]
        message = line_split[4:]
        if message[0] == "Hello!":
            print("Responding to \"Hello\" from %s." % sender)
            s.send(("PRIVMSG #%s :%s Hello!\r\n" % (self.testchannel, sender)).encode('utf-8'))
        elif message[0] == "Bye!":
            print("Quiting IRC.")
            s.send("QUIT\r\n".encode('utf-8'))
            run_loop = 0
        elif message[0] == "stock":
            print("Getting stockquote for %s." % message[1])
            info = self.get_stock(message[1])
            amount = info[0]
            name = info[1]
            s.send(("PRIVMSG #%s :%s %s is at %s.\r\n" % (self.testchannel, sender, name, amount)).encode('utf-8'))
        return run_loop

    @staticmethod
    def get_stock(symbol):
        quote = urlopen(Request('http://finance.yahoo.com/d/quotes.csv?s=%s&f=l1' % symbol))
        name = urlopen(Request('http://finance.yahoo.com/d/quotes.csv?s=%s&f=n' % symbol))
        return str(quote.read().decode('utf-8').strip()), str(name.read().decode('utf-8').strip())

run_loop = 1

irc_bot = Bot("weber.freenode.net", 6667, "test_bot", "test_bot", "test_bot", "bottestbottest")
s = irc_bot.connect_to_server()
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

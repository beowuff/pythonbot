import feedparser
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
        self.connection = None

    @property
    def connect_to_server(self):
        self.connection = socket.socket()
        self.connection.connect((self.host, int(self.port)))
        print("Connecting...")

        return self.connection

    def set_nick(self):
        self.connection.send(("NICK %s\r\n" % self.nick).encode('utf-8'))
        print("Sending Nick request.")
        self.connection.send(("USER %s %s bla :%s\r\n" % (self.ident, self.host, self.realname)).encode('utf-8'))
        print("Sending User info.")

    def join_channel(self):
        self.connection.send(("JOIN %s\r\n" % self.testchannel).encode('utf-8'))
        print("Joining %s." % self.testchannel)

    def ping_pong(self, line):
        self.connection.send(("PONG %s\r\n" % line[1]).encode('utf-8'))

    def parse_irc_line(self, line, run_loop):
        print(line)
        line_split = line.split()

        if line_split[0] == "PING":
            self.ping_pong(line_split)
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
            self.connection.send(("PRIVMSG %s :Hello %s!\r\n" % (self.testchannel, sender)).encode('utf-8'))
        elif message[0] == "Bye!":
            self.connection.send(("PRIVMSG %s :Good bye!\r\n" % self.testchannel).encode('utf-8'))
            print("Quiting IRC.")
            self.connection.send("QUIT\r\n".encode('utf-8'))
            run_loop = 0
        elif message[0] == "news":
            try:
                if message[1] == "defcon":
                    url = 'https://defcon.org/defconrss.xml'
                elif message[1] == "reddit":
                    try:
                        if message[2] == "security":
                            linkpath = "security"
                        elif message[2] == "netsec":
                            linkpath = "netsec"
                        else:
                            linkpath = ""
                        url = ("https://www.reddit.com/r/%s/.rss" % linkpath)
                    except IndexError:
                        url = "https://www.reddit.com/.rss"
                else:
                    url = "https://news.google.com/news?&topic=tc&output=rss"
            except IndexError:
                url = "https://news.google.com/news?&topic=tc&output=rss"
            self.get_news(url)
        elif message[0] == "stock":
            try:
                self.get_stock(message[1])
            except IndexError:
                send_message = ("PRIVMSG %s :%s Missing stock symbol.\r\n" % (self.testchannel, sender)).encode('utf-8')
                self.connection.send(send_message)

        return run_loop

    def get_stock(self, symbol):
        quote = urlopen(Request('http://finance.yahoo.com/d/quotes.csv?s=%s&f=l1' % symbol))
        compname = urlopen(Request('http://finance.yahoo.com/d/quotes.csv?s=%s&f=n' % symbol))
        amount = quote.read().decode('utf-8').strip()
        name = str(compname.read().decode('utf-8').strip())
        self.connection.send(("PRIVMSG #%s :%s is at %s.\r\n" % (self.testchannel, name, amount)).encode('utf-8'))

    def get_news(self, url):
        rawdata = feedparser.parse(url)
        self.connection.send(("PRIVMSG %s :%s\r\n" % (self.testchannel, rawdata.entries[0].title)).encode('utf-8'))
        self.connection.send(("PRIVMSG %s :%s\r\n" % (self.testchannel, rawdata.entries[0].link)).encode('utf-8'))

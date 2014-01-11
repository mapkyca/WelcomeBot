# Import some necessary libraries.
import socket 
import time
import csv
import Queue
import random
from threading import Thread

# Some basic variables used to configure the bot        
server = "irc.freenode.net" 
channel = "#openhatch" 
botnick = "WelcomeBot" 
waitTime = 60        # Amount of time after joining before bot replies to someone

# Connects to server and joins channel
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
ircsock.send("NICK "+ botnick +"\n") # here we actually assign the nick to the bot

def joinchan(chan): 
    ircsock.send("JOIN "+ chan +"\n")

joinchan(channel)

# Creates separate thread for reading messages from the server
def getIRC():
    while True:
        ircmsg = ircsock.recv(2048) # receive data from the server   
        ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
        q.put(ircmsg) # Put in queue for main loop to read
        print(ircmsg) 

q = Queue.LifoQueue()
t = Thread(target=getIRC)
t.daemon = True
t.start()

# Classes
class newcomer(object):  # Newcomer class created when someone joins the room

        def __init__(self, nick):
            self.nick = nick
            self.born = time.time()
            self.status = 0

        def updateStatus(self,status=0):
            self.status = status

        def aroundFor(self):
            return time.time() - self.born

# Functions
def ping(): # Responds to server Pings.
    ircsock.send("PONG :pingis\n")  

def hello(actor,greeting): # This function responds to a user that inputs "Hello Mybot"
    ircsock.send("PRIVMSG " + channel +" :" + greeting + " " + actor + "\n")

def help(actor): # This function explains what the bot is when queried.
    ircsock.send("PRIVMSG " + channel +" :I'm a bot!  I'm from here: https://github.com/shaunagm/oh-irc-bot. You can change my behavior by submitting a pull request or by talking to shauna. \n")

def welcome(newcomer):  # This welcomes a specific person.
    ircsock.send("PRIVMSG "+ channel +" :Welcome "+ newcomer + "!  The channel's pretty quiet right now, so I thought I'd say hello, and ping my maintainers(shauna, paulproteus) that you're here.  If no one responds for a while, try emailing us at hello@openhatch.org or just coming back later.\n")

def makeNickArray():  # On startup, makes array of nicks from Nicks.txt.  New info will be written to both array and txt file.
    nickArray = []
    with open('nicks.csv', 'rb') as csvfile:
        nicksData = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in nicksData:
             nickArray.append(row)
    # Do I need to explicitly close this?

def addPerson(person):  # After a newcomer has been greeted (either by the bot, or someone else) their information will be set recorded.
    nicksData.append(person)
    with open('nicks.csv', 'wb') as csvfile:
        nickwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        nickwriter.writerow([person])

#### Main function

newList = []  # This is the array of newcomer objects that people who join the room are added to.
helloArray = ['Hello','hello','Hi','hi','Hey','hey','Yo','yo ','Sup','sup']
helpArray = ['Help','help','Info','info','faq','FAQ','explain yourself','EXPLAIN YOURSELF']

while 1: 

    for i in newList: 
        i.updateStatus()
        if i.status == 0 and i.aroundFor > waitTime:
            welcome(i.nick)
            i.updateStatus(1)
            addPerson(i)

        if q.empty() == 0:
            ircmsg = q.get()
            actor = ircmsg.split(":")[1].split("!")[0]

            # Welcome functions
            if ircmsg.find("PRIVMSG "+ channel) != -1: # If someone has spoken into the channel
                for i in newList:
                    if actor != i.nick: # Don't turn off response if the person speaking is the person who joined.
                        i.updateStatus(1)	# Sets status to 1
                        addPerson(i)
                    ## Else: Do we want to do something if the person who joined the chat says something?

            if ircmsg.find("JOIN "+ channel) != -1:  # If someone joins #channel
                if actor != botnick:  # Remove the case where the bot gets a message that the bot has joined.
                    if actor not in nickArray: 
                        newList.append(newcomer(actor)) # Create a newcomer object and append to list.

            # Unwelcome functions
            if ircmsg.find(botnick) != -1 and ircmsg.find("PRIVMSG #") != -1: # If someone talks to (or refers to) the bot
                if any(x in ircmsg for x in helloArray):
                    hello(actor,random.choice(helloArray))
                if any(y in ircmsg for y in helpArray):
                    help(actor)

            if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
                ping()


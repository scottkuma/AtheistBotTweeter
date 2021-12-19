#!/usr/bin/env python
import sys
import os
import random

from twython import Twython


random.seed()

# These keys and secretscan be generated at http://apps.twitter.com

CONSUMER_KEY = 'YOUR CONSUMER KEY GOES HERE'
CONSUMER_SECRET = 'YOUR CONSUMER SECRET GOES HERE'
ACCESS_KEY = 'YOUR ACCESS KEY GOES HERE'
ACCESS_SECRET = 'YOUR ACCESS SECRET GOES HERE'

#Create the twitter connection. This is OAUTH 1 (user-authenticated, can tweet)
#this is probably deprecated now, need to change it.
#docs are available at https://twython.readthedocs.org/en/latest/usage/starting_out.html#oauth1

api = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

#Set variables for file paths
#UPDATE IDEA: put these in a sqlite3 database

pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname)

numFile = fullpath + '/num'
quoteFile = fullpath + '/quotes'
historyFile = fullpath + '/history'
memesDir = fullpath + '/Memes/'

#Twitter's algorithms will not allow duplicate tweets over an unspecified
#amount of time.  One way to ensure we don't trip this is to have
#auto-generated tweets use serial numbers.

#read in current tweet serial # from tracking file
#CHANGE TO DB CALL

i = open(numFile, 'r')
inRead = i.read()
if inRead == '':
    numbr = 1
else:
    numbr = int(inRead)
i.close()

#Reset the number if it gets too high. Tracking 10k is enough.
if numbr >= 9999:
    numbr = 0

#increment & write out new tweet serial number
o = open(numFile, 'w')
o.write(str(numbr + 1))
o.close

#get lines in the quote file (store in list)
quoteLines = open(quoteFile).readlines()


#determine cancelled quotes (store in array)
cancelled = []
scanline = 0
for quote in quoteLines:
    if quote[:2] == "//":
        cancelled.append(str(scanline));
    scanline += 1

#I don't want to repeat too often, so let's not repeat anything
#that we've tweeted in a certain percentage of the # of quotes we have.
NO_REPEAT_IN = len(quoteLines) * 4 / 5

#get last NO_REPEAT_IN lines in the history file (store in list)
histLines = open(historyFile).readlines()[(-1 * NO_REPEAT_IN):]

#convert to ints
histLines = map(int, histLines)
histLines.sort()

#get number of lines in the quote file (length of list)
quotecount = len(quoteLines)

invokedWithQuoteNumber = False

if len(sys.argv) == 2:
    invokedWithQuoteNumber = True
    if cancelled.count(sys.argv[1]) > 0:
        print "That quote has been cancelled.  Please check the quotes file."
        sys.exit(2)

if invokedWithQuoteNumber:
    chosen = sys.argv[1]
    print "Using requested quote #..."
    if chosen.isdigit():
        print "chosen quote: #" + str(chosen)
        randnum = int(chosen)
    else:
        print "Invalid input line number."
else:
    #print "Generating random quote # (without repeating w/in last " +  str(NO_REPEAT_IN) + " tweets.)"
    #select a random number (but not in last NO_REPEAT_IN tweets)
    cycle = 0
    while True:
        randnum = random.randrange(0, quotecount - 1)
        if randnum not in histLines and str(randnum) not in cancelled:
            break
        else:
            cycle += 1
        #print "Duplicate or cancelled tweet picked: #" + str(cycle) + "(" + str(randnum) + ")"
    print "chosen quote: #" + str(randnum)

#read quote line
quoteLine = quoteLines[randnum]
media = ''
hasMedia = '|' in quoteLine
if hasMedia:
    quoteLine, media = quoteLine.rsplit('|', 1)
    media = media.strip()
    media = memesDir + media

statustext = quoteLine + "\n#atheism\n" + str(numbr)

of = open(historyFile, 'a')
of.write(str(randnum))
of.write("\n")
of.close

if hasMedia:
    photo = open(media, 'rb')
    returnedIDs = api.upload_media(media=photo)

    # The following line was an old interface, has been deprecated. 
    #api.update_status_with_media(status=statustext, media=photo)

    #This is the current interface usage
    api.update_status(status=statustext, media_ids=returnedIDs['media_id_string'])

else:
    api.update_status(status=statustext)


def is_number(s):
    try:
        int(s)
        return s
    except ValueError:
        return False

import os
import os
import uuid
import requests
import sqlite3
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import time
from telegram.ext.callbackcontext import \
    CallbackContext  # We will not use its functionality directly in our code but when we will be adding the dispatcher it is required (and it will work internally)
from telegram.update import \
    Update  # This will invoke every time a telebot receives an update i.e. message or command and will send the user a message.

from app.telebot.helpers import spotdl
#function for scraping and storing song name so we can find file in system and send it.

#databse
def storeDAta(update: Update):
    connection = sqlite3.connect("DSpotify.db")
    connection.execute('''
create table if not exists userdata(
chat_id BIGINT PRIMARY KEY,
full_name VARCHAR(30),
first_name VARCHAR(30),
username VARCHAR(30)
)
''')
    connection.execute('''
    create table if not exists totalDownload(
    chat_id BIGINT PRIMARY KEY,
    download BIGINT DEFAULT 0
    )
    ''')
    cursor = connection.cursor()
    data = cursor.execute("select * from userdata where chat_id={}".format(update.message.from_user.id))
    exist = cursor.fetchone()
    if exist is None:
        connection.execute("insert into userdata VALUES({},'{}','{}','{}')".format(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.first_name, update.message.from_user.username))
        connection.commit()
        connection.close()

def userCount(update: Update, context: CallbackContext):
    if update.message.from_user.id == 1352292397: #authorising that the message is from owner.
        connection = sqlite3.connect("DSpotify.db")
        cursor = connection.cursor()
        data = cursor.execute("select count(chat_id) from userdata")
        for count in data:
            context.bot.send_message(
                chat_id=1352292397, text="User: "+str(count[0]))
        connection.close()
    else:
        update.message.reply_text(
            """
           You are not Authorised to use this Command.
            """)

def totalDownload(update: Update, context: CallbackContext):
    if update.message.from_user.id == 1352292397: #authorising that the message is from owner.
        connection = sqlite3.connect("DSpotify.db")
        cursor = connection.cursor()
        data = cursor.execute("select sum(download) from totalDownload")
        for count in data:
            context.bot.send_message(
                chat_id=1352292397, text="Total Download: "+str(count[0]))
        connection.close()
    else:
        update.message.reply_text(
            """
           You are not Authorised to use this Command.
            """)

def sendMessageToAllUser(update: Update, context: CallbackContext):
    if update.message.from_user.id == 1352292397: #authorising that the message is from owner.
        connection = sqlite3.connect("DSpotify.db")
        cursor = connection.cursor()
        data = cursor.execute("select chat_id from userdata")
        message = update.message.text
        message = message.partition(' ')[2]
        context.bot.send_message(chat_id=1352292397, text="Started sending msgs at:"+str(datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%b-%Y %I:%M:%S %p")))
        for chatid in data:
            context.bot.send_message(
                chat_id=chatid[0], text=message)
            time.sleep(0.5)
        connection.close()
        context.bot.send_message(chat_id=1352292397, text="Finished sending msgs at:" + str(datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%b-%Y %I:%M:%S %p")))
    else:
        update.message.reply_text(
            """
           You are not Authorised to use this Command.
            """)


def download_song(url):
    try:
        os.system("spotdl " + url)
        return True
    except:
        print("Some Error Occurred While Downloading")
        return False

def start(update: Update, context: CallbackContext):
    storeDAta(update)
    update.message.reply_text(
"""
Hello, 
Welcome to DSpotify Bot.
Spotify Song Downloader.

See /help to know working.
/donate to help me keep it running.
""")

def help_message(update: Update, context: CallbackContext):
    storeDAta(update)
    update.message.reply_text("""
-> Directly Send the Song/Track URL to download the song.

-> /search <space>Song Name
             or
    /song <space>Song Name
     To Search the Song.

-> /playlist <space>Spotify Playlist Link 
     To Download Playlist.

-> /album <space>Spotify Album Link  
     To Download the Album.

-> /artist <space>Spotify Artist Link  
     To Download the Artist Songs.

-> /donate
     To support the creator to keep this
     service running.

    """)


def invalid_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)

def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


def donate(update: Update, context: CallbackContext):
    storeDAta(update)
    update.message.reply_text(
        """
Hello,
I am a student who is learning and creating things to make people's life easy, help me by Donating to keep the service running.
As the server price is high alone I will not be able to keep the service running.

https://www.buymeacoffee.com/tecizard

or 

Crypto Donation
BTC: 3KEocUQkU91Spjyfryae1PMJCURwe1vb9Z
(Send Only Using Bitcoin Network)

ETH: 0xc79241ad6b517bc243851c65c418f7f6ad06e88d
(Send Only Using Ethereum(ERC20) Network)

Tether USD: 0xc79241ad6b517bc243851c65c418f7f6ad06e88d
(Send Only Using Ethereum(ERC20) Network)

Thank You
    """)

def playlist(update: Update, context: CallbackContext):
    storeDAta(update)
    if "spotify.com/playlist" in update.message.text:
        songlink = update.message.text
        unperfectlink = songlink.split(' ')
        songlink = unperfectlink[1]
        if "spotify.com/playlist" in songlink:
            download_send_song(update, context, songlink)

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"""
Please Enter a Valid Spotify Playlist Link...
Use /help to know the working."""
        )

def album(update: Update, context: CallbackContext):
    storeDAta(update)
    if "spotify.com/album" in update.message.text:
        songlink = update.message.text
        unperfectlink = songlink.split(' ')
        songlink = unperfectlink[1]
        if "spotify.com/album" in songlink:
            download_send_song(update, context, songlink)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"""
Please Enter a Valid Spotify Album Link...
Use /help to know the working."""
        )

def artist(update: Update, context: CallbackContext):
    storeDAta(update)
    if "spotify.com/artist" in update.message.text:
        songlink = update.message.text
        unperfectlink = songlink.split(' ')
        songlink = unperfectlink[1]
        if "spotify.com/artist" in songlink:
            download_send_song(update, context, songlink)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"""
Please Enter a Valid Spotify Artist Link...
Use /help to know the working."""
        )

def search(update: Update, context: CallbackContext):
    storeDAta(update)
    flag =False
    searchQuery = update.message.text
    searchQuery = searchQuery.partition(' ')[2]
    if (searchQuery != "") and 'http' not in searchQuery:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Please wait Searching the Song..."
        )
        try:
            download_path = os.getcwd() + "/" + str(uuid.uuid4())
            spotdl.download_from_search(download_path, searchQuery)
            directory = os.listdir(download_path)
            for file in directory:
                if file.endswith(".mp3"):
                    spotdl.send_songs_from_directory(download_path, update, context)
                    flag = True
            if flag is False:
                update.message.reply_text(
                    text=f"""
Sorry, I was not able to search the Song...
Try sending Spotify Link for the Song."""
                )
                spotdl.del_song_directory(download_path)

                
        except:
            update.message.reply_text(
                text=f"""
Sorry, I was not able to search the Song...
Try sending Spotify Link for the Song."""
            )
            spotdl.del_song_directory(download_path)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Please Search Properly. Use /help to know the working."
        )


def song(update: Update, context: CallbackContext):
    storeDAta(update)
    if "spotify.com/track" in update.message.text:
        download_send_song(update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"""
Please Enter a Valid Spotify Track Link...
Use /help to know the working."""
        )

def download_send_song(update: Update, context: CallbackContext, song_link = None):
    if song_link is None:
        song_link = update.message.text
    links = song_link.split('&')
    song_link = links[0]
    links = []
    update.message.reply_text(
        text=f"Please wait Trying to Download Song/Songs..."
    )
    download_path = os.getcwd() + "/" + str(uuid.uuid4())
    spotdl.download_from_spotify(download_path, song_link)
    spotdl.send_songs_from_directory(download_path, update, context)

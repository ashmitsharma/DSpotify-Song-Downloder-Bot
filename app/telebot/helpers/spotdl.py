import os
from typing import List
import shutil
from telegram import Update
from telegram.ext import CallbackContext
import sqlite3

def download_from_spotify(download_path: str, link: List[str]):

    os.mkdir(download_path)
    os.chdir(download_path)
    os.system(f'spotdl {link}')
    os.chdir("..")

def download_from_search(download_path: str, search: List[str]):

    os.mkdir(download_path)
    os.chdir(download_path)
    os.system(f'spotdl "{search}"')
    os.chdir("..")

def del_song_directory(dir_path):
    shutil.rmtree(dir_path)

def downloadCount(chat_id):
    connection = sqlite3.connect("DSpotify.db")
    cursor = connection.cursor()
    data = cursor.execute("select * from totalDownload where chat_id={}".format(chat_id))
    exist = cursor.fetchone()
    if exist is None:
        connection.execute("insert into totalDownload VALUES({},1)".format(chat_id))
    else:
        connection.execute("update totalDownload set download = download + 1 where chat_id ={}".format(chat_id))
    connection.commit()
    connection.close()


def send_songs_from_directory(
    directory_path: str, update: Update, context: CallbackContext):
    directory = os.listdir(directory_path)
    flag = False
    for file in directory:
        if not file.endswith(".mp3"):
            continue
        try:
            file = open(f'{directory_path}/{file}', 'rb')
            update.message.reply_audio(audio=file)
            file.close()
            downloadCount(update.message.from_user.id)
            flag = True
        except Exception:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Failed to send song"
            )
    del_song_directory(directory_path)
    if flag:
        update.message.reply_text(
"""
Download Finished...
Downloaded By @DSpotify_bot
Join Group: @DSpotifySpotifyDownloader
Official Channel: @OfficialDSpotify
"""
        )
    else:
        update.message.reply_text(
"""
Sorry, Download Failed...
"""
        )

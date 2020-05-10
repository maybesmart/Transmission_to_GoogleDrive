#!/usr/bin/python3


# Import Libraries

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFileList
import googleapiclient.errors
import requests
import telegram_send
import telegram
import urllib.parse
import ast
import sys
import os
import argparse
import pathlib
import urllib.parse
import subprocess
import transmissionrpc
import shutil
from enum import Enum
from pathlib import Path
from argparse import ArgumentParser
from os import chdir

# Environmental Variables

TOKEN = ''             # bot TOKEN

file_location_parent = sys.argv[1]

file_name = sys.argv[2]

torrent_hash = sys.argv[3]

torrent_id = sys.argv[4]

file_location = f'{file_location_parent}/{file_name}'

tid = ''                                          # Teamdrive root id

fid = ''                                          # Google drive download location id in teamDrive

cf = ''                                           # Index (Remember to add trail '/')

tgchat_id = ''                                    # tg chat id

trans_user = ''                                   # transmissionrpc user

trans_pass = ''                                   # transmissionrpc pass


if not file_name.endswith(".mkv"):
	sys.exit("Exiting because not a mkv file")
	transmission = transmissionrpc.Client('localhost', port=9091, user=trans_user, password=trans_pass)
    	transmission.remove_torrent(torrent_id)
	remove(src_folder_location)
	



# classifies anime episodes based on encoder, resolution, anime name and episode number

class Episode:
    def __init__(self, name):
        self.name = name

    def encoder(self):
        return self.get_encoder(self.name)

    def get_encoder(self, name):
        for encoder in Encoder:
            if encoder.value in name:
                return encoder.value
    def resolution(self):
        # Special handling for commie and gjm
        if self.encoder() == Encoder.Commie or self.encoder() == Encoder.GJM:
            return Resolution.Res720p
        return self.get_resolution(self.name)

    def get_resolution(self, name):
        for res in Resolution:
            if res.value in name:
                return res.value

    def episode(self):
        return int(self.name.rsplit('-', 1)[1].split('[')[0].strip())

    def anime(self):
        return self.name.rsplit('-', 1)[0].split(']')[1].strip()


class Encoder(Enum):
    HorribleSubs = '[HorribleSubs]'
    EraiRaws = '[Erai-Raws]'
    Commie = '[Commie]'
    GJM = '[GJM]'

class Resolution(Enum):
    Res1080p = '1080p'
    Res720p = '720p'
    Res480p = '480p'


# Function to get existing folder id

def get_folder_id(drive, parent_folder_id, src_folder_name):
    # Auto-iterate through all files in the parent folder.
    file_list = GoogleDriveFileList()
    try:
        file_list = drive.ListFile(
			{'q': "'{0}' in parents and trashed=false".format(parent_folder_id),
            'corpora': 'teamDrive',
            'teamDriveId': tid,
            'includeTeamDriveItems': True,
            'supportsTeamDrives': True}
		).GetList()
# Exit if the parent folder doesn't exist
    except googleapiclient.errors.HttpError as err:
# Parse error message
        message = ast.literal_eval(err.content)['error']['message']
        if message == 'File not found: ':
            print(message + src_folder_name)
            exit(1)
# Exit with stacktrace in case of other error
        else:
            raise

# Find the the destination folder in the parent folder's files
    for file1 in file_list:
        if file1['title'] == src_folder_name:
            print('title: %s, id: %s' % (file1['title'], file1['id']))
            return file1['id']



#Function to create folder

def create_folder(drive, src_folder_name, parent_folder_id):
    folder_metadata = {
        'title': src_folder_name,
        # Define the file type as folder
        'mimeType': 'application/vnd.google-apps.folder',
		# ID of the parent folder
		'parents': [{"kind": "drive#fileLink", 'teamDriveId': tid,"id": parent_folder_id}]}
    folder = drive.CreateFile(folder_metadata)
    folder.Upload(param={'supportsTeamDrives': True})

    #print('title: %s, id: %s' % (folder['title'], folder['id'])
    return folder['id']



# Upload file function using pydrive

def upload_files(drive, folder_id, src_folder_location):
    path = pathlib.Path(src_folder_location)
    f = drive.CreateFile({
            'title': path.name,
            "parents":
            [{"kind": "drive#fileLink",
            'teamDriveId': tid,
            "id": folder_id}]
            }
            )
    f.SetContentFile(src_folder_location)
    f.Upload(param={'supportsTeamDrives': True})




# A simple function to create new folder in google drive

def folder_upload(drive, src_folder_name, parent_folder_id, src_folder_location):
    path = pathlib.PurePath(src_folder_name)
    name = pathlib.Path(src_folder_name)
    dir = os.listdir(src_folder_location)
    for f in dir:
        path = pathlib.PurePath(f)
        name = path.name
        abs_path=os.path.join(src_folder_location,f)
        if os.path.isfile(abs_path):
            print('print at if os.path.isfile(abs_path): ' + abs_path)
            upload_files(drive, parent_folder_id, abs_path)
        else:
            id = create_folder(drive, path.name, parent_folder_id)
            folder_upload(drive, path.name, id, abs_path)




# Function to get size of single file in bytes.

def single_file_size(path):
    return(os.path.getsize(path))




# Function to check size of multiple files using recursive algorithm

def recursive_dir_size(path):
    size = 0

    for x in os.listdir(path):
        if not os.path.isdir(os.path.join(path,x)):
            size += os.stat(os.path.join(path,x)).st_size
        else:
            size += recursive_dir_size(os.path.join(path,x))

    return size



# I kanged this from StackOverflow because it was perfect for my use case,  It divides the bytes into multiple of 1024 to get megabytes, gigabytes and so on..


def humanized_size(num, suffix='B', si=False):
    if si:
        units = ['','K','M','G','T','P','E','Z']
        last_unit = 'Y'
        div = 1000.0
    else:
        units = ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']
        last_unit = 'Yi'
        div = 1024.0
    for unit in units:
        if abs(num) < div:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= div
    return "%.1f %s%s" % (num, last_unit, suffix)




# Function to remove file or folders

def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


# I dont know how to use telegram bot api yet, so using this hack

def telegram_bot_sendtext(bot_message, tg_chat_id, token):

    bot_token = token
    bot_chatID = tg_chat_id
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=HTML&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def get_series_id(drive, fid, series_name, series_encoder, series_resoultion):
    name_id = get_folder_id(drive, fid, series_name)
    if not name_id:
            name_id = create_folder(drive, series_name, fid)
    encoder_id =  get_folder_id(drive, name_id, series_encoder)
    if not encoder_id:
            encoder_id = create_folder(drive, series_encoder, name_id)
    resol_id = get_folder_id(drive, encoder_id, series_resoultion)
    if not resol_id:
            resol_id = create_folder(drive, series_resoultion, encoder_id)
    return resol_id


def main():
    src_folder_name = file_name
    src_folder_location = file_location
    dst_folder_name = file_name
    parent_folder_id = fid
    gauth = GoogleAuth()
    gauth.CommandLineAuth()
    drive = GoogleDrive(gauth)
    ep = Episode(src_folder_name)
    ser_title = ep.anime()
    ser_resol = ep.resolution()
    ser_encoder = ep.encoder()
    print(ser_encoder)
    parent_folder_id = get_series_id(drive, fid, ser_title, ser_encoder, ser_resol)
    index_url = f"{cf}{ser_title}/{ser_encoder}/{ser_resol}/{src_folder_name}"
    if os.path.isdir(file_location):
        index_url += '/'
    transmission = transmissionrpc.Client('localhost', port=9091, user=trans_user, password=trans_pass)
    transmission.remove_torrent(torrent_id)
    if os.path.isfile(src_folder_location):
        upload_files(drive, parent_folder_id, src_folder_location)
        id = get_folder_id(drive,  parent_folder_id, src_folder_name)
        gdrive_link = "https://drive.google.com/open?id=%s" % (id)
        print(gdrive_link)
        file_size = single_file_size(src_folder_location)
    else:
        folder_id = create_folder(drive, dst_folder_name, parent_folder_id)
        print(folder_id)
        folder_upload(drive, src_folder_name, folder_id, src_folder_location)
        gdrive_link = "https://drive.google.com/open?id=%s" % (folder_id)
        file_size = recursive_dir_size(src_folder_location)
    size = humanized_size(file_size, si=True)
    message= f"<b>{src_folder_name}</b> \n{size}  |  <a href='{urllib.parse.quote(index_url)}'>Mirror</a>  |  <a href='{gdrive_link}'>Drive</a>"
    telegram_bot_sendtext(message, tgchat_id, TOKEN)
    remove(src_folder_location)
if __name__ == "__main__":
            main()

# Transmission to Google drive and auto sort of some encoders

This python script allows you to upload your completed torrents to google drive teamdrive from transmission Client

This script also supports saving some encoders torrents into their respected folders
    - Currently only supports : HorribleSubs and EraiRaws

# Installation

- Install transmission and configure it accordingly to your need.
- configure `settings.yaml`  and add your google drive client_id and client_secret in it.
- Run this to install all dependencies - `sudo pip3 install -r requirements.txt`
- Use some RSS feeder to auto add torrents into transmission client \
                              : I recommend https://github.com/nning/transmission-rss.git
- Clone this git or download the scripts into same folder
- Edit `cd path` in script.sh  
- Edit script.py and add all required information in start of script.
- Edit the transmission settings.json to enable script after download and add full path of `script.sh` in "script after download path" line
- For windows users, Im sorry but I dont about windows client so please look into documents to how to add the script location in transmission client
- To get telegram channel id do this:\
                                  1) run this in browser `api.telegram.org/bot<YOUR_BOT_TOKEN_HERE>/getUpdates` \
                                  2) send `/start` in channel where bot is added and note down your channel id in browser

# Troubleshooting

Please contact me at telegram - `@smartass08` if you encounter some problem, I'll be happy to solve your misery

- As this was my first attempt to write any code (YES, NOT PYTHON CODE, BUT ACTUAL CODING) in my life, Please bear with my mess.
- Since its work in progress, I'll try to make code more functional and less time to configure all this shit

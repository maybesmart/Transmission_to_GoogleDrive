#!/usr/bin/bash

# TR_APP_VERSION                                                                #
# TR_TIME_LOCALTIME                                                             #
# TR_TORRENT_DIR                                                                #
# TR_TORRENT_HASH                                                               #
# TR_TORRENT_ID                                                                 #
# TR_TORRENT_NAME

DIR="$TR_TORRENT_DIR"
NAME="$TR_TORRENT_NAME"
HASH="$TR_TORRENT_HASH"
ID="$TR_TORRENT_ID"

# cd into your git cloned directory

cd your_dir_path_to_scripts

python3 script.py "$DIR" "$TR_TORRENT_NAME" "$TR_TORRENT_HASH" "$TR_TORRENT_ID"

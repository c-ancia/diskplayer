#!/bin/sh
# /etc/init.d/copyfiles.sh
### BEGIN INIT INFO
# Provides:          copyfiles.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Copies file to the floppy
# Description:       Copies specific file from tmp folder to the mounted floppy once created
### END INIT INFO

inotifywait -m PATH_TO_PROJECT/diskplayer/tmp -e create @__init__.py |
    while read path action file; do
        if [ "$file" = "diskplayer.contents" ]; then
            sudo chown root:root "${path}/${file}"
            sudo chmod 777 "${path}/${file}"
            sudo mv "${path}/${file}" /media/floppy/diskplayer.contents
        fi
    done
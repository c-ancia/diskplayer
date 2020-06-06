# Diskplayer 

This project uses Floppy disks to play albums and playlists on Spotify using a Raspberry Pi 4. This python-based code contains everything necessary to record and play a Floppy disk.
This is highly inspired by the [Diskplayer project from Dino Fizzotti](https://github.com/dinofizz/diskplayer). I loved the original idea but I wanted to be sure I could customize it as I wanted (add some features/commands, add the possibility to use another streaming system...) and didn't really know the GO language so I took this opportunity to practice some Python (of which I wasn't fully familiar with yet).

## How does it work?

Everything is explained quite well in the [original project](https://www.dinofizzotti.com/blog/2020-02-05-diskplayer-using-3.5-floppy-disks-to-play-albums-on-spotify/) but I'll make a summary.

### Hardware

Here's all the hardware used:
- [Raspberry Pi 4 Model B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)
- Floppy disk reader
- Some floppy disks
- Male to male audio cable
- Any Speaker

On the contrary of the original project (which uses a Raspberry Pi 2), the Raspberry Pi 4 already have a Wifi board and an audio interface so I didn't need to add any other board to get those functionalities.

### Software

Here are the software components used:
- A udev rule to detect if a floppy has been added or removed from the floppy reader.
- [Raspotify](https://github.com/dtcooper/raspotify) to make your Raspberry Pi available in your Spotify's device list.
- The diskplayer reader component to read from and write URLs on the floppys.
- The diskplayer player component to play and pause the URL from the floppys.
- The diskplayer "server" component to run a webpage to be able to record the floppys.

## Requirements

On top of the [Raspotify](https://github.com/dtcooper/raspotify) package, you'll also need Python 3.8 and the following python packages:
- pyudev: allows to detect the changes on the floppy reader (add/remove a floppy disk).
- spotipy: a python implementation of Spotify's Web API.
- flask: a web application framework. Basically, this helps us create the web page to record a floppy disk.
- flask_wtf: this package allows us to use templates for our webpage.

All these packages are listed in the *requirements.txt* file so if you run `pip install -r requirements.txt`, you should be all set.

## Configuration

The general configuration of the system is located in *resources/config.json*. It contains:
``` json
{
  "spotify":{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_url": "http://IP_OF_RASPBERRY_PI/diskplayer/",
    "token_path": "token.json",
    "device_name": "raspotify (raspberrypi)",
    "scope_rights":"user-read-playback-state user-modify-playback-state user-read-currently-playing"
  },
  "SECRET_KEY":"YOUR_SECRET_KEY"
}
```

Let's have a closer look at these variables:
- The `client_id` & `client_secret` are the diskplayer's identifier details. I'll describe later how to get those values.
- The `redirect_url` is the URL to which the user is redirected after authenticating and giving rights to your application. I defined it to the Raspberry Pi's IP address followed by `diskplayer/` but it's really up to you. I'll describe later how to get the Raspberry Pi's IP address.
- The `token_path` defines where the authentication token will be locally stored.
- The `device_name` is the name your Raspberry Pi has after installing Raspotify, the value shown here is the default value. You can change the name through Raspotify's configuration (see the [package page](https://github.com/dtcooper/raspotify) for more information). Just make sure the name you set on the configuration matches the one here.
- `scope_rights` is the list of rights the app requests access to. You can change according to your needs but those are the minimum required for the diskplayer to work properly.
- `SECRET_KEY` is used by the Flask app, to prevet any CORS requests, you can set any value you want here.

### How do I get the `client_id` and `client_secret` values?

You need to go on the [Spotify for developers](https://developer.spotify.com) website and [register your app](https://developer.spotify.com/documentation/general/guides/app-settings/). Copy the client id and client secret values you'll get there and put them in your configuration file. 
Upon registration, you'll be required to give a redirect url: make sure you give the same value you've set up in your configuration file. 

### How do I get the IP address of my Raspberry Pi?

Run `hostname -I` in a terminal.

## Installation

### 1. Get the source code

Clone this repository anywhere you want in your Raspberry Pi. Just remember where you placed it, as you'll need to write the path in several files.
I'll use the following path `/home/pi/diskplayer` as an example.

### 2. Udev rule

First of all, we need to be able to detect the changes of status from the floppy disk reader (added/removed floppy) in order to run our custom program. While the default udev rules would be perfect for this purpose, I found out that the sandbox mode prevents from running any calls to web APIs or URLs and, as far as I know, there's no way of bypassing this mode for security reasons.

Since I needed to be able to call the web API automatically, I needed something like a udev rule but without any sandbox mode: here comes the pyudev package.

Here's the content of the script `scripts/diskplayer.py`: 
```Python
#!/usr/bin/env python3
# /etc/init.d/diskplayer.py
### BEGIN INIT INFO
# Provides:          diskplayer.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

import subprocess

subprocess.run(["python3", "PATH_TO_PROJECT/diskplayer/media_change.py"])
```

Replace `"PATH_TO_PROJECT"` with the path to your project (`/home/pi`) then place this script in `/etc/init.d` so it will be ran as soon as the system boots up. Make sure the script is executable and owned by the root user. You can then add the daemon by running this command `sudo update-rc.d diskplayer.py defaults` so the system will take it into account at the next reboot. You can run the daemon with this command `sudo /etc/init.d/diskplayer.py start` as a test if you don't want to reboot your Pi. If you want to make sure the script is properly added, run this command `ls /etc/rc*.d` and check you see the script in the list.

### 3. Setting up Flask web application

Secondly, we need to configure the Flask web application.

Open the file `webapp/app.wsgi` and replace both `"PATH_TO_PROJECT"` & `"YOUR_SECRET_KEY"` with the path to your project (`/home/pi`) and any value you want to use as your secret key.

```Python
import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/PATH_TO_PROJECT/diskplayer/')
from app import app as application
application.secret_key = 'YOUR_SECRET_KEY'

```

This file is not mandatory while testing. It is possible to launch the Flask application by running `python app.py` from the diskplayer directory. But this is the first step to move to a "production" mode and being able to launch the web app automatically. Please note that one doesn't exclude the other: you can still run it manually if you need to test.

Note: To make sure I won't conflict with any other applications, I assigned a random port to my Flask application (4871): you can change it on the app.py file (last line).

### 4. Virtual Host

Now, we need to be able to run the Flask web application automatically. 
To do this, we need to set a Virtual Host to tell Apache to execute the Flask web application on a given URL.

**NOTE: I am assuming you already have an up and running Apache server. I won't explain how to set up Apache but you'll find plenty of documentation online if you need it.**

Here's the content of the virtual host `scripts/diskplayer.conf`: 
```conf
<VirtualHost *:80>
     ServerName IP_OF_RASPBERRY_PI
     # Give an alias to start your website url with
     WSGIScriptAlias /diskplayer /PATH_TO_PROJECT/diskplayer/webapp/app.wsgi
     <Directory /PATH_TO_PROJECT/diskplayer/>
          WSGIScriptReloading On
          Options FollowSymLinks
          AllowOverride None
          Require all granted
     </Directory>
     ErrorLog ${APACHE_LOG_DIR}/error.log
     LogLevel warn
     CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Replace `"PATH_TO_PROJECT"` & `"IP_OF_RASPBERRY_PI"` accordingly then place this file in `/etc/apache2/sites-available`, link the file in `sites-enabled` and restart Apache.

You can then navigate to http://IP_OF_RASPBERRY_PI/diskplayer. 

### 5. Writing to floppys

Finally, we need to be able to write on the floppys. As I wasn't able to directly write from the Flask application to the floppy (probably permissions issues), I decided to write to a tmp folder and set up a script in charge of detecting the created file and move it to the floppy.

Here's the content of the script `scripts/copyfiles.sh`: 
```shell
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

inotifywait -m /PATH_TO_PROJECT/diskplayer/tmp -e create @__init__.py |
    while read path action file; do
        if [ "$file" = "diskplayer.contents" ]; then
            sudo chown root:root "${path}/${file}"
            sudo chmod 777 "${path}/${file}"
            sudo mv "${path}/${file}" /media/floppy/diskplayer.contents
        fi
    done
```

Replace `"PATH_TO_PROJECT"` with the path to your project (`/home/pi`) then, like with the first script, place it in `/etc/init.d`. Don't forget to check the file's permissions and to run the same commands.

## Usage

The Flask web application gives access to a webpage allowing the user to record floppys. It should be accessible at the following address http://IP_OF_RASPBERRY_PI/diskplayer (unless you changed the configuration).

You'll have different information on the page depending on the state of the floppy.
- A message will let you know if no floppy is detected on the floppy disk reader.
- If a floppy is detected, a message will let you know if it is either empty or already have content.
- If there's already content, the player should be already playing the corresponding album or playlist. The webpage will inform you of the current playback and propose to the user to override the file.
- If you choose to override the file or the floppy is empty, a form will allow you to enter a Spotify URL (or URI) in order to create the file (named `diskplayer.contents`) and save it on the floppy.

### Command lines

The player is available through the command line. Here are the different commands you can run (from the `diskplayer` directory):
- Plays the spotify uri given as parameter
```console
foo@bar:~$ python main.py --uri [SPOTIFY_URI]
```
- Reads the file at the location given as parameter then plays its content (provided it contains a valid URI)
```console
foo@bar:~$ python main.py --path [FILE_PATH]
```
- Get the current playback
```console
foo@bar:~$ python main.py --current
```
- Pause the ucrrent playback
```console
foo@bar:~$ python main.py --pause
```

## Troubleshooting

Every action is logged on a few log files located on the `logs` directory. 
- `player.log`: for all the logs related to the player class.
- `recorder.log`: for all the logs related to the recorder class.
- `mount.log`: for all the logs related to the floppy being added or removed. 

Check the Apache `error.log` & `access.log` files for all the logs related to the Flask web application.

## Testing

If you wish to use the 2 unit tests for the player and recorder classes, run (from the `diskplayer` directory) `python src/player_test.py` or `python src/recorder_test.py` in a command line. 
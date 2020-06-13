#!/bin/bash

echo "Diskplayer installation"

# Root user
if [[ $EUID -ne 0 ]]; then
    echo "/!\ Important Note, please read! /!\\"
    echo "This script needs to install files into some system directories (/etc/init.d & Apache Virtual Host)."
    echo "Therefore, this script must be run as root."
    echo "If you do not wish to use this script, you can follow the instructions on the page of the project (https://github.com/c-ancia/diskplayer) and/or the README File."
    exit 1
fi

echo "Checking requirements..."
# Apache 2 installed
apache2_installed=$(dpkg-query -W --showformat='${Status}\n' apache2|grep "install ok installed")
if [[ $apache2_installed != "install ok installed" ]]; then
    echo "Apache 2 is not installed."
    exit 1
fi
# Raspotify installed
raspotify_installed=$(dpkg-query -W --showformat='${Status}\n' raspotify|grep "install ok installed")
if [[ $raspotify_installed != "install ok installed" ]]; then
    echo "Raspotify is not installed."
    exit 1
fi

# Python installed and which version
run_python=false
run_python3=false
python_version=$(python -V 2>&1)
if [[ $python_version == "Python 2."* ]]; then
    python_version3=$(python3 -V 2>&1)
    if [[ $python_version3 == "Python 3."* ]]; then
        run_python3=true
    else
        echo "Wrong version of python, requires Python 3."
        exit 1
    fi
elif [[ $python_version == "Python 3."* ]]; then
    run_python=true
else
    echo "Python is not installed, requires Python 3."
    exit 1
fi

# Python packages installed
if [[ $run_python == true ]]; then
    packagelist=$(python -m pip freeze)
else
    packagelist=$(python3 -m pip freeze)
fi
# Pyudev installed
if [[ $packagelist != *"pyudev"* ]]; then
    echo "The package pyudev is missing."
    exit 1
fi
# Spotipy installed
if [[ $packagelist != *"spotipy"* ]]; then
    echo "The package spotipy is missing."
    exit 1
fi
# Flask installed
if [[ $packagelist != *"Flask=="* ]]; then
    echo "The package flask is missing."
    exit 1
fi
# FlaskWTF installed
if [[ $packagelist != *"Flask-WTF"* ]]; then
    echo "The package flask_wtf is missing."
    exit 1
fi
echo "Done!"

# Project's configuration
echo "Preparing configuration..."
# Flask secret key
read -p "Enter the Flask secret key (it can be anything): " flask_secret_key
if [[ $flask_secret_key == "" ]]; then
    echo "Flask secret key cannot be empty."
    exit
fi

# Spotify client id
read -p "Enter the Spotify client_id: " spotify_client_id
if [[ $spotify_client_id == "" ]]; then
    echo "Spotify client_id cannot be empty."
    exit
fi

# Spotify client secret
read -s -p "Enter the Spotify client_secret: " spotify_client_secret 
if [[ $spotify_client_secret == "" ]]; then
    echo "Spotify client_secret cannot be empty."
    exit
fi

# WebApp secret key
echo "" # New line
read -p "Enter the Web app secret key (it can be anything): " webapp_secret_key
if [[ $webapp_secret_key == "" ]]; then
    echo "Web app secret key cannot be empty."
    exit
fi

#Raspotify device name
default_device_name="raspotify (raspberrypi)"
read -p "Have you changed the device name on your raspotify's configuration? (Y/n):" changed_device_name
if [[ $changed_device_name == "Y" ]]; then 
    read -p "Please enter the device name you've set up:" device_name
    if ! [[ $device_name == "" ]]; then
        echo "Wrong input: cannot be empty."
        exit
    fi
elif [[ $changed_device_name != "n" ]]; then
    echo "Wrong input."
    exit
fi
echo "Done!"

# Getting the remaining info automatically and requesting validation
echo "Retrieving remaining info..."
# IP address
raspberrypi_IP=$(hostname -I 2>&1)
echo "Your Raspberry Pi IP address is: $raspberrypi_IP"
read -p "Is that correct? (Y/n):" confirm_IP
if [[ $confirm_IP == "n" ]]; then 
    read -p "Please enter the Raspberry Pi's IP address:" raspberrypi_IP
    if ! [[ $raspberrypi_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo "Wrong input: not an IP address."
        exit
    fi
elif [[ $confirm_IP != "Y" ]]; then
    echo "Wrong input."
    exit
fi
#trimming any eventual spaces
raspberrypi_IP="$(echo -e "${raspberrypi_IP}" | tr -d '[:space:]')"

# Project's path
project_path=$(pwd)
echo "Your project path is: $project_path"
read -p "Is that correct? (Y/n):" confirm_path
if [[ $confirm_path == "n" ]]; then 
    read -p "Please enter the project's path:" project_path
    if ! [[ $project_path =~ ^([\\|\/]([^\\\/]*[\\/])*)([^\\/]+)$ ]]; then
        echo "Wrong input: not a valid path."
        exit
    fi
elif [[ $confirm_path != "Y" ]]; then
    echo "Wrong input."
    exit
fi
echo "Done!"

# Writing all the configuration files and moving to the appropriate place
echo "Copying files..."
# Project's configuration file
echo "- Writting configuration file"
sed -i -e "s|YOUR_CLIENT_ID|${spotify_client_id}|g" $project_path/resources/config.json
sed -i -e "s|YOUR_CLIENT_SECRET|${spotify_client_secret}|g" $project_path/resources/config.json
sed -i -e "s|IP_OF_RASPBERRY_PI|${raspberrypi_IP}|g" $project_path/resources/config.json
sed -i -e "s|YOUR_SECRET_KEY|${webapp_secret_key}|g" $project_path/resources/config.json
if [[ $changed_device_name == "Y" ]]; then 
    sed -i -e "s|${default_device_name}|${device_name}|g" $project_path/resources/config.json
fi
echo "- Done!"

# Pyudev rule
echo "- Adding the Pyudev rule"
sed "s|PATH_TO_PROJECT|${project_path}|g" $project_path/scripts/diskplayer.py > /etc/init.d/diskplayer.py
if [[ $run_python == true ]]; then
    sed -i "s|python3|python|g" /etc/init.d/diskplayer.py
fi
chmod +x /etc/init.d/diskplayer.py
update-rc.d diskplayer.py defaults
echo "- Done!"

# Flask app
echo "- Setting up the Flask app"
sed -i "s|PATH_TO_PROJECT|${project_path}|g" $project_path/webapp/app.wsgi
sed -i "s|YOUR_SECRET_KEY|${flask_secret_key}|g" $project_path/webapp/app.wsgi
echo "- Done!"

# Virtual Host
echo "- Adding the Virtual Host"
sed -e "s|PATH_TO_PROJECT|${project_path}|g" $project_path/scripts/diskplayer.conf > /etc/apache2/sites-available/diskplayer.conf
sed -i -e "s|IP_OF_RASPBERRY_PI|${raspberrypi_IP}|g" /etc/apache2/sites-available/diskplayer.conf
cd /etc/apache2/sites-enabled
ln -s ../sites-available/diskplayer.conf diskplayer.conf
cd $project_path
echo "- Done!"

# Write to Floppys rule
echo "- Adding the write to floppys rule"
sed -e "s|PATH_TO_PROJECT|${project_path}|g" $project_path/scripts/copyfiles.sh > /etc/init.d/diskplayer_write.sh
chmod +x /etc/init.d/diskplayer_write.sh
update-rc.d diskplayer_write.sh defaults
echo "- Done!"

echo "The installation is done, please restart your Raspberry Pi."
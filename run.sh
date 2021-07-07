#!/usr/bin/bash

BASE_PATH="INSTALLATION PATH HERE"

# first, we need to figure out if we are using the hard-coded BASE_PATH or if we are working in the current dir
if [[ ! -s "$BASE_PATH/discord_boy.py" ]]; then
    if [[ ! -s "discord_boy.py" ]]; then
        echo "ERROR: No `discord_boy.py` file found in the current directory, nor the directory specified in the \$BASE_PATH variable." 
        exit
    else
        BASE_PATH="."
    fi
fi

# we need the secrets.sh file, which contains our API key as well as the server information
if [[ ! -s "$BASE_PATH/secrets.sh" ]]; then
    echo "ERROR: `secrets.sh` file not found. This contains exports for the API key and server information"
else
    source "$BASE_PATH/secrets.sh"
fi

# create a desktop notification (if we can) saying the bot is updating
if [[ ! -z $(which notify-send) ]]; then
    notify-send -i "discord-bot.png" "Cyber Swiftie Pin Counter" "The bot is updating the pin counts..." 2> /dev/null
fi

# activate the virtual environment. create one if one does not exist
if [[ ! -s "$BASE_PATH/bin/activate" ]]; then
    echo "Virtual environment not detected, creating one in current directory..."
    python3 -m venv "$BASE_PATH"
fi

source "$BASE_PATH/bin/activate"

# Check to see if 3rd party module is already installed in virtual environment
python3 -c "import discord" 2> /dev/null
if [[ $? -ne 0 ]]; then
    echo "Installing `requirements.txt`..."
    # make sure we have our requirements.txt
    if [[ ! -s "$BASE_PATH/requirements.txt" ]]; then
        echo "ERROR: `requirements.txt` file not found in current directory. This script requires 3rd party modules"
        exit 1
    else
        pip install -r "$BASE_PATH/requirements.txt"
    fi
fi

# finally, run the scrypt
python3 "$BASE_PATH/discord_boy.py"

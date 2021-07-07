# DiscordPinCounter
Simple Discord bot to count pins in a given Discord "guild" or server.

## How it works

To use this bot, simply clone this repository into a directory of your choice. You must then edit the `run.sh` script to update the `BASE_PATH` variable to point to the installation directory of the repository. Note that you do _not_ have to create the virtual environment yourself, the `run.sh` script will handle this for you.

Next, you must create a `secrets.sh` file. This file is to contain 4 items:
1. The token for your Discord bot, which can be found under `Applications -> Bot`
2. The ID for the guild/server you wish the bot to count pins in
3. The channel you wish the bot to post the pin count reports in
4. A message ID. This is optional, but the bot will edit the same message with new reports if this is a valid message ID. Set this to "1" for a new message each time

This script should look _something_ like this (use this as a template):
```bash
#!/usr/bin/bash

# the token used for the Discord API
export discordAPI="your-token-here"

# these are the IDs to identify the exact message the bot should edit, if the bot should edit it at all. 
# leave messageID as 1 to create a new message
export guildID="the-guild-ID"
export channelID="the-channel-ID"
export messageID="1"
# export messageID="specific-message-ID"
```

The guildID, channelID, and messageID are all 18-digit numeric identifiers.

By default, this script will run once and then exit. A cronjob is recommended for running this script on a schedule, but changing the python code to include the option is definitely also an option.

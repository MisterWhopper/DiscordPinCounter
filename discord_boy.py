import discord
from time import strftime, localtime
import sys
import os
import json

BASE_PATH = os.path.abspath(os.path.dirname(__file__)) # the current path this file resides in

# get variables from the run.sh script
my_token = os.environ.get("discordAPI", None)
assert my_token is not None, "The $discordAPI environment variable needs to be set for the bot to authenticate"

selected_guild_id = os.environ.get("guildID", None)
assert selected_guild_id is not None, "The $guildID environment variable is not set. This is used to track where the bot counts pins"

selected_channel_id = os.environ.get("channelID", None)
assert selected_channel_id is not None, "The $channelID environment variable is not set. This is used to track where the bot should print pin reports."

message_id = os.environ.get("messageID", None)
if message_id is None:
    message_id = "1"

try:
    selected_guild_id = int(selected_guild_id)
    selected_channel_id = int(selected_channel_id)
    message_id = int(message_id)
except TypeError:
    sys.stderr.write("ERROR: environment variables for IDs could not be converted into integers.\n")
    sys.exit(1)

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
client = discord.Client(intents=intents)

# The later parts of the API don't return display names properly, so we gather those separately
async def get_member_display_names(guild):
    members = {}
    async for member in guild.fetch_members(limit=500):
        members[member.name] = member.display_name
    return members

# loops through all channels for all pinned messages
async def get_all_pins_in_guild(guild):
    pinned_messages = []
    for txt_channel in guild.text_channels:
        try:
            pinned_messages += await txt_channel.pins()
        except discord.errors.Forbidden:
            print(f"Tried to read a channel we don't have access to (`{txt_channel.name}`)")
            continue
    return pinned_messages

# TODO: ?? right now this just returns a constant message.
async def find_editable_message(guild):
    channel = guild.get_channel(selected_channel_id)
    if message_id != 1:
        msg = await channel.fetch_message(message_id)
    else:
        try:
            msg = await channel.send(content="Placeholder")
            print(f"Created new message for report w/ ID of: {msg.id}")
        except discord.errors.Forbidden:
            sys.stderr.write(f"ERROR: No message ID provided, and could not send message in channel `{channel.name}`")
            sys.exit(1)
    return msg

# edit a specific message in a given guild w/ results
async def edit_message(guild, results):
    # results = ["Username: **number**", ...]
    # TODO: figure out how to determine the correct message to edit.
    msg = await find_editable_message(guild)
    new_content = "Pins:\n"
    for i,result in enumerate(results):
        new_content += f"\t{i+1}. {result}\n"

    new_content += f"Enjoy the gulag, bitches.\n(Last updated {strftime('%d/%m/%y %H:%M:%S', localtime())} CDT)"

    # print(new_content)
    try:
        await msg.edit(content=new_content)
    except discord.errors.Forbidden:
        sys.stderr.write(f"ERROR: Could not edit provided message. Msg_id = {msg.id}, channel = `{msg.channel.name}`")
        sys.exit(1)

@client.event
async def on_ready():

    print("Signed in as bot...")
    # TODO: pick the actual guild we want. right now we just grab the first one
    for g in client.guilds:
        if g.id == selected_guild_id:
            guild = g
            break
    else:
        print("ERROR: provided guildID is either invalid or the bot is not a member of the guild.")
        exit(1)
    
    members = await get_member_display_names(guild)
    pins = await get_all_pins_in_guild(guild)
    results = {}
    for msg in pins:
        if msg.author.name in members.keys() or msg.author.name in members.values():
            name = members.get(msg.author.name)
        else:
            name = msg.author.name
        if msg.author.name == client.user.name:
            continue # we don't count
        if name in results.keys():
            results[name] += 1
        else:
            results[name] = 1

    # we only want to update the message if there has been a change
    if os.path.isfile(f"{BASE_PATH}/prev-run.json"):
        prev_results_json = open(f"{BASE_PATH}/prev-run.json").read()
        prev_results = json.loads(prev_results_json)
        if prev_results == results:
            print("Nothing to do. Stopping...")
            await client.close()
            return

    results_as_json = json.dumps(results,indent=4)
    with open(f"{BASE_PATH}/prev-run.json", "w") as f:
        f.write(results_as_json)

    # sort the results
    sort_dict = lambda d: {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
    # lambda to flatten a dict into a list of strings
    flatten = lambda d: [f"{k}: {v}" for k,v in d.items()]
    results = flatten(sort_dict(results))
    print(results)

    await edit_message(guild, results)
    await client.close()

if __name__ == "__main__":
    client.run(my_token)
    
import sys
import socket
import string
import datetime
import pickle
import json
import random

import rng_build
import overlay

build_file = 'user_builds.pickle'
try:
    user_builds = pickle.load(open(build_file, 'rb'))
except FileNotFoundError:
    user_builds = {}

skill_tree = json.load(open('skill-tree.json.txt'))
build_maker = rng_build.BuildMaker(skill_tree)

def new_build(user, *args):
    builds = user_builds.get(user, [])
    build = build_maker.new()
    safe_chars = list(user.strip(string.digits + string.punctuation))
    random.shuffle(safe_chars)
    charname = ''.join(safe_chars)

    builds.append(build)
    user_builds[user] = builds
    pickle.dump(user_builds, open(build_file, 'wb'))

    return "Hey @{0}, you're going to be a {1}. I shall call you {2}".format(
        user, build.class_name.name, charname
    )

def level(user, *args):
    build = user_builds[user].pop()
    build_maker.choose_next_node(build)
    last_node = next(filter(
        lambda i: i['id'] == build.nodes[-1],
        skill_tree['nodes']
    ))
    url = build.url()
    user_builds[user].append(build)
    pickle.dump(user_builds, open(build_file, 'wb'))
    return "@{0}, allocate the {1} node. Your tree is now: {2}".format(
        user, last_node['dn'], url
    )

def current_build(user, *args):
    user = args[0]
    build = user_builds[user][-1]
    url = build.url()
    return "{0}'s current build is {1}".format(user, url)

def effective_experience(player_level, zone_level):
    safe_level_range = 3 + (player_level / 16)
    level_difference = abs(zone_level - player_level)
    effective_difference = 0
    if level_difference > safe_level_range:
        effective_difference = level_difference - safe_level_range

    multiplier = max((
        pow(player_level + 5, 1.5) /
        pow(player_level + 5 + pow(effective_difference, 2.5), 1.5)
    ), 0.02)
    return multiplier * 100

def drop_penalty(player_level, zone_level):
    player_level = min(player_level, 68)
    if player_level - zone_level <= 2:
        return 0
    return 2.5 * (player_level - (zone_level + 2))

def penalties(user, *args):
    try:
        char_level = int(args[0])
        zone_level = int(args[1])
    except (ValueError, IndexError):
        return "DansGame"
    exp = effective_experience(char_level, zone_level)
    drops = drop_penalty(char_level, zone_level)

    return "A level {0} character in a level {1} zone will gain {2:.2f}% experience and suffer a {3:.2f}% drop rate penalty".format(
        char_level, zone_level,
        exp, drops
    )

def info(user, *args):
    return "Beep boop, I understand these commands: !new -- create a new build. !passive -- get the next passive for your current build. !current USERNAME -- USERNAME's current build. !penalties CHARLEVEL ZONELEVEL -- exp/drop penalties."

def rules(user, *args):
    return "Solo, self-found, hardcore, four tabs, no pre-existing gear. No gem muling. All drops are fine. Master crafting is fine. I control your passives. No regrets. No respecs. -- !siosa for commands."

commands = {
    'penalties': penalties,
    'siosa': info,
    'new': new_build,
    'passive': level,
    'rules': rules,
    'current': current_build,
}

HOST="irc.twitch.tv"
PORT=6667
NICK="siosabot"
TOKEN=open('twitch.auth').read().strip()
CHANNELS = ["exhortatory"]

s = socket.socket()
s.connect((HOST, PORT))
s.send("PASS {0}\r\n".format(TOKEN).encode())
s.send("NICK {0}\r\n".format(NICK).encode())
s.send("JOIN {0}\r\n".format(",".join(map(lambda a: "#{0}".format(a), CHANNELS))).encode())

chat_display = overlay.Overlay(width=420, height=230, xpos=0, ypos=120)
readbuffer=""
while True:
    readbuffer += s.recv(1024).decode()
    temp = readbuffer.split("\n")
    readbuffer = temp.pop()

    for line in temp:
        parts = line.rstrip().split()

        if (parts[0] == "PING"):
            s.send("PONG {0}\r\n".format(parts[1]).encode())
        elif len(parts) > 3:
            sender = ""
            for char in parts[0]:
                if(char == "!"):
                    break
                if(char != ":"):
                    sender += char
            channel = parts[2]

            message = ' '.join([
                parts[3].replace(':', ''),
                ' '.join(parts[4:])
            ])

            chat_display.update(sender, message)

            command = parts[3].replace(":!", '')
            command = commands.get(command, None)
            if command:
                try:
                    response = command(sender, *parts[4:])
                    msg = "PRIVMSG {0} :{1}\r\n".format(channel, response)
                except:
                    msg = "PRIVMSG {0} :wtf is going on here DansGame\r\n".format(channel)
                finally:
                    s.send(msg.encode())
        print(line)

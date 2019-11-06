#!/usr/bin/env python3

import i3ipc
import re
import json
import os
from xdg.BaseDirectory import xdg_config_home, xdg_cache_home
import argparse
from shutil import copyfile
import requests

default_config = xdg_config_home + "/i3-workspace-names"


parser = argparse.ArgumentParser(
    description='Dynamically change i3wm workspace names depending on windows')

parser.add_argument(
    "-c", "--config", help="Set the config directory to a custom one")
parser.add_argument("--copy-config", help="Copy sample config to %s" %
                    default_config + "/icons.json or the provided config directory", action="store_true")
parser.add_argument("-u", "--update-icons",
                    help="Update icon list from FontAwesome", action="store_true")
parser.add_argument("-t", "--hide-titles",
                    help="Hide window titles from workspace names", action="store_true")
args = parser.parse_args()

i3 = i3ipc.Connection()


def get_icons():
    r = requests.get(
        'https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.json')
    j = json.loads(r.text)

    icons = {}

    for i in j:
        icons[i] = chr(int(j[i]['unicode'], 16))

    with open(xdg_cache_home + "/fa.json", 'w') as f:
        f.write(json.dumps(icons))


def replace(string):
    for key, val in icon_replace.items():
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        string = pattern.sub(icons[val], string)

    for i in string.split():
        if i.lower() in icons:
            string = string.replace(i, icons[i.lower()])

    for key, val in string_replace.items():
        string = string.replace(key, val)

    return string[:15]


def rename(i3, e):
    for i in i3.get_tree().workspaces():
        windows = ""
        for j in i.leaves():
            if j.window_class in apps:
                icon = icons[apps[j.window_class]]
            else:
                icon = j.window_class + ' '

            if args.hide_titles:
                windows += icon + ' '
            else:
                windows += icon + ' ' + replace(j.name) + ' '

        i3.command('rename workspace "%s" to "%s: %s"' %
                   (i.name, i.num, windows))


def main():
    global apps
    global icon_replace
    global string_replace
    global icons

    config_dir = default_config
    if args.config:
        config_dir = args.config

    if args.copy_config:
        try:
            if not os.path.isdir(config_dir):
                os.makedirs(config_dir)

            copyfile("config.example.json", config_dir + "/icons.json")
        except FileNotFoundError:
            copyfile("/usr/share/config.example.json",
                     config_dir + "/icons.json")

        print("Example config copied to %s" %
              config_dir + "/icons.json")
        return

    if args.update_icons:
        get_icons()
        print("Done")
        return

    try:
        with open(xdg_cache_home + "/fa.json") as j:
            icons = json.load(j)
    except IOError:
        get_icons()

    try:
        with open(config_dir + "/icons.json") as j:
            settings = json.load(j)
    except IOError:
        print("Config not found. Use --copy-config to create example config.")
        return

    apps = settings['apps']
    icon_replace = settings['icon_replace']
    string_replace = settings['string_replace']

    # Subscribe to events

    i3.on("window::move", rename)
    i3.on("window::new", rename)
    i3.on("window::title", rename)
    i3.on("window::close", rename)

    i3.main()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import i3ipc
import re
import json
import os
from xdg.BaseDirectory import xdg_config_home, xdg_cache_home
import argparse
from shutil import copyfile
import requests

PACKAGE_NAME = "i3-workspace-names"


class Settings:
    DEFAULT_CONFIG = xdg_config_home + "/" + PACKAGE_NAME + "/config.json"

    def __init__(self, args):
        self._config = args.config if args.config else Settings.DEFAULT_CONFIG
        self.apps = None
        self.icons = None
        self.strings = None
        self.args = args

    def hasConfig(self):
        return os.path.isfile(self._config)

    def load(self):
        try:
            with open(self._config) as j:
                settings = json.load(j)
                self.apps = settings['apps']
                self.icons = settings['icon_replace']
                self.strings = settings['string_replace']
        except IOError as e:
            print(f"Failed to read config file from {self._config}\n{e}")
            exit(1)

    def copy(self):
        try:
            dirname = os.path.dirname(self._config)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            copyfile("config.example.json", self._config)

            print(f"Example config copied to {self._config}")
        except Exception as e:
            print(f"Failed to create default config in {self._config}\n{e}")
            exit(1)


class Cache:
    DEFAULT_CACHE = xdg_cache_home + "/" + PACKAGE_NAME
    ICON_CACHE = "/fa.json"
    FONT_AWESOME_URL = 'https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.json'

    def __init__(self, cache_path):
        self._cache = cache_path if cache_path else Cache.DEFAULT_CACHE
        self.icons = None

        self.init_directory()

    def init_directory(self):
        try:
            if not os.path.isdir(self._cache):
                os.makedirs(self._cache)
        except IOError as e:
            print(
                f"Failed to initialise cache directory at {self._cache}\n{e}")

    def refresh_icons(self, icon_path=None):
        if icon_path is None:
            icon_path = self._cache + Cache.ICON_CACHE

        try:
            r = requests.get(Cache.FONT_AWESOME_URL)
            j = json.loads(r.text)

            icons = {}

            for i in j:
                icons[i] = chr(int(j[i]['unicode'], 16))

            with open(icon_path, 'w') as f:
                f.write(json.dumps(icons))

            print(
                f"Updated Font Awesome icon cache")
        except requests.exceptions.RequestException as e:
            print(
                f"Failed to retrieve icons from {Cache.FONT_AWESOME_URL}\n{e}")
            exit(1)
        except IOError as e:
            print(f"Failed to save icon cache to disk at {icon_path}\n{e}")
            exit(1)

    def load_fa(self, icon_path):
        if icon_path is None:
            icon_path = self._cache + Cache.ICON_CACHE

        if not os.path.isfile(icon_path):
            self.refresh_icons(icon_path)

        try:
            with open(icon_path, "r") as f:
                self.icons = json.load(f)

            print("Loaded icons from disk")
        except IOError as e:
            print(f"Failed to load icon cache file\n{e}")
            exit(1)


class WorkspaceRenamer:
    def __init__(self, cache, settings):
        self.cache = cache
        self.settings = settings
        self.i3 = i3ipc.Connection()

        # Subscribe to events
        self.i3.on("window::move", self.rename)
        self.i3.on("window::new", self.rename)
        self.i3.on("window::title", self.rename)
        self.i3.on("window::close", self.rename)

    def run(self):
        print("Started workspace renamer")
        self.i3.main()
        self.rename(self.i3, None)  # Force an initial refresh

    def replace(self, string):
        for key, val in self.settings.icons.items():
            pattern = re.compile(re.escape(key), re.IGNORECASE)
            string = pattern.sub(self.cache.icons[val], string)

        for i in string.split():
            if i.lower() in self.cache.icons:
                string = string.replace(i, self.cache.icons[i.lower()])

        for key, val in self.settings.strings.items():
            string = string.replace(key, val)

        return string[:15]

    def rename(self, i3, e):
        for i in i3.get_tree().workspaces():
            windows = ""
            for j in i.leaves():
                if j.window_class in self.settings.apps:
                    icon_name = self.settings.apps[j.window_class]
                    if icon_name in self.cache.icons:
                        icon = self.cache.icons[icon_name]
                    else:
                        icon = "N/A"
                else:
                    icon = j.window_class + ' '

                if self.settings.args.show_titles:
                    windows += icon + ' ' + self.replace(j.name) + ' '
                else:
                    windows += icon + ' '

            new_name = f"{i.num}"
            if windows:
                new_name += f": {windows}"

            i3.command(f'rename workspace "{i.name}" to "{new_name}"')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Dynamically change i3wm workspace names depending on windows')

    parser.add_argument("-c", "--config",
                        help="Use a custom config file")
    parser.add_argument("-x", "--cache",
                        help="Cache directory for icons")
    parser.add_argument("-i", "--icons",
                        help="Use a custom icon cache file")
    parser.add_argument("-u", "--update-icons",
                        help="Update icon list from FontAwesome", action="store_true")
    parser.add_argument("-s", "--show-titles",
                        help="Hide window titles from workspace names", action="store_true")
    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    cache = Cache(args.cache)
    settings = Settings(args)

    if not settings.hasConfig():
        settings.copy()

    if args.update_icons:
        cache.refresh_icons(args.icons)
    else:
        cache.load_fa(args.icons)
        settings.load()

        renamer = WorkspaceRenamer(cache, settings)
        renamer.run()


if __name__ == "__main__":
    main()

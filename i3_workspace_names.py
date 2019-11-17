#!/usr/bin/env python3

import i3ipc
import re
import json
import os
from xdg.BaseDirectory import xdg_config_home, xdg_cache_home, xdg_data_home
import argparse
from shutil import copyfile, copy, move
import requests
import subprocess
import traceback

PACKAGE_NAME = "i3-workspace-names"


class Settings:
    CONFIG_DIR = xdg_config_home + "/" + PACKAGE_NAME
    CONFIG_FILE = CONFIG_DIR + "/config.json"

    def __init__(self, args):
        self.config = args.config if args.config else Settings.CONFIG_FILE
        self.apps = None
        self.icons = None
        self.strings = None
        self.args = args

    def hasConfig(self):
        return os.path.isfile(self.config)

    def load(self):
        try:
            with open(self.config) as j:
                settings = json.load(j)
                self.apps = settings['apps']
                self.icons = settings['icon_replace']
                self.strings = settings['string_replace']
        except IOError:
            traceback.print_exc()
            exit(f"Failed to read config file from {self.config}")

    def copy(self):
        try:
            dirname = os.path.dirname(self.config)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            copyfile("config.example.json", self.config)

            print(f"Example config copied to {self.config}")
        except Exception:
            traceback.print_exc()
            exit(f"Failed to create default config in {self.config}")

    def get_application(self, name):
        if name in self.apps:
            return self.apps[name]

        return None


class FontBuilder:
    SOURCE_DIR = "/icons"
    FONT_NAME = (PACKAGE_NAME + "-font").replace("-", "_")
    FONT_DIR = xdg_data_home + "/fonts/"
    COMMAND_FORMAT = "icon-font-generator {source}/*.svg --types ttf --css false --html false --name {font_name}" + \
        " --out {target} --normalize true --center"

    def __init__(self, cache, args):
        self.cache = cache
        self.args = args

        self.target = cache.directory
        self.source = args.build_source if args.build_source \
            else Settings.CONFIG_DIR + FontBuilder.SOURCE_DIR

    def build(self):
        try:
            command = FontBuilder.COMMAND_FORMAT.format(
                font_name=FontBuilder.FONT_NAME,
                target=self.target,
                source=self.source
            ).split(" ")

            result = subprocess.run(
                command,
                check=True,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

            print(result.stdout)

            self.convert_json()

        except subprocess.CalledProcessError:
            traceback.print_exc()
            exit(f"Failed to build font with command {command}")

    def convert_json(self):
        try:
            json_file = self.target + "/" + FontBuilder.FONT_NAME + ".json"
            data = None
            with open(json_file, "r") as f:
                data = json.load(f)

            for icon in data:
                data[icon] = chr(int(data[icon][1:], 16))

            with open(json_file, "w") as f:
                json.dump(data, f)

            print("Successfully converted custom cache file")
        except IOError:
            traceback.print_exc()
            exit(f"Failed to convert custom font json cache file")

    def get_build_names(self):
        file_types = ['json', 'ttf']
        files = [FontBuilder.FONT_NAME + "." + ft for ft in file_types]
        return files

    def build_exists(self):
        files = self.get_build_names()
        for f in files:
            if not os.path.isfile(self.target + "/" + f):
                return False

        return True

    def clean(self):
        names = self.get_build_names()
        build_absolute = [self.target + "/" + b for b in names]
        build_absolute.append(FontBuilder.FONT_DIR + "/" +
                              FontBuilder.FONT_NAME + ".ttf")
        build_absolute.append(self.cache.directory + Cache.CUSTOM_CACHE)
        try:
            for build in build_absolute:
                if os.path.isfile(build):
                    print(f"Removing {build}")
                    os.remove(build)

            print("Finished build cleaning")
        except IOError:
            traceback.print_exc()
            exit("Failed to clean build files")

    def install(self):
        try:
            self.clean()
            self.build()

            if not os.path.isdir(FontBuilder.FONT_DIR):
                os.makedirs(FontBuilder.FONT_DIR)

            move(
                self.target + "/" + FontBuilder.FONT_NAME + ".ttf",
                FontBuilder.FONT_DIR
            )

            move(
                self.target + "/" + FontBuilder.FONT_NAME + ".json",
                self.cache.directory + Cache.CUSTOM_CACHE
            )

            print("Installed icon font for local user")
        except IOError:
            traceback.print_exc()
            exit(f"Failed to install font to {FontBuilder.FONT_DIR}")


class Cache:
    CACHE_DIR = xdg_cache_home + "/" + PACKAGE_NAME
    ICON_CACHE = "/fa.json"
    CUSTOM_CACHE = "/custom.json"
    FONT_AWESOME_URL = 'https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.json'

    def __init__(self, cache_path):
        self.directory = cache_path if cache_path else Cache.CACHE_DIR
        self.icons = None

        self.init_directory()

    def init_directory(self):
        try:
            if not os.path.isdir(self.directory):
                os.makedirs(self.directory)
        except IOError:
            traceback.print_exc()
            exit(f"Failed to initialise cache directory at {self.directory}")

    def refresh_icons(self, icon_path=None):
        if icon_path is None:
            icon_path = self.directory + Cache.ICON_CACHE

        try:
            r = requests.get(Cache.FONT_AWESOME_URL)
            j = json.loads(r.text)

            icons = {}

            for i in j:
                icons[i] = chr(int(j[i]['unicode'], 16))

            with open(icon_path, 'w') as f:
                json.dump(icons, f)

            print(
                f"Updated Font Awesome icon cache")
        except requests.exceptions.RequestException:
            traceback.print_exc()
            exit(f"Failed to retrieve icons from {Cache.FONT_AWESOME_URL}")
        except IOError:
            traceback.print_exc()
            exit(f"Failed to save icon cache to disk at {icon_path}")

    def load_fa(self, icon_path):
        if icon_path is None:
            icon_path = self.directory + Cache.ICON_CACHE

        if not os.path.isfile(icon_path):
            self.refresh_icons(icon_path)

        try:
            with open(icon_path, "r") as f:
                self.icons = json.load(f)

            print("Loaded icons from disk")
        except IOError:
            traceback.print_exc()
            exit(f"Failed to load icon cache file from {icon_path}")

    def load_custom(self):
        custom_path = self.directory + Cache.CUSTOM_CACHE
        if os.path.isfile(custom_path):
            try:
                with open(custom_path, "r") as f:
                    self.custom = json.load(f)

                print("Loaded custom icons from disk")
            except IOError:
                traceback.print_exc()
                exit(f"Failed to load custom icon cache for {custom_path}")


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
        for workspace in i3.get_tree().workspaces():
            title = ""
            for window in workspace.leaves():
                if window.window_class in self.settings.apps:
                    icon_name = self.settings.apps[window.window_class]

                    if icon_name in self.cache.custom:
                        icon = self.cache.custom[icon_name]
                    elif icon_name in self.cache.icons:
                        icon = self.cache.icons[icon_name]
                    else:
                        icon = "N/A"
                else:
                    icon = window.window_class + ' '

                if self.settings.args.show_titles:
                    title += icon + ' ' + self.replace(window.name) + ' '
                else:
                    title += icon + ' '

            new_name = f"{workspace.num}"
            if title:
                new_name += f": {title}"

            i3.command(f'rename workspace "{workspace.name}" to "{new_name}"')


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
    parser.add_argument("-b", "--build-font",
                        help="Build icon font from SVGs", action="store_true")
    parser.add_argument("--build-source",
                        help="Source directory with SVGs for font builder")
    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    cache = Cache(args.cache)
    settings = Settings(args)
    builder = FontBuilder(cache, args)

    if not settings.hasConfig():
        settings.copy()

    if args.update_icons:
        cache.refresh_icons(args.icons)
    elif args.build_font:
        builder.install()
    else:
        cache.load_fa(args.icons)
        cache.load_custom()
        settings.load()

        renamer = WorkspaceRenamer(cache, settings)
        renamer.run()


if __name__ == "__main__":
    main()

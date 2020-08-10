# i3-workspace-names

## About

`i3-workspace-names` dynamically changes the names of workspaces depending on what windows are open in them. Names of applications and keywords are replaced with icons from FontAwesome.

## Install

Install from `pip`

```
pip install i3-workspace-names
```

Install from `AUR`

```
yay -S i3-workspace-names
```

## Usage

```
usage: i3_workspace_names.py [-h] [-c CONFIG] [-x CACHE] [-i ICONS] [-u] [-s] [-b]
                             [--build-source BUILD_SOURCE]

Dynamically change i3wm workspace names depending on windows

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Use a custom config file
  -x CACHE, --cache CACHE
                        Cache directory for icons
  -i ICONS, --icons ICONS
                        Use a custom icon cache file
  -u, --update-icons    Update icon list from FontAwesome
  -s, --show-titles     Hide window titles from workspace names
  -b, --build-font      Build icon font from SVGs
  --build-source BUILD_SOURCE
                        Source directory with SVGs for font builder
```

Copy default config to home directory. Icons will be downloaded on first run.

Add this to your i3 config:

```
exec_always --no-startup-id exec i3-workspace-names
```

Workspace switching keybinds should be similar to the code below (note the `number` keyword):

```
set $workspace1 "1"
bindsym $mod+1 workspace number $workspace1
```

Polybar users may have to add the following to their config:

```
font-1 = FontAwesome5Free:style=Solid:size=10;1
font-2 = FontAwesome5Free:style=Regular:size=10;1
font-3 = FontAwesome5Brands:style=Regular:size=10;1
```

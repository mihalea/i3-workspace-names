# i3-workspace-names

[![pipeline status](https://gitlab.com/flib99/i3-workspace-names/badges/master/pipeline.svg)](https://gitlab.com/flib99/i3-workspace-names/commits/master)

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
usage: i3-workspace-names [-h] [--copy-config] [-u]

Dynamically change i3wm workspace names depending on windows

optional arguments:
  -h, --help          show this help message and exit
  --copy-config       copy sample config to
                      /home/$USER/.config/i3/icons.json
  -u, --update-icons  Update icon list from FontAwesome
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
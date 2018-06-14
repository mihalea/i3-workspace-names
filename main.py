import i3ipc
import re
from icons import icons
import json
from xdg import XDG_CONFIG_HOME

i3 = i3ipc.Connection()

with open(XDG_CONFIG_HOME + "/i3/icons.json") as j:
    settings = json.load(j)


apps = settings['apps']

replaces = settings['strings']

print(json.dumps(replaces))


def replace(string):
    for key, val in replaces.items():
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        string = pattern.sub(val, string)

    for i in string.split():
        print(i)
        if i.lower() in icons:
            string = string.replace(i, icons[i.lower()])

    return string[:15]


def rename(i3, e):
    for i in i3.get_tree().workspaces():
        windows = ""
        for j in i.leaves():
            if j.window_class in apps:
                icon = apps[j.window_class]
            else:
                icon = j.window_class + ' '

            windows += icon + ' ' + replace(j.name) + ' '

        print(i3.command('rename workspace "%s" to "%s: %s"' %
                         (i.name, i.num, windows)))


def main():

    # Subscribe to events

    i3.on("window::move", rename)
    i3.on("window::new", rename)
    i3.on("window::title", rename)
    i3.on("window::close", rename)

    i3.main()


if __name__ == "__main__":
    main()

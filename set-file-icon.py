#!/usr/bin/python
# macOS File Icon Setter
# Description: Set the icon for specific files on macOS. Credit to Apple
# StackExchange user [kolen](https://apple.stackexchange.com/users/77404/kolen)
# for the [solution](https://apple.stackexchange.com/a/161984/300078).
# Requirements: pyobjc
# Notes: pyobjc is needed to access the Cocoa python module. The macOS
# system python `/usr/bin/python` already has pyobjc installed so no
# additional package installations are required. If using a specific python
# installation (i.e. Homebrew, MacPorts) is preferred, then pyobjc can be
# installed via pip: `pip install pyobjc`.

import argparse


import Cocoa


def set_file_icon(file_path, icon_file_path):
    return Cocoa.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(
        Cocoa.NSImage.alloc().initWithContentsOfFile_(icon_file_path),
        file_path,
        0
    )


def main():
    parser = argparse.ArgumentParser(
        description="Set the icon for specific files on macOS.")
    parser.add_argument('file_path', metavar='FILE', type=str, help='')
    parser.add_argument('icon_file_path', metavar='ICONFILE', type=str, help='')
    args = parser.parse_args()
    try:
        set_file_icon(args.file_path, args.icon_file_path)
    except Exception as inst:
        print("Unknown error occurred:", inst)


if __name__ == '__main__':
    main()

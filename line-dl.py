#!/usr/bin/env python3
# Line Sticker Download Script
# A Python 3 script to download line stickers in PNG format.
# Requirements: requests

import argparse
import os
import re

from subprocess import call

import requests

REGEX_STICKER_FILE_URL = r'https?:\/\/(?:[-\/\w.]|(?:%[\da-fA-F]{2}))+;compress=true'
REGEX_STICKER_SPAN = "".join((
        r'<span class="\w+" style="background\-image:',
        r'url\(',
        REGEX_STICKER_FILE_URL,
        r'\);"'
    )
)
# Expecting span element of the form:
# <span class="mdCMN09Image"
# style="background-image: url([URL];compress=true);"


def main():
    parser = argparse.ArgumentParser(description="Download Line Stickers in PNG format.")
    parser.add_argument('urls', metavar='URLs', type=str, nargs='+',
                        help='URL of sticker page. Example: https://store.line.me/stickershop/product/1249335/')
    args = parser.parse_args()

    for url in args.urls:
        try:
            req = requests.get(url)
            text = " ".join(req.text.split())
        except requests.exceptions.ConnectionError:
            print("Connection error. Are you connected to the internet?",
                  "Is Line down?"
                  )
            continue
        else:
            print("Something went wrong when opening the URL.",
                  "Is the URL valid?")
            continue
        try:
            sticker_count = len(re.findall(REGEX_STICKER_SPAN, text, flags=re.IGNORECASE))
            first_sticker = re.search(REGEX_STICKER_SPAN, text, flags=re.IGNORECASE)

            first_sticker_id = re.search(r'\/\d+\/', first_sticker.group(0))
            first_sticker_id = int(first_sticker_id.group(0).replace("/", ""))

            last_sticker_id = first_sticker_id + (sticker_count - 1)

            base_url = re.search(REGEX_STICKER_FILE_URL,
                                 first_sticker.group(0))
            base_url = base_url.group(0).replace(";compress=true", "")

            dirname = re.search(r'<h3 class="\w+\">[\w\.,"\'\-; ]+<\/h3>',
                                text).group(0).lower()
            dirname = re.sub(r'<h3 class="\w+\">', "", dirname)
            dirname = dirname.replace("</h3>", "")
            dirname = re.sub(r'[^\w\&]', "-", dirname)
        else:
            print("""
                Requested page does not contain a sticker element.
                Either Line has changed the webpage schema, or an invalid URL was used.
            """)
            continue

        # try:
        #     os.mkdir(dirname)
        # except:
        #     pass
        # os.chdir(dirname)

        # for i in range(first_sticker_id, last_sticker_id + 1):
        #     sticker_url = base_url.replace(str(first_sticker_id), str(i))
        #     print(sticker_url)
        #     call(['curl', sticker_url, '-o', f'{str(i)}.png'])

        # os.chdir("..")


if __name__ == "__main__":
    main()

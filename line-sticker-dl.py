#!/usr/bin/env python3
# Line Sticker Download Script
# Description: A Python 3 script to download line stickers in PNG format.
# Requirements: requests

import argparse
import os
import re
import sys

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


def download_file(url: str, save_path: str, name: str=""):
    req = requests.get(url, stream=True)
    total_length = req.headers.get('content-length')
    if total_length is None:
        raise Exception("Invalid response from server.")
    else:
        total_length = int(total_length)
    with open(save_path, 'wb') as f:
        total_data = 0
        for data in req.iter_content(chunk_size=1024): 
            if data:
                total_data += len(data)
                f.write(data)
                done = int(100 * total_data / total_length)
                sys.stdout.write(f"\rDownloading{' ' + name if name else name} {done}%")
                sys.stdout.flush()


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
        except Exception as inst:
            print("Something went wrong when opening the URL.",
                  "Is the URL valid?")
            continue

        try:
            sticker_type = re.search(r'type: \"\w+\"', text).group(0)
            sticker_type = sticker_type.replace("type: \"", "").replace("\"", "")
            sticker_count = len(re.findall(REGEX_STICKER_SPAN, text, flags=re.IGNORECASE))
            first_sticker = re.search(REGEX_STICKER_SPAN, text, flags=re.IGNORECASE)

            first_sticker_id = re.search(r'\/\d+\/', first_sticker.group(0))
            first_sticker_id = int(first_sticker_id.group(0).replace("/", ""))

            last_sticker_id = first_sticker_id + (sticker_count - 1)

            base_url = re.search(REGEX_STICKER_FILE_URL,
                                    first_sticker.group(0))
            base_url = base_url.group(0).replace(";compress=true", "")

            stickerset_name = re.search(r'<h3 class="\w+\">[\w\.,"\'\-; ]+<\/h3>',
                                text).group(0)
            stickerset_name = re.sub(r'<h3 class="\w+\">', "", stickerset_name)
            stickerset_name = stickerset_name.replace("</h3>", "")
            dirname = re.sub(r'[^\w\&]', "-", stickerset_name).lower()
        except Exception as inst:
            print("""
                Requested page does not contain a sticker element.
                Either Line has changed the webpage schema, or an invalid URL was used.
            """)
            continue

        try:
            os.mkdir(dirname)
        except Exception as inst:
            pass
        os.chdir(dirname)

        # Download PNG Stickers
        print("Downloading stickers from", stickerset_name)
        for i in range(first_sticker_id, last_sticker_id + 1):
            sticker_url = base_url.replace(str(first_sticker_id), str(i))
            download_file(sticker_url, f'{str(i)}.png', f"Sticker {1 + i - first_sticker_id}/{sticker_count}")
        print("\n")
        os.chdir("..")

        # Download PNG Animations
        if sticker_type == "animation":
            print("Downloading sticker animations from", stickerset_name)
            try:
                os.mkdir(f"{dirname}_animations")
            except Exception as inst:
                pass
            os.chdir(f"{dirname}_animations")

            animation_base_url = re.sub(r'android\/sticker.png', "IOS/sticker_animation@2x.png", base_url, flags=re.IGNORECASE)
            for i in range(first_sticker_id, last_sticker_id + 1):
                animation_url = animation_base_url.replace(str(first_sticker_id), str(i))
                download_file(animation_url, f'{str(i)}.png', f"Animation {1 + i - first_sticker_id}/{sticker_count}")
            print("")
            os.chdir("..")


if __name__ == "__main__":
    main()

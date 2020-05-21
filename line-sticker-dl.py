#!/usr/bin/env python3
# Line Sticker Download Script
# Description: A Python 3 script to download line stickers in PNG format.
# Requirements: requests

import argparse
import json
import os
import re
import sys

import requests

REGEX_STICKER_LIST_ITEM = "".join(
    (
        r'<li\s+class="mdCMN09Li FnStickerPreviewItem"\s+data\-preview=\''
        r'{[^\}]+}',
        '\'>'
    )
)


def sticker_li_str_to_dict(sticker_li: str) -> dict:
    sticker_json_data_str = re.search(r'{[^\}]+}', sticker_li).group(0)
    sticker_json_data_str = sticker_json_data_str.replace("&quot;", '"')
    sticker_json_data = json.loads(sticker_json_data_str)
    return sticker_json_data


def download_file(url: str, save_path: str, name: str = ""):
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
    parser = argparse.ArgumentParser(
        description="Download Line Stickers in PNG format."
    )
    parser.add_argument('urls', metavar='URLs', type=str, nargs='+',
                        help='URL of sticker page. Example: '
                        + 'https://store.line.me/stickershop/product/1249335/')
    args = parser.parse_args()

    for url in args.urls:
        try:
            req = requests.get(url)
            text = " ".join(req.text.split())
        except requests.exceptions.ConnectionError:
            print(
                "Connection error. Are you connected to the internet?",
                "Is Line down?"
            )
            continue
        except Exception as inst:
            print(
                "Something went wrong when opening the URL.",
                "Is the URL valid?",
                inst
            )
            continue

        sticker_li_arr = re.findall(
            REGEX_STICKER_LIST_ITEM, text, flags=re.IGNORECASE)
        if not sticker_li_arr:
            print(
                "Requested page does not contain a sticker element.",
                "Either Line has changed the webpage schema, or an invalid URL was used."
            )
            continue

        try:
            stickerset_name = re.search(
                r'<p class="mdCMN38Item01Ttl">(.*?)<\/p>', text).group(0)
            stickerset_name = stickerset_name.replace(
                '<p class="mdCMN38Item01Ttl">', "")
            stickerset_name = stickerset_name.replace("</p>", "")
            dirname = re.sub(r'[^\w\&]', "-", stickerset_name).lower()
        except Exception as inst:
            print(
                "Unable to find name of sticker set.",
                "Either Line has changed the webpage schema, or an invalid URL was used.",
                inst
            )
            continue

        if os.path.exists(dirname):
            print(f"The file or directory '{dirname}' already exists.")
            prompt = input("Overwrite? [yY/nN]: ")
            if prompt.lower() == 'y':
                if os.path.isfile(dirname):
                    os.remove(dirname)
                print("\n")
            else:
                print("Skipping this sticker set.")
                continue
        else:
            try:
                os.mkdir(dirname)
            except Exception as inst:
                print(
                    "Unable to create directory for sticker set.",
                    inst
                )
                continue
        os.chdir(dirname)

        # Download PNG Stickers
        print("Downloading stickers for", stickerset_name)
        sticker_count = len(sticker_li_arr)
        sticker_dict_arr = list(map(sticker_li_str_to_dict, sticker_li_arr))
        for i, sticker_dict in enumerate(sticker_dict_arr):
            download_file(
                sticker_dict["staticUrl"],
                f'{sticker_dict["id"]}.png',
                f"Sticker {i + 1}/{sticker_count}"
            )
        print("\n")

        print("Checking if sticker has animations.")
        has_animations = False
        for sticker_dict in sticker_dict_arr:
            if sticker_dict["animationUrl"] != "":
                has_animations = True
                break

        if has_animations:
            print("Downloading animations for", stickerset_name)
            for (i, sticker_dict) in enumerate(sticker_dict_arr):
                if sticker_dict["animationUrl"] != "":
                    download_file(
                        sticker_dict["animationUrl"],
                        f'{sticker_dict["id"]}_animation.png',
                        f"Animation {i + 1}/{sticker_count}"
                    )
            print("\n")
            os.chdir("..")
        else:
            print("No animations found.")


if __name__ == "__main__":
    main()

from bs4 import BeautifulSoup
import ffmpy
import requests
import os
from cv2 import VideoCapture, CAP_PROP_FPS
import argparse

parser = argparse.ArgumentParser(description="Download and convert Arcacons to gifs.")
parser.add_argument(
    "arcacon_id",
    help="The ID of the Arcacon you want to download. This will most likely be a 4-digit number.",
    type=int,
)
parser.add_argument(
    "-s", "--single_palette",
    help="Use a single 256-color palette to display the colors in the GIF file instead of using a palette for each frame. This will reduce the file size, but may be low quality if the GIF file has many colors and/or frames.",
    action="store_true"
)
args = parser.parse_args()

URL = f"https://arca.live/e/{args.arcacon_id}"
page = requests.get(URL)

soup = BeautifulSoup(page.text, "html.parser")
body = soup.find("div", {"class": "article-body"})
icons = body.find_all(loading="lazy")
title = f"[{args.arcacon_id}] {soup.title.text}".replace('/', ' ')

if not os.path.exists(title):
    os.mkdir(title)
else:
    i = input(f'Icon directory "{title}" already exists. Continue? [Y/n] ')
    if i.lower() == "n":
        print("Terminating script...")
        quit()

os.chdir(title)

for num, i in enumerate(icons):
    icon_url = "https:" + i["src"]
    if icon_url.endswith("mp4"):
        # GIF
        with open("temp.mp4", "wb") as f:
            r = requests.get(icon_url, allow_redirects=True)
            if r.status_code == 200:
                f.write(r.content)
            else:
                print("Error fetching icon; skipping...")
        # For each icon, save the frame palette and use this palette to generate the gif
        # This removes the "blotchy" effects you would get from converting mp4 to gif otherwise

        if args.single_palette:
            ffmpeg_arg = '-filter_complex "[0:v] split [a][b];[a] palettegen [p];[b][p] paletteuse"'
        else:
            ffmpeg_arg = '-filter_complex "[0:v] split [a][b];[a] palettegen=stats_mode=single [p];[b][p] paletteuse=new=1"'

        # GIFs support a maximum frame rate of 50 fps.
        # If temp.mp4 exceeds 50, then we limit it.
        cap = VideoCapture("temp.mp4")
        if cap.get(CAP_PROP_FPS) > 50:
            ff = ffmpy.FFmpeg(
                inputs={"temp.mp4": None},
                outputs={f"{num}.gif": f'{ffmpeg_arg} -r 50'},
            )
        else:
            ff = ffmpy.FFmpeg(
                inputs={"temp.mp4": None},
                outputs={f"{num}.gif": ffmpeg_arg},
            )
        ff.run()
        cap.release()
        os.remove("temp.mp4")
    else:
        # Save the file as is
        ext = icon_url.split(".")[-1]
        with open(f"{num}.{ext}", "wb") as f:
            r = requests.get(icon_url, allow_redirects=True)
            if r.status_code == 200:
                f.write(r.content)
            else:
                print("Error fetching icon; skipping...")

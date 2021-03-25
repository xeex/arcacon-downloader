from io import BytesIO
from json import loads
import os
from requests import Session
import argparse

parser = argparse.ArgumentParser(description="Download DCcons.")
parser.add_argument(
    "dccon_id",
    help="The ID of the DCcon you want to download. To find this, navigate to \
        the DCcon you want, then hover over the icon and read the number at \
            the end.",
    type=int,
)
args = parser.parse_args()

session = Session()
session.get("https://dccon.dcinside.com/")

details = loads(
    session.post(
        "https://dccon.dcinside.com/index/package_detail",
        data={
            "ci_t": session.cookies.get("ci_c"),
            "package_idx": args.dccon_id,
        },
        headers={"X-Requested-With": "XMLHttpRequest"},
    ).text
)

DIR_NAME = f"({args.dccon_id}) {details['info']['title']}"

if not os.path.exists(DIR_NAME):
    os.mkdir(DIR_NAME)
else:
    i = input(f'Icon directory "{DIR_NAME}" already exists. Continue? [Y/n] ')
    if i.lower() == "n":
        print("Terminating script...")
        quit()
os.chdir(DIR_NAME)

imgs = {
    "{}.{}".format(i["title"], i["ext"]): BytesIO(
        session.get(
            "https://dcimg5.dcinside.com/dccon.php?no={}".format(i["path"]),
            headers={"Referer": "http://dccon.dcinside.com/"},
        ).content
    )
    for i in details["detail"]
}
for name, image in imgs.items():
    with open(name, "wb") as f:
        f.write(image.getbuffer())

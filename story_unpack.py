import os
import json
import msgpack
import requests
import lz4.block as lb
from src.read_ini import config

_story_ID = config.get("Download Data", "stroy_ID")
_Episode_Len = config.getint("Download Data", "Episode_Len")
_Episode_PATH = config.get("File PATH", "Episode_PATH")
_Episode_list: list[str] = []

os.makedirs(f"{_Episode_PATH}/{_story_ID}", exist_ok=True)

for seq in range(1, _Episode_Len + 1):
    _Episode_list.append(_story_ID + "{:0>2}".format(seq))

for Episode in _Episode_list:
    url = f"https://assets.wds-stellarium.com/master-data/production/scenes/{Episode}.bin"
    res = requests.get(url)

    deserialized = msgpack.unpackb(res.content)
    decompressed = b""
    for data in deserialized:
        if isinstance(data, bytes):
            decompressed += lb.decompress(data, uncompressed_size=1024 * 1024)
    obj = msgpack.unpackb(decompressed, raw=False)

    Episode_data: list[dict] = []
    with open(f"{_Episode_PATH}/{_story_ID}/{Episode}.json", "w+", encoding="utf-8") as wf:
        for part in obj:
            if part[7] != "":
                Episode_data.append({"GroupOrder": part[3], "SpeakerName": part[5], "Phrase": part[7]})
        json.dump(Episode_data, wf, ensure_ascii=False)

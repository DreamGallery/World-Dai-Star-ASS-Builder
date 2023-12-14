import os
import json
import msgpack
import requests
import lz4.block as lb
from src.read_ini import config

_EPISODE_PATH = config.get("File Path", "EPISODE_PATH")
_story_id = config.get("Download Data", "story_id")
_episode_len = config.getint("Download Data", "episode_len")
_episode_list: list[str] = []

os.makedirs(f"{_EPISODE_PATH}/{_story_id}", exist_ok=True)

for seq in range(1, _episode_len + 1):
    _episode_list.append(_story_id + "{:0>2}".format(seq))

for episode in _episode_list:
    url = f"https://assets.wds-stellarium.com/master-data/production/scenes/{episode}.bin"
    res = requests.get(url)

    deserialized = msgpack.unpackb(res.content)
    decompressed = b""
    for data in deserialized:
        if isinstance(data, bytes):
            decompressed += lb.decompress(data, uncompressed_size=1024 * 1024)
    obj = msgpack.unpackb(decompressed, raw=False)

    episode_data: list[dict] = []
    with open(f"{_EPISODE_PATH}/{_story_id}/{episode}.json", "w+", encoding="utf-8") as wf:
        for part in obj:
            if part[7] != "":
                episode_data.append({"GroupOrder": part[3], "SpeakerName": part[5], "Phrase": part[7]})
        json.dump(episode_data, wf, ensure_ascii=False)

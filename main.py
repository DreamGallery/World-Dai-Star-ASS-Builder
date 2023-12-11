import json
from src.frame import *
from src.create_axis import *
from src.read_ini import config
from src.ass_part import script_info, garbage, styles, events


ASS_PATH = config.get("File PATH", "ASS_PATH")
Episode_PATH = config.get("File PATH", "Episode_PATH")
story_ID = config.get("Download Data", "stroy_ID")
EpisodeMasterId = config.getint("Download Data", "EpisodeMasterId")
video_file_name = config.get("Info", "video_file_name")
ass_file_name = config.get("Info", "ass_file_name")

story_json_path = f"{Episode_PATH}/{story_ID}/{EpisodeMasterId}.json"
with open(story_json_path, "r", encoding="utf-8") as json_file:
    Episode_json = json.load(json_file)

SpeakerName_list: list[str] = []
for part in Episode_json:
    if str(part["SpeakerName"]) not in SpeakerName_list:
        SpeakerName_list.append(str(part["SpeakerName"]))

SpeakerName_list.sort(key=lambda x: len(x), reverse=True)
stream = FrameProcess()
image_list, image_info_list = stream.to_frame(video_file_name, SpeakerName_list)

Mask_event_list = echo_Mask_event(image_info_list)
SpeakerName_event_list = echo_SpeakerName_event(image_info_list, SpeakerName_list)
Phrase_event_list = echo_Phrase_event(image_list, image_info_list, Episode_json)

try:
    with open(f"{ASS_PATH}/{ass_file_name}", "+w", encoding="utf-8") as ass_file:
        content = script_info + "\n" + garbage + "\n" + styles + "\n" + events
        for Mask_event in Mask_event_list:
            content = content + Mask_event + "\n"
        for SpeakerName_event in SpeakerName_event_list:
            content = content + SpeakerName_event + "\n"
        for Phrase_event in Phrase_event_list:
            content = content + Phrase_event + "\n"
        ass_file.write(content)
    print(f"\nMatch process finished, {ass_file_name} has been successfully created!")
except Exception as e:
    print(f"\n{ass_file_name} creating failed. Info: {e}")

import json
from src.frame import *
from src.create_axis import *
from src.read_ini import config
from src.ass_part import script_info, garbage, styles, events


ASS_PATH = config.get("File Path", "ASS_PATH")
EPISODE_PATH = config.get("File Path", "Episode_PATH")
story_id = config.get("Download Data", "story_id")
episode_master_id = config.getint("Download Data", "episode_master_id")
video_file_name = config.get("Info", "video_file_name")
ass_file_name = config.get("Info", "ass_file_name")

story_json_path = f"{EPISODE_PATH}/{story_id}/{episode_master_id}.json"
with open(story_json_path, "r", encoding="utf-8") as json_file:
    episode_json = json.load(json_file)

speaker_name_list: list[str] = []
for part in episode_json:
    if str(part["SpeakerName"]) not in speaker_name_list:
        speaker_name_list.append(str(part["SpeakerName"]))

speaker_name_list.sort(key=lambda x: len(x), reverse=True)
stream = FrameProcess()
image_list, image_info_list = stream.to_frame(video_file_name, speaker_name_list)

mask_event_list = echo_mask_event(image_info_list)
speaker_name_event_list = echo_speaker_name_event(image_info_list, speaker_name_list)
phrase_event_list = echo_phrase_event(image_list, image_info_list, episode_json)

try:
    with open(f"{ASS_PATH}/{ass_file_name}", "+w", encoding="utf-8") as ass_file:
        content = script_info + "\n" + garbage + "\n" + styles + "\n" + events
        for Mask_event in mask_event_list:
            content = content + Mask_event + "\n"
        for speaker_name_event in speaker_name_event_list:
            content = content + speaker_name_event + "\n"
        for phrase_event in phrase_event_list:
            content = content + phrase_event + "\n"
        ass_file.write(content)
    print(f"\nMatch process finished, {ass_file_name} has been successfully created!")
except Exception as e:
    print(f"\n{ass_file_name} creating failed. Info: {e}")

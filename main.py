import os
import configparser
from src.frame import *
from src.ass_part import script_info, garbage, styles, events
from src.events import ass_events

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_PATH ,'config.ini'), encoding="utf-8")
ASS_PATH = config.get("File PATH", "ASS_PATH")
video_file_name = config.get("Info", "video_file_name")
ass_file_name = config.get("Info", "ass_file_name")
Mask_text = config.get("Mask", "Mask_text")

def to_time(clip_time: float) -> str:
    H = clip_time // 3600
    M = (clip_time - H * 3600)//60
    S = clip_time - H * 3600 - M * 60
    _time = '%02d:%02d:%05.2f' %(H,M,S)
    return _time

stream = frame_stream()
start_time_list = stream.to_frame(video_file_name)
content = script_info + "\n" + garbage + "\n" + styles + "\n" + events
Mask_event = ass_events(layer=0, start = "0:00:00.00", end = "0:00:05.00", style = "Default", name = "遮罩示例", text = Mask_text)
content = content + Mask_event.echo_dialogue() + "\n"
for index in range(len(start_time_list)):
    if (index + 1) == len(start_time_list):
        start_time = to_time(start_time_list[index])
        end_time = ""
    else:
        start_time = to_time(start_time_list[index])
        end_time = to_time(start_time_list[index + 1] - 0.01)
    _event = ass_events(layer = 2, start = start_time , end = end_time , style = "手游剧情-单行")
    content = content + f"{_event.echo_dialogue()}" + "\n"
try:
    with open(f"{ASS_PATH}/{ass_file_name}", "w", encoding="utf8") as fp:
        fp.write(content)
    print(f"\n{ass_file_name} successfully generated")
except:
    print(f"\ngenerated failed")

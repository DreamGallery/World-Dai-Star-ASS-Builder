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
Dial_Mask_text = config.get("Mask", "Dial_Mask_text")
Name_Mask_text = config.get("Mask", "Name_Mask_text")

def to_time(clip_time: float) -> str:
    H = clip_time // 3600
    M = (clip_time - H * 3600)//60
    S = clip_time - H * 3600 - M * 60
    S = int(S * 100) / 100
    _time = '%02d:%02d:%05.2f' %(H,M,S)
    return _time

stream = frame_stream()
start_time_list, narration, video_length = stream.to_frame(video_file_name)
content = script_info + "\n" + garbage + "\n" + styles + "\n" + events
Dial_Mask_event_eg = ass_events(Layer=0, Start = "0:00:00.00", End = "0:00:00.00", Style = "Default", Name = "对话框遮罩示例", Text = Dial_Mask_text)
Name_Mask_event_eg = ass_events(Layer=0, Start = "0:00:00.00", End = "0:00:00.00", Style = "Default", Name = "人名框遮罩示例", Text = Name_Mask_text)
content = content + Name_Mask_event_eg.echo_dialogue() + "\n" + Dial_Mask_event_eg.echo_dialogue() + "\n"


if len(narration):
    for index, _time in enumerate(narration):
        if index == 0:
            start_time = to_time(start_time_list[0] - 0.1)
            end_time = to_time(_time)
        elif index % 2 != 0:
            if index == len(narration) - 1:
                start_time = to_time(_time)
                end_time = to_time(video_length - 1)
            else:
                start_time = to_time(_time)
                end_time = to_time(narration[index + 1])
        else:
            continue
        Dial_Mask_event = ass_events(Layer=0, Start = start_time, End = end_time, Style = "Default", Name = "对话框遮罩", Text = Dial_Mask_text)
        Name_Mask_event = ass_events(Layer=0, Start = start_time, End = end_time, Style = "Default", Name = "人名框遮罩", Text = Name_Mask_text)
        content = content + Name_Mask_event.echo_dialogue() + "\n" + Dial_Mask_event.echo_dialogue() + "\n"
else:
    start_time = to_time(start_time_list[0] - 0.1)
    end_time = to_time(video_length - 1)
    Dial_Mask_event = ass_events(Layer=0, Start = start_time, End = end_time, Style = "Default", Name = "对话框遮罩", Text = Dial_Mask_text)
    Name_Mask_event = ass_events(Layer=0, Start = start_time, End = end_time, Style = "Default", Name = "人名框遮罩", Text = Name_Mask_text)
    content = content + Name_Mask_event.echo_dialogue() + "\n" + Dial_Mask_event.echo_dialogue() + "\n"
    

for index, start_time in enumerate(start_time_list):
    if index == len(start_time_list) - 1:
        start_time = to_time(start_time_list[index])
        end_time = to_time(video_length - 1)
    else:
        
        start_time = to_time(start_time_list[index])
        is_narration = False
        for n_index, _time in enumerate(narration):
            if n_index % 2 == 0:
                narration_start = _time
            else:
                continue
            if start_time_list[index] < narration_start and narration_start < start_time_list[index + 1]:
                end_time = to_time(narration_start - 0.01)
                is_narration = True
        if not is_narration:
            end_time = to_time(start_time_list[index + 1] - 0.01)
    _event = ass_events(Layer = 2, Start = start_time , End = end_time , Style = "手游剧情-单行")
    content = content + f"{_event.echo_dialogue()}" + "\n"
try:
    with open(f"{ASS_PATH}/{ass_file_name}", "w", encoding="utf8") as fp:
        fp.write(content)
    print(f"\n{ass_file_name} successfully generated")
except:
    print(f"\ngenerated failed")

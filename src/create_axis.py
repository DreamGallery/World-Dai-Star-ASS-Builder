import json
import cv2, cv2.typing
from src.read_ini import config
from src.match import *
from src.draw import draw_text
from src.events import AssEvents


_Phrase_Mask_text = config.get("Mask", "Phrase_Mask_text")
_SpeakerName_Mask_text = config.get("Mask", "SpeakerName_Mask_text")
_FONT_PATH = config.get("File PATH", "FONT_PATH")
_fontsize = config.getint("Font Config", "fontsize")
_strokewidth = config.getint("Font Config", "strokewidth")
_kerning = config.getint("Font Config", "kerning")
_threshold = config.getfloat("Option", "threshold")
_Phrase_Area = tuple(json.loads(config.get("Area", "Phrase_Area")))


def echo_Mask_event(image_info_list: list[tuple[str, str]]) -> list[str]:
    period_list: list[tuple[str, str]] = []
    start_time: str = ""
    end_time: str = ""
    for current_next_info in zip(image_info_list[:], image_info_list[1:]):
        info_current, info_next = current_next_info[0], current_next_info[1]
        if not info_current[1] and info_next[1]:
            start_time = info_next[0]
        elif info_current[1] and not info_next[1]:
            end_time = info_next[0]
        if start_time and end_time:
            period_list.append((start_time, end_time))
            start_time, end_time = "", ""

    Mask_event_list: list[str] = []
    for period in period_list:
        Phrase_mask_event = AssEvents(Start=period[0], End=period[1], Style="Default", Text=_Phrase_Mask_text)
        SpeakerName_mask_event = AssEvents(
            Start=period[0], End=period[1], Style="Default", Text=_SpeakerName_Mask_text
        )
        Mask_event_list.append(f"{Phrase_mask_event.echo_dialogue() + Phrase_mask_event.Text}")
        Mask_event_list.append(f"{SpeakerName_mask_event.echo_dialogue() + SpeakerName_mask_event.Text}")

    return Mask_event_list


def echo_SpeakerName_event(image_info_list: list[tuple[str, str]], SpeakerName_list: list[str]) -> list[str]:
    start_time: str = ""
    end_time: str = ""
    SpeakerName_event_list: list[str] = []
    SpeakerName_tag: str = ""
    for info in image_info_list:
        for SpeakerName in SpeakerName_list:
            if SpeakerName == info[1] and SpeakerName != SpeakerName_tag:
                if start_time:
                    end_time = info[0]
                    SpeakerName_event = AssEvents(
                        Layer=1,
                        Start=start_time,
                        End=end_time,
                        Style="WDS_剧情_人名",
                        Name=SpeakerName_tag,
                        Text=SpeakerName_tag,
                    )
                    SpeakerName_event_list.append(
                        f"{SpeakerName_event.echo_dialogue() + SpeakerName_event.Text}"
                    )
                SpeakerName_tag = info[1]
                start_time = info[0]
                break
            if SpeakerName_tag == info[1]:
                break
            elif SpeakerName_tag and SpeakerName_tag != info[1]:
                end_time = info[0]
                SpeakerName_event = AssEvents(
                    Layer=1,
                    Start=start_time,
                    End=end_time,
                    Style="WDS_剧情_人名",
                    Name=SpeakerName_tag,
                    Text=SpeakerName_tag,
                )
                SpeakerName_event_list.append(f"{SpeakerName_event.echo_dialogue() + SpeakerName_event.Text}")
                SpeakerName_tag = info[1]
                if info[1]:
                    start_time = info[0]
                else:
                    start_time = ""
                break

    return SpeakerName_event_list


def echo_Phrase_event(
    image_list: list[cv2.typing.MatLike], image_info_list: list[tuple[str, str]], Episode_json: dict
) -> list[str]:
    Phrase_event_list: list[str] = []
    image_tag: int = int(0)
    total_image_num = len(image_list)

    for index, part in enumerate(Episode_json):
        GroupOrder: int = part["GroupOrder"]
        if index > 1 and GroupOrder == Episode_json[index - 1]["GroupOrder"]:
            continue
        if index < len(Episode_json) - 1:
            if GroupOrder == Episode_json[index + 1]["GroupOrder"]:
                Phrase: str = part["Phrase"] + "/n" + Episode_json[index + 1]["Phrase"]
            else:
                Phrase: str = part["Phrase"]
        SpeakerName: str = part["SpeakerName"]

        start_time: str = ""
        end_time: str = ""
        line1_complete_flag: bool = False
        char = Phrase[0]
        lines: list[str] = []
        for line in Phrase.split("/n"):
            lines.append(line)
        char_img_inv, char_mask = draw_text(char, _FONT_PATH, _fontsize, _strokewidth, _kerning)
        line_img_inv, line_mask = draw_text(lines[0], _FONT_PATH, _fontsize, _strokewidth, _kerning)
        line_img: list[cv2.typing.MatLike] = [cv2.bitwise_not(img_inv) for img_inv in line_img_inv]
        char_img: list[cv2.typing.MatLike] = [cv2.bitwise_not(img_inv) for img_inv in char_img_inv]

        for _index, image in enumerate(image_list[image_tag:]):
            percent = round((_index + image_tag) / total_image_num * 100)
            print(
                f"\rMatch-Process:({_index + image_tag}/{total_image_num})" + "{}%: ".format(percent),
                "▮" * (percent // 2),
                end="",
            )
            if not image_info_list[_index + image_tag][1]:
                continue
            if not start_time and compare(
                get_area(image, _Phrase_Area), char_img, _threshold, mask=char_mask
            ):
                start_time = image_info_list[_index + image_tag][0]
                continue
            if start_time:
                if not line1_complete_flag and compare(
                    get_area(image, _Phrase_Area), line_img, _threshold, mask=line_mask
                ):
                    line1_complete_flag = True
                elif line1_complete_flag and not compare(
                    get_area(image, _Phrase_Area), line_img, _threshold, mask=line_mask
                ):
                    end_time = image_info_list[_index + image_tag][0]
                    Phrase_event = AssEvents(
                        Layer=1,
                        Start=start_time,
                        End=end_time,
                        Style="WDS_剧情_台词",
                        Name=SpeakerName,
                        Text=Phrase,
                    )
                    Phrase_event_list.append(Phrase_event.echo_dialogue())
                    if len(lines) > 1:
                        line2 = Phrase_event.echo_dialogue() + "{\pos(240,931)}"
                        Phrase_event_list.append(line2)
                    Phrase_event_list.append(Phrase_event.echo_comment())
                    image_tag = _index + image_tag
                    break

    return Phrase_event_list

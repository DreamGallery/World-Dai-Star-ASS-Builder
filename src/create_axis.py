import sys
import json
import cv2, cv2.typing
from src.read_ini import config
from src.match import *
from src.draw import draw_text
from src.speaker import get_translate
from src.events import AssEvents


_FONT_PATH = config.get("File Path", "FONT_PATH")
_phrase_mask = config.get("Mask", "phrase_mask")
_speaker_name_mask = config.get("Mask", "speaker_name_mask")
_font_size = config.getint("Font Config", "font_size")
_stroke_width = config.getint("Font Config", "stroke_width")
_kerning = config.getint("Font Config", "kerning")
_threshold = config.getfloat("Option", "threshold")
_char_area_1 = tuple(json.loads(config.get("Area", "char_area_1")))
_char_area_2 = tuple(json.loads(config.get("Area", "char_area_2")))
_phrase_area_1 = tuple(json.loads(config.get("Area", "phrase_area_1")))
_phrase_area_2 = tuple(json.loads(config.get("Area", "phrase_area_2")))


def _format_time(time: str) -> str:
    _time = float(time[:-1])
    H = _time // 3600
    M = (_time - H * 3600) // 60
    S = _time - H * 3600 - M * 60
    ass_time = "%d:%02d:%05.2f" % (H, M, S)
    return ass_time


def echo_mask_event(image_info_list: list[tuple[str, str]]) -> list[str]:
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

    mask_event_list: list[str] = []
    for period in period_list:
        phrase_mask_event = AssEvents(
            Start=_format_time(period[0]),
            End=_format_time(period[1]),
            Style="Default",
            Text=_phrase_mask,
        )
        speaker_name_mask_event = AssEvents(
            Start=_format_time(period[0]),
            End=_format_time(period[1]),
            Style="Default",
            Text=_speaker_name_mask,
        )
        mask_event_list.append(f"{phrase_mask_event.echo_dialogue() + phrase_mask_event.Text}")
        mask_event_list.append(f"{speaker_name_mask_event.echo_dialogue() + speaker_name_mask_event.Text}")

    return mask_event_list


def echo_speaker_name_event(
    image_info_list: list[tuple[str, str]], speaker_name_list: list[str]
) -> list[str]:
    start_time: str = ""
    end_time: str = ""
    speaker_name_event_list: list[str] = []
    speaker_name_tag: str = ""
    for info in image_info_list:
        for speaker_name in speaker_name_list:
            if speaker_name == info[1] and speaker_name != speaker_name_tag:
                if start_time:
                    end_time = info[0]
                    speaker_name_event = AssEvents(
                        Layer=1,
                        Start=_format_time(start_time),
                        End=_format_time(end_time),
                        Style="WDS_剧情_人名",
                        Name=speaker_name_tag,
                        Text=get_translate(speaker_name_tag),
                    )
                    speaker_name_event_list.append(
                        f"{speaker_name_event.echo_dialogue() + speaker_name_event.Text}"
                    )
                speaker_name_tag = info[1]
                start_time = info[0]
                break
            if speaker_name_tag == info[1]:
                break
            elif speaker_name_tag and speaker_name_tag != info[1]:
                end_time = info[0]
                speaker_name_event = AssEvents(
                    Layer=1,
                    Start=_format_time(start_time),
                    End=_format_time(end_time),
                    Style="WDS_剧情_人名",
                    Name=speaker_name_tag,
                    Text=get_translate(speaker_name_tag),
                )
                speaker_name_event_list.append(
                    f"{speaker_name_event.echo_dialogue() + speaker_name_event.Text}"
                )
                speaker_name_tag = info[1]
                if info[1]:
                    start_time = info[0]
                else:
                    start_time = ""
                break

    return speaker_name_event_list


def echo_phrase_event(
    image_list: list[cv2.typing.MatLike], image_info_list: list[tuple[str, str]], episode_json: dict
) -> list[str]:
    phrase_event_list: list[str] = []
    image_line1_tag: int = 0
    image_line2_tag: int = 0

    for json_index, part in enumerate(episode_json):
        group_order: int = part["GroupOrder"]
        if json_index >= 1 and group_order == episode_json[json_index - 1]["GroupOrder"]:
            continue
        if json_index < len(episode_json) - 1:
            if group_order == episode_json[json_index + 1]["GroupOrder"]:
                phrase: str = part["Phrase"] + "/n" + episode_json[json_index + 1]["Phrase"]
            else:
                phrase: str = part["Phrase"]
        elif json_index == len(episode_json) - 1:
            phrase: str = part["Phrase"]
        speaker_name: str = part["SpeakerName"]

        start_time: str = ""
        end_time: str = ""
        appear_flag: bool = False
        lines = phrase.split("/n")
        for line_num, line in enumerate(lines, start=1):
            char = line.lstrip()[0]
            char_img_inv, char_mask = draw_text(char, _FONT_PATH, _font_size, _stroke_width, _kerning)
            line_img_inv, line_mask = draw_text(line, _FONT_PATH, _font_size, _stroke_width, _kerning)
            line_img: list[cv2.typing.MatLike] = [cv2.bitwise_not(img_inv) for img_inv in line_img_inv]
            char_img: list[cv2.typing.MatLike] = [cv2.bitwise_not(img_inv) for img_inv in char_img_inv]
            if line_num == 1:
                for image_index_1, image in enumerate(image_list[image_line1_tag:]):
                    percent = round((json_index + 1) / len(episode_json) * 100)
                    print(
                        f"\rMatch-Process:[{image_index_1 + image_line1_tag + 1}/{len(image_list)}] ({json_index + 1}/{len(episode_json)})"
                        + "{}%: ".format(percent),
                        "▮" * (percent // 2),
                        end="",
                    )
                    if image_index_1 + image_line1_tag == len(image_list) - 1:
                        if json_index == len(episode_json) - 1 and not start_time:
                            print(
                                f"{line} still can't find the start or end time after traversing all the video."
                            )
                            print(
                                "Please adjust the parameters and try again or contact me to provide details."
                            )
                            sys.exit(1)
                    if not image_info_list[image_index_1 + image_line1_tag][1]:
                        if start_time:
                            end_time = image_info_list[image_index_1 + image_line1_tag][0]
                            phrase1_event = AssEvents(
                                Layer=1,
                                Start=_format_time(start_time),
                                End=_format_time(end_time),
                                Style="WDS_剧情_台词",
                                Name=speaker_name,
                                Text=phrase,
                            )
                            print(f"\n{phrase1_event.Start} {phrase1_event.End} {phrase1_event.Name} {lines}")
                            phrase_event_list.append(phrase1_event.echo_dialogue())
                            if len(lines) == 1:
                                phrase_event_list.append(phrase1_event.echo_comment())
                            image_line1_tag = image_index_1 + image_line1_tag
                            break
                        continue
                    if not start_time and compare(
                        get_area(image, _char_area_1), char_img, _threshold, mask=char_mask
                    ):
                        start_time = image_info_list[image_index_1 + image_line1_tag][0]
                        continue
                    if start_time:
                        if not appear_flag and compare(
                            get_area(image, _phrase_area_1), line_img, _threshold, mask=line_mask
                        ):
                            appear_flag = True
                            image_line2_tag = image_index_1 + image_line1_tag
                        elif appear_flag and not compare(
                            get_area(image, _phrase_area_1), line_img, _threshold, mask=line_mask
                        ):
                            end_time = image_info_list[image_index_1 + image_line1_tag][0]
                            phrase1_event = AssEvents(
                                Layer=1,
                                Start=_format_time(start_time),
                                End=_format_time(end_time),
                                Style="WDS_剧情_台词",
                                Name=speaker_name,
                                Text=line,
                            )
                            print(f"\n{phrase1_event.Start} {phrase1_event.End} {phrase1_event.Name} {line}")
                            phrase_event_list.append(phrase1_event.echo_dialogue())
                            if len(lines) == 1:
                                phrase_event_list.append(phrase1_event.echo_comment())
                            image_line1_tag = image_index_1 + image_line1_tag
                            break
            elif line_num == 2:
                line2_start_time: str = ""
                for image_index_2, image in enumerate(image_list[image_line2_tag:]):
                    percent = round((json_index + 1) / len(episode_json) * 100)
                    print(
                        f"\rMatch-Process:[{image_index_2 + image_line2_tag + 1}/{len(image_list)}] ({json_index + 1}/{len(episode_json)})"
                        + "{}%: ".format(percent),
                        "▮" * (percent // 2),
                        end="",
                    )
                    if not line2_start_time and compare(
                        get_area(image, _char_area_2), char_img, _threshold, mask=char_mask
                    ):
                        line2_start_time = image_info_list[image_index_2 + image_line2_tag][0]
                        continue
                    if line2_start_time:
                        if compare(get_area(image, _phrase_area_2), line_img, _threshold, mask=line_mask):
                            phrase2_event = AssEvents(
                                Layer=1,
                                Start=_format_time(line2_start_time),
                                End=_format_time(end_time),
                                Style="WDS_剧情_台词",
                                Name=speaker_name,
                                Text=line,
                            )
                            print(f"\n{phrase2_event.Start} {phrase2_event.End} {phrase2_event.Name} {line}")
                            phrase_event_list.append(phrase2_event.echo_dialogue() + "{\\pos(240,931)}")
                            phrase2_event.Start = _format_time(start_time)
                            phrase2_event.Text = lines[0] + lines[1]
                            phrase_event_list.append(phrase2_event.echo_comment())
                            break
                    if image_index_2 + image_line2_tag == len(image_list) - 1:
                        print(
                            f"{line} still can't find the start or end time after traversing all the video."
                        )
                        print("Please adjust the parameters and try again or contact me to provide details.")
                        sys.exit(1)

    return phrase_event_list

import sys
import json
import threading
import cv2, cv2.typing
from src.match import *
from src.read_ini import config
from src.draw import to_binary_adaptive, draw_text
from concurrent.futures import ThreadPoolExecutor, wait


_VIDEO_PATH = config.get("File PATH", "VIDEO_PATH")
_FONT_PATH = config.get("File PATH", "FONT_PATH")
_fontsize = config.getint("Font Config", "fontsize")
_strokewidth = config.getint("Font Config", "strokewidth")
_kerning = config.getint("Font Config", "kerning")
_threshold = config.getfloat("Option", "threshold")
_SpeakerName_Area = tuple(json.loads(config.get("Area", "SpeakerName_Area")))


_lock = threading.Lock()
_current_count = int(0)


class FrameProcess(object):
    def one_task(
        self,
        image_with_info_list: list[tuple[cv2.typing.MatLike, str, str]],
        frame: cv2.typing.MatLike,
        height: int,
        milliseconds: float,
        total_fps: int,
        SpeakerName_img_list: list[tuple[list[cv2.typing.MatLike], list[cv2.typing.MatLike], str]],
    ) -> None:
        global _current_count
        seconds = "%.4f" % (milliseconds // 1000 + (milliseconds % 1000) / 1000)
        ass_time = seconds[:-1]
        img: cv2.typing.MatLike = frame[(height * 2 // 3) :, :]
        binary_frame = to_binary_adaptive(img, 11, 0)
        SpeakerName_str: str = ""
        for SpeakerName_img in SpeakerName_img_list:
            if compare(
                get_area(binary_frame, _SpeakerName_Area),
                SpeakerName_img[0],
                _threshold,
                mask=SpeakerName_img[1],
            ):
                SpeakerName_str = SpeakerName_img[2]
                break
        _lock.acquire()
        image_with_info_list.append((binary_frame, ass_time, SpeakerName_str))
        _current_count += 1
        percent = round(_current_count / total_fps * 100)
        print(
            f"\rPre-Progress:({_current_count}/{total_fps})" + "{}%: ".format(percent),
            "▮" * (percent // 2),
            end="",
        )
        sys.stdout.flush()
        _lock.release()

    def to_frame(
        self, input: str, SpeakerName_list: list[str]
    ) -> tuple[list[cv2.typing.MatLike], list[tuple[str, str]]]:
        image_with_info_list: list[tuple[cv2.typing.MatLike, str, str]] = []
        video_path = f"{_VIDEO_PATH}/{input}"
        vc = cv2.VideoCapture(video_path)
        total_fps = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_tasks = []
        executor = ThreadPoolExecutor(max_workers=20)
        SpeakerName_img_list: list[tuple[list[cv2.typing.MatLike], list[cv2.typing.MatLike], str]] = []
        for SpeakerName in SpeakerName_list:
            image, mask = draw_text(SpeakerName, _FONT_PATH, _fontsize, _strokewidth, _kerning)
            SpeakerName_img_list.append((image, mask, SpeakerName))

        while vc.isOpened():
            status, frame = vc.read()
            if not status:
                break
            milliseconds = vc.get(cv2.CAP_PROP_POS_MSEC)
            frame_tasks.append(
                executor.submit(
                    self.one_task,
                    image_with_info_list,
                    frame,
                    height,
                    milliseconds,
                    total_fps,
                    SpeakerName_img_list,
                )
            )
        vc.release()
        wait(frame_tasks, return_when="ALL_COMPLETED")
        print("\nVideo Pre-Progress finished")

        image_with_info_list.sort(key=lambda x: float(x[1]))
        image_list: list[cv2.typing.MatLike] = []
        info_list: list[tuple[str, str]] = []
        for image_and_info in image_with_info_list:
            image_list.append(image_and_info[0])
            info_list.append((image_and_info[1], image_and_info[2]))

        return (image_list, info_list)

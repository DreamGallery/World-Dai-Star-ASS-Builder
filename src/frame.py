import cv2, cv2.typing
import sys
import threading
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
from src.read_ini import config
from concurrent.futures import ThreadPoolExecutor


_ass_file_name = config.get("Info", "ass_file_name")
_Dial_box_name = config.get("Info", "Dial_box_name")
_Degree_Threshold = config.getfloat("Option", "Degree_Threshold")
_Narration_Threshold = config.getfloat("Option", "Narration_Threshold")
_VIDEO_PATH = config.get("File PATH", "VIDEO_PATH")
_CACHE_PATH = config.get("File PATH", "CACHE_PATH")
_ASSET_PATH = config.get("File PATH", "ASSET_PATH")
_fig_name = _ass_file_name.replace(".ass", ".png")


_lock = threading.Lock()
_current_count = int(0)


def to_binary(img: cv2.typing.MatLike) -> cv2.typing.MatLike:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 159, 255, cv2.THRESH_BINARY)
    return binary


def compare(img: cv2.typing.MatLike, binary: cv2.typing.MatLike) -> float:
    res = cv2.matchTemplate(img, binary, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_val


class FrameProcess(object):
    def one_task(
        self,
        frame: cv2.typing.MatLike,
        frame_time_milli: float,
        dial_box: cv2.typing.MatLike,
        total_fps: int,
        axis_data: list[tuple[float, float]],
    ) -> None:
        global _current_count
        height = len(frame)
        img: cv2.typing.MatLike = frame[(height * 2 // 3) :, :]
        binary_frame = to_binary(img)
        matching_degree = compare(dial_box, binary_frame)
        frame_time = int((frame_time_milli // 1000 + (frame_time_milli % 1000) / 1000) * 1000) / 1000
        _lock.acquire()
        axis_data.append((frame_time, matching_degree))
        _current_count += 1
        percent = round(_current_count / total_fps * 100)
        print(
            f"\rPre-Progress:({_current_count}/{total_fps})" + "{}%: ".format(percent),
            "▓" * (percent // 2),
            end="",
        )
        sys.stdout.flush()
        _lock.release()

    def list_less(self, value: float, _continue: int, _list: list) -> list[tuple[int, int]]:
        count = int(0)
        temp = _continue
        Tuple_list: list[tuple[int, int]] = []
        for index, _value in enumerate(_list):
            if _value < value:
                count += 1
                if count > temp:
                    temp += 1
            else:
                if count > _continue:
                    Tuple_list.append((index - temp + 1, index - 1))
                count = 0
        return Tuple_list

    def to_frame(self, input: str) -> tuple[list[float], list[float], float]:
        video_path = f"{_VIDEO_PATH}/{input}"
        vc = cv2.VideoCapture(video_path)
        fps = vc.get(cv2.CAP_PROP_FPS)
        total_fps = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        axis_data: list[tuple[float, float]] = []
        x_axis_data: list[float] = []  # x
        y_axis_data: list[float] = []  # y
        dial_start: list[float] = []  # time for every dialogue start
        narration: list[float] = []
        narration_index: list[tuple[int, int]] = []
        dia_box = to_binary(cv2.imread(f"{_ASSET_PATH}/{_Dial_box_name}"))
        executor = ThreadPoolExecutor(max_workers=20)
        while vc.isOpened():
            status, frame = vc.read()
            if not status:
                break
            milliseconds = vc.get(cv2.CAP_PROP_POS_MSEC)
            executor.submit(self.one_task, frame, milliseconds, dia_box, total_fps, axis_data)
        vc.release()
        video_length = _current_count / fps
        axis_data.sort(key=lambda x: x[0])
        for Tuple in axis_data:
            x_axis_data.append(Tuple[0])
            y_axis_data.append(Tuple[1])
        narration_index = self.list_less(_Narration_Threshold, int(fps), y_axis_data)
        peaks_start, _ = scipy.signal.find_peaks(
            y_axis_data, height=_Degree_Threshold, distance=int(1.5 * fps)
        )
        plt.figure(dpi=200, figsize=(32, 8))
        plt.xlabel("time")
        plt.ylabel("matching degree")
        plt.xlim((0, (total_fps + fps) // fps))
        plt.ylim((0, 1))
        plt.xticks(np.arange(0, (total_fps + fps) // fps, 10))
        plt.yticks(np.arange(0, 1, 0.02))
        plt.plot(x_axis_data, y_axis_data, alpha=0.5, linewidth=1)
        plt.plot(np.array(x_axis_data)[peaks_start], np.array(y_axis_data)[peaks_start], "o")
        for x, y in zip(np.array(x_axis_data)[peaks_start], np.array(y_axis_data)[peaks_start]):
            x_3f: str = "%.3f" % x
            y_4f: str = "%.4f" % y
            dial_start.append(float(x_3f))
            plt.text(x, y, f"({x_3f},{y_4f})", ha="center", fontsize=8)
        plt.savefig(f"{_CACHE_PATH}/{_fig_name}")
        for Tuple in narration_index:
            narration.append(float("%.3f" % x_axis_data[Tuple[0]]))
            narration.append(float("%.3f" % x_axis_data[Tuple[1]]))
        return (dial_start, narration, video_length)

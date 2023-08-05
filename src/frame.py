import os
import cv2
import sys
import threading
import configparser
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
from concurrent.futures import ThreadPoolExecutor


BASE_PATH = os.path.abspath(os.path.dirname(__file__)+os.path.sep+"..")
config = configparser.ConfigParser()
config.read(os.path.join(BASE_PATH ,'config.ini'), encoding="utf-8")
ass_file_name = config.get("Info", "ass_file_name")
Dial_box_name = config.get("Info", "Dial_box_name")
VIDEO_PATH = config.get("File PATH", "VIDEO_PATH")
CACHE_PATH = config.get("File PATH", "CACHE_PATH")
ASSET_PATH = config.get("File PATH", "ASSET_PATH")
fig_name = ass_file_name.replace(".ass", ".png")


lock = threading.Lock()
_current_count = 0


def to_binary(img: any) ->any:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,binary = cv2.threshold(gray, 159, 255, cv2.THRESH_BINARY)
    return binary


def compare(img: any, binary: any):
    res = cv2.matchTemplate(img, binary, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_val


class frame_stream(object):    
    
    def one_task(self, frame: any, frame_time_milli: float, dia_box: any, total_fps: int, axis_data: list[tuple[float, float]]):
        global _current_count
        height = len(frame)
        height = len(frame)
        width = len(frame[0])
        img = frame[(height*2//3):height, 0:width]
        binary_frame = to_binary(img)
        matching_degree = compare(dia_box, binary_frame)
        frame_time = int((frame_time_milli // 1000 + (frame_time_milli % 1000) / 1000) * 1000) / 1000
        lock.acquire()
        axis_data.append((frame_time, matching_degree))
        _current_count += 1
        percent = round(_current_count / total_fps * 100)
        print(f"\rPre-Progress:({_current_count}/{total_fps})"+"{}%: ".format(percent), "▓" * (percent // 2), end="")
        sys.stdout.flush()
        lock.release()
    
    
    def to_frame(self, input: str) -> list[float]:
        video_path = f"{VIDEO_PATH}/{input}"
        vc = cv2.VideoCapture(video_path)
        fps = vc.get(cv2.CAP_PROP_FPS)
        total_fps = vc.get(cv2.CAP_PROP_FRAME_COUNT)    
        axis_data = []
        x_axis_data = [] #x
        y_axis_data = [] #y
        dial_start = [] #time for every dialogue start
        dia_box = to_binary(cv2.imread(f"{ASSET_PATH}/{Dial_box_name}"))
        executor = ThreadPoolExecutor(max_workers=20)
        while vc.isOpened():
            status, frame = vc.read()
            if not status:
                break
            milliseconds = vc.get(cv2.CAP_PROP_POS_MSEC) 
            executor.submit(self.one_task, frame, milliseconds, dia_box, total_fps, axis_data)
        vc.release()
        axis_data.sort(key=lambda x:x[0])
        for tuple in axis_data:
            x_axis_data.append(tuple[0])
            y_axis_data.append(tuple[1])
        peaks_start, _ = scipy.signal.find_peaks(y_axis_data, height=0.9, distance=int(1.5 * fps))
        plt.figure(dpi=200, figsize=(32,8))
        plt.xlabel('time')
        plt.ylabel('matching degree')
        plt.xlim((0, (total_fps + fps) // fps))
        plt.ylim((0, 1))
        plt.xticks(np.arange(0, (total_fps + fps) // fps, 10))
        plt.yticks(np.arange(0, 1, 0.02))
        plt.plot(x_axis_data, y_axis_data, alpha=0.5, linewidth=1)
        plt.plot(np.array(x_axis_data)[peaks_start], np.array(y_axis_data)[peaks_start], "o")
        for x, y in zip(np.array(x_axis_data)[peaks_start], np.array(y_axis_data)[peaks_start]):
            x_3f = '%.3f' %x
            y_4f = '%.4f' %y
            dial_start.append(float(x_3f))
            plt.text(x, y, f"({x_3f},{y_4f})", ha='center', fontsize=8)
        plt.savefig(f"{CACHE_PATH}/{fig_name}")
        return dial_start
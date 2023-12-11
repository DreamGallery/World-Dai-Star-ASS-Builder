import numpy as np
import cv2, cv2.typing


def get_area(binary_image: cv2.typing.MatLike, clip: tuple[int, int, int, int]) -> cv2.typing.MatLike:
    cut_area = binary_image[clip[0] : clip[1], clip[2] : clip[3]]
    return cut_area


def compare(
    frame_img: cv2.typing.MatLike,
    binary: list[cv2.typing.MatLike],
    threshold: float,
    mask: list[cv2.typing.MatLike],
) -> bool:
    white_pixels = cv2.countNonZero(frame_img)
    if white_pixels < 10:
        return False
    part_max: list[float] = []
    for image in zip(binary, mask):
        res = cv2.matchTemplate(frame_img, image[0], cv2.TM_CCORR_NORMED, mask=image[1])
        res[np.isinf(res)] = 0
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        part_max.append(max_val)
    max_avg = sum(part_max) / len(part_max)
    if max_avg > threshold:
        return True
    else:
        return False

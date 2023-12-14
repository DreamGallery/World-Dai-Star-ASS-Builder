_check_list = {
    "ここな": "心菜",
    "静香": "静香",
    "カトリナ": "卡特莉娜",
    "八恵": "八恵",
    "ぱんだ": "潘达",
    "知冴": "知冴",
    "望有": "望有",
    "暦": "历",
    "ラモーナ": "拉莫娜",
    "王雪": "王雪",
    "リリヤ": "莉莉亚",
    "緋花里": "绯花里",
    "いろは": "伊吕波",
    "美兎": "美兔",
    "カミラ": "卡米拉",
    "蕾": "蕾",
    "叶羽": "叶羽",
    "初魅": "初魅",
    "大黒": "大黑",
    "仁花子": "仁花子",
    "容": "容",
    "しぐれ": "时雨",
}


def get_translate(speaker_name: str) -> str:
    if _check_list.__contains__(speaker_name):
        translated_name = _check_list[speaker_name]
        return translated_name
    else:
        return speaker_name

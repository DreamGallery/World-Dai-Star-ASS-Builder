import os
import configparser

_BASE_PATH = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
config = configparser.ConfigParser()
try:
    config.read(os.path.join(_BASE_PATH, "config.ini"), encoding="utf-8")
except Exception:
    config.read(os.path.join(_BASE_PATH, "config.ini"), encoding="utf-8-sig")

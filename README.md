# WORLD DAI STAR ASS BUILDER
This is a tool to generate a rough subtile file for World Dai Star dialogue plot (you need to check yourself after finished)

Using `OPENCV2` to create an analysis chart like this
![image](cache/电姬主线第一章第五话.png)
As you can see，the point of mutation is where a word begins

So, you can also change the image of dialogue box(in `asset` folder) to make this tool universal to other games 


# Usage

install requirement
```
pip3 install -r requirements.txt
```

Edit `[Info]` in `config.ini` first, put video file in `video/`, and run with
```
python main.py
```
The `.ass` file will saved in `ass/` and you can find the image of analysis chart in `cache/` with the name you set for subtitle




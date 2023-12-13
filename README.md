# WORLD DAI STAR ASS BUILDER (V2)

Using `OPENCV2` to match video image and auto create subtitle timeline for `Aegisub`

## Usage

### Get from the repository
```
git clone https://github.com/DreamGallery/World-Dai-Star-ASS-Builder.git
cd World-Dai-Star-ASS-Builder
```

### Install requirement

```
pip install -r requirements.txt
```

Before running, edit the section `[Info]` and section `[Download Data]` in `config.ini`.<br />
The preset in `config.ini` is for `[1920x1080]`, so if your recorded video is at this resolution, just put your video into the `video` folder.<br />
※ If your want to change some options, more information for you in the `config.ini` 

### Download Episode files
```
python story_unpack.py
``` 
This is just a simple script to get the necessary data for the tool to run. <br />
If you want to get more detailed data, you can find solutions in these repository: <br />
[WDS-Adv-Resource](https://github.com/nan0521/WDS-Adv-Resource)&emsp;[sirius-toolbox](https://github.com/SonolusHaniwa/sirius-toolbox)

### Start matching
Now you have completed all the preparation, just run with
```
python main.py
```
and wait for the process to finish and you will find the `.ass` file in `ass` folder

### ※ For speaker name translate
A Chinese translation checklist is preset in `src/speaker.py`, if you want to add more correspondence, you can do it like this
```
···
"しぐれ": "时雨",
"Speaker name": "Translated name",
``` 

## Some notes on upgrading from V1 to V2
In the `V1 version`, the tool is just match with the empty dialog box, by analyzing the changes in match rates, draw a line graph.<br />
The abrupt points in the graph are where the dialogue begins and ends, this can only generate a rough timeline.

After upgrading to `V2 version`, the tool starts matching names and dialogue text directly.<br />
By using `Pillow` to draw text image, and match with `OPENCV Template match` method, this improved the accuracy of timeline.<br />
You don't need to add timeline of names manually anymore, there will also be comments of original Japanese text here that you can compare to translate or just fill in the translated text.<br />
The only thing that you may need to pay attention to is the fade in and fade out effect, adjust it according to your mood.  

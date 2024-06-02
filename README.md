# Deepwoken Helper

<div align="center">
  <img src="https://github.com/Tuxsupa/DeepwokenHelper/assets/69093264/9039ed81-6bea-4725-a169-d0d2d799c248" alt="main window">
  <p>
    Deepwoken Helper to help you choose your cards.
  </p>
  <a href="https://github.com/Tuxsupa/DeepwokenHelper/releases"><img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/Tuxsupa/DeepwokenHelper/total?label=Downloads&color=green"></a>
</div>

# How does this work?
Wait for the program to finish loading the AI model in the background.\
Afterwards load a new build from the [builder](https://deepwoken.co/) with the add button.\
Then after it's finished press the hotkey (default `J`) while having the cards on screen in Deepwoken.\
This will show all the data of the cards so it can help you pick which card you need for your build.\
\
\
It might be prone to not being able to detect certain cards.

## Showcase
https://github.com/Tuxsupa/DeepwokenHelper/assets/69093264/2ebfd1d8-cad2-4076-93e4-4674fcdaee81

# Potential Enhancements
- Overlay showing the card info on the cards themselfs ingame.
- Add/Remove cards manually in case of wrong detections.
- Turn on and off the AI model so it's not always loaded in the background.
- Testing and working macOS version.
- Order of which stats to get first to get an optimized build.
- Recommendation on which card to get next.
- Better UI.
- More settings.
- More testing.
- Devs of the game hopefully adding useful logs when acquiring cards so OCR isn't needed.

# Build (Windows)
It's recommended to use `.venv` and then installing the `requirements.txt` on it.\
Then you need to clone [Ultralytics Yolov5](https://github.com/ultralytics/yolov5) repository onto the home directory of this repository.\
Finally you need to install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and paste the folder to the home directory of this repository. Don't forget to rename the folder to `tesseract` after pasting it.
\
\
To build the application, I use PyInstaller.\
Then, use this command on the repo's home directory for onedir output (You can use onefile but it's more susceptible to getting a false positive from a AV).
```
python -m PyInstaller --noconfirm --onedir --noconsole --icon "./assets/icons/favicon.ico" --name "Deepwoken Helper" --collect-data=ultralytics   "./src/gui.py"
```
Finally copy `assets`, `tesseract` and `yolov5` folder into the output folder that has the new .exe.

# Support
If you really like this project, please consider making a small donation, it really helps and means a lot!
\
\
<a href='https://ko-fi.com/tuxsuper' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />

# Special Thanks

- cyfiee, who created the deepwoken builder! Go [support](https://deepwoken.co/support) his/hers website!
- crea, for emotional support!

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
- Testing and working macOS version.
- Order of which stats to get first to get an optimized build.
- Recommendation on which card to get next.
- Better UI.
- More settings.
- More testing.
- Devs of the game hopefully adding useful logs when acquiring cards so AI/OCR isn't needed.

# Build (Windows)
Install [uv](https://docs.astral.sh/uv/getting-started/installation/), use `uv python install 3.13`, `uv venv --python 3.13` and `uv sync` on the repository folder.\
Finally you need to install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and paste the folder to the home directory of this repository. Don't forget to rename the folder to `tesseract` after pasting it.

To build the application, I use [PyInstaller](https://pyinstaller.org/en/stable/installation.html).\
Then, use this command on the repo's home directory for onedir output (You can use onefile but it's more susceptible to getting a false positive from a AV).
```
python -m PyInstaller --noconfirm --onedir --noconsole --icon "./assets/icons/favicon.ico" --name "Deepwoken Helper"   "./deepwokenhelper/__main__.py"
```
Finally copy `assets` and `tesseract` folder into the output folder that has the new .exe.

# Support
If you really like this project, please consider making a small donation, it really helps and means a lot!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/tuxsuper)

# Special Thanks

- cyfiee, who created the deepwoken builder! Go [support](https://deepwoken.co/support) her website!
- crea, for emotional support!

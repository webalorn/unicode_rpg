# ⚔️ Unicode RPG 🏰

This project is currently in development. The final objective is to make a RPG that works only using unicode characters, with an interesting story and world, and that can run into a terminal emulator. Currently, there are the first elements and a functional GUI system. It uses python3.

## Installation

Currently, the only way to start the project is to clone the repository and execute the code from source. Please make sure you have python3 installed, and then, just use :

```bash
git clone https://github.com/webalorn/unicode_rpg
```

To have the audio working, you will need the simpleaudio python package, that can be installed with pip. If you don't have pip installed, [take a look at here](https://pip.pypa.io/en/stable/installing/). Then juste type:

```bash
python3 -m pip install --upgrade simpleaudio
```

On linux, you will need some dependencies to be installed. More informations [here](https://simpleaudio.readthedocs.io/en/latest/installation.html#installation-ref). But to make it short, under ubuntu / debian, uses:

```bash
https://simpleaudio.readthedocs.io/en/latest/installation.html#installation-ref
```

## Usage

Just start the `main.py` scrip located in the `rpg` folder with python3 in a command line environment:

```bash
python3 rpg/main.py
```

Because of the various support for unicode characters and emojis in a terminal, you can choose between different 'skins'. The `default` skin is full skin with all the characters used. The `unicode_compatible` skin makes some changes to be compatibles with terminals that lacks support for some unicode characters. The `ascii` skin only uses ascii characters, and should works everywhere, but is uglier.

```bash
python3 rpg/main.py -s unicode_compatible
python3 rpg/main.py -s ascii
```

You can have better performances using `pypy3` instead of python. Increasing the font size can also improve performance as it reduce the number of characters that needs to be updated each frame.

## Compatiblity list

- MacOS :
	- iTerm2 : Full compatibility
	- Default MacOS terminal : Very bad compatibility, only works with the `ascii` skin
- Linux:
	- gnome-terminal : Works well with the skin `unicode_compatible`
- Windows : unknown

## Authors

- Théophane Vallaeys - [webalorn](https://github.com/webalorn)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
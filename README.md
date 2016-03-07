# Summary
Python2-based bulk downloader that will download the game manifest. 

# Requisites
Works with `Python 2.7`.

# Usage
Run `main.py`, it will download the manifest.json file, and create a `data` folder to download all files from the game.

# Roadmap
- Multiprocessing to download faster.
- Use colorama for user-friendliness.
- Unpack *.ixb files (they are just zip files), and dump contained data.
- Decompile *.luac files in *.ixb packages.
- Investigate where root *.luac files come from.
- Investigate where some root *.rml files come from.

# Screenshots
![enter image description here](https://raw.githubusercontent.com/GameOfWarVault/DataDownloader/master/doc/items_01.png)
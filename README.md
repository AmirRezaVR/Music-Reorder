# Music Shuffler

A simple Python application for organizing music files so that songs from the same artist are not played one after another whenever possible.

I made this project for a simple problem: some car audio systems don't have a shuffle option. If the songs on a flash drive are sorted by artist, songs from the same artist will usually play one after another.

Music Shuffler rearranges the songs and adds a number to the beginning of each filename, so the car plays them in a more shuffled order.

## Features

* Select a music folder manually or use drag and drop
* Supports English and Persian
* Reads the artist name from the music file metadata
* Rearranges songs to avoid consecutive songs from the same artist
* Adds numbers such as `001`, `002`, `003` to the filenames
* Creates a new output folder
* Keeps the original music files unchanged

## Supported Formats

* MP3
* FLAC
* M4A
* AAC
* OGG
* WAV
* WMA

## Requirements

* Python 3
* `mutagen`
* `tkinterdnd2`

Install the required packages with:

```bash
pip install -r requirements.txt
```

## How to Use

Run the program:

```bash
python music_shuffler.py
```

Then:

1. Select your music folder, or drag and drop it into the program.
2. Choose your language.
3. Click **Shuffle and Copy Music**.
4. The program creates a new folder next to the original folder.

For example:

```text
My Music/
My Music_Shuffled/
```

The original files are not modified.

The new folder will contain files such as:

```text
001 - Song Name.mp3
002 - Another Song.mp3
003 - My Favorite Song.mp3
```

## How It Works

The program reads the `Artist` information from each music file and groups the songs by artist.

It then creates a new order that tries to keep songs from the same artist apart as much as possible.

If there are too many songs from one artist compared to the others, it may not be possible to completely avoid consecutive songs from that artist. In that case, the program simply tries to keep them apart as much as possible.

## Version

Current version: **v1.0**

## License

This project is licensed under the MIT License.

# Music Reorder

A small Python app that reorders your music files so songs by the same artist don't play back to back.

Made for car stereos that have no shuffle. It copies your songs into a new folder and puts a number in front of each filename (`001 - Song.mp3`, `002 - Song.mp3`, ...), so the car plays them in the new order.

## Features

- Pick a folder or drag and drop it
- English and Persian interface
- Reads the artist from file metadata
- Spreads out songs by the same artist as much as it can
- Your original files are never changed
- Output goes to a new folder next to the original (`Music/` → `Music_Shuffled/`)

Formats: MP3, FLAC, M4A, AAC, OGG, WAV, WMA

## Setup

You need Python 3, `mutagen` and `tkinterdnd2`:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python music_shuffler.py
```

1. Choose your music folder.
2. Choose the language.
3. Click **Reorder and Copy Music**.

## Good to know

- Every run starts from scratch. Old numbers are removed, all songs (including new ones) are reordered, and the old output folder is replaced.
- The order is different each time.
- If one artist has way more songs than the rest, some of their songs may still end up next to each other.
- Songs with no artist tag are grouped as "Unknown Artist".

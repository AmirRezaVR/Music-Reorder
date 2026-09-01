# Music Reorder

A small Python app that rearranges your music files so songs from the same artist are not played one after another whenever possible.

## Why?

Some car audio systems don't have a shuffle option.

If your music files are sorted by artist on a USB flash drive, your car may play several songs from the same artist one after another.

Music Reorder solves this by creating a new order for your songs and adding a number to the beginning of each filename. Your car can then play the files in the new order.

## Features

- Select a music folder or drag and drop it into the app
- English and Persian interface
- Reads artist information from music file metadata
- Rearranges songs to keep the same artist apart whenever possible
- Adds numbers such as `001`, `002`, `003` to filenames
- Removes existing numbers before creating a new order
- Reorders all songs from scratch every time
- Automatically includes newly added songs
- Creates a separate output folder
- Keeps your original music files unchanged

## Supported Formats

- MP3
- FLAC
- M4A
- AAC
- OGG
- WAV
- WMA

## Requirements

- Python 3
- `mutagen`
- `tkinterdnd2`

Install the required packages with:

```bash
pip install -r requirements.txt
````

## How to Use

Run the program:

```bash
python music_shuffler.py
```

Then:

1. Select your music folder, or drag and drop it into the app.
2. Choose your language.
3. Click **Reorder and Copy Music**.
4. Wait for the new folder to be created.

The program creates the output folder next to your original folder.

For example:

```text
Music/
Music_Shuffled/
```

Your original files stay untouched.

The output folder will contain files like:

```text
001 - Song Name.mp3
002 - Another Song.mp3
003 - My Favorite Song.mp3
```

## Adding New Songs Later

You can keep adding new songs to your original music folder.

When you run Music Reorder again, it reads **all** the songs in the folder and creates a completely new order.

This means:

* Old songs are reordered again
* New songs are included automatically
* Previous positions are not preserved
* All songs are considered together when creating the new order

You don't need to manually rearrange or rename anything.

### What about the old numbers?

If a song already has a number from a previous run, Music Reorder removes it before creating the new order.

For example:

```text
001 - Song Name.mp3
```

will be treated as:

```text
Song Name.mp3
```

And even something like:

```text
001 - 002 - Song Name.mp3
```

will be cleaned up before the new number is added.

The result will be:

```text
001 - Song Name.mp3
```

So you won't end up with filenames like:

```text
001 - 002 - Song Name.mp3
```

or:

```text
001-001-Song Name.mp3
```

## How the Ordering Works

Music Reorder reads the `Artist` information from each music file and groups songs by artist.

It then creates a new order that tries to keep songs from the same artist apart.

For example, if you have:

```text
Artist A: 4 songs
Artist B: 3 songs
Artist C: 5 songs
Artist D: 2 songs
```

the result might look something like:

```text
A, B, C, D, A, B, C, D, A, B, C, A, C, C
```

The exact order can be different each time you run the program.

If one artist has many more songs than the others, it may not be possible to completely avoid consecutive songs from that artist. In that case, the program tries to keep them apart as much as possible.

## Output Folder

Music Reorder creates a separate folder next to your original music folder.

For example:

```text
Music/
Music_Shuffled/
```

The original folder is not modified.

Each time you run the program, the previous output folder is replaced with a fresh one containing the new order.

## Artist Information

The program uses the `Artist` information stored in each music file's metadata.

If an artist name cannot be found, the song is grouped under:

```text
Unknown Artist
```

or:

```text
خواننده نامشخص
```

depending on the selected language.

## Notes

Music Reorder does not move, delete, or modify your original music files.

It only copies them to the output folder and adds the new numbering to the copied files.

Numbering starts at `001` and automatically uses more digits when needed for larger collections.


## License

This project is licensed under the MIT License.

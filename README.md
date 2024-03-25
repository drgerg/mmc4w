# MMC4W - Minimal MPD Client for Windows 

You really should start here.  It's the [Help text](https://github.com/drgerg/mmc4w/blob/main/code/_internal/mmc4w_help.md).

## It Really is All About the Music.

The entire interface is intentionally tiny and simple. In its most basic mode it looks like this:

![titlebar.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/most_basic.png)

## MMC4W.py now runs in Ubuntu with no tweaking starting with v2.0.6.  

I recently added SHA256 hashes for the installer and mmc4w.py:  [File_Hashes.md](https://github.com/drgerg/mmc4w/blob/main/File_Hashes.md).

Playlist Builder Mode is one of my favorite things.  I've been looking forward to this for a long time.

![PlayList Builder Mode](https://github.com/drgerg/mmc4w/blob/main/pics/mmc4w_plb.png)

This is **such** a simple way to manage my playlists! While I'm listening, if I want to add or removed the current song, just click the playlist name.  Sweet!

![Testing v0.9.2](https://github.com/drgerg/mmc4w/blob/main/pics/testing_v0.9.2.jpg)Testing v0.9.2

### Intentionally tiny. Unexpectedly mighty. Basic and yet very capable.
> "I don't rent music. I don't trust 'the cloud' to be there when I want it." - me.

I needed a tiny set of controls for a couple of different **[Music Player Daemon](https://www.musicpd.org/)** (MPD) servers here.  

I could not find a Windows MPD client with an interface as small as what I wanted.  So I wrote this one.

Tkinter may not be sexy, but it gets the job done.  MMC4W does exactly what I need, simply and easily.  Play saved playlists, search your library easily for song titles, albums, or by text in an Artist's name.

MMC4W is natively a saved-playlist player.  There is also what I call "True Blue Album Mode" that plays all songs on an album sequentially, first to last.  Play single titles using 'Search by Title'.

There is one fairly simple config step after running the Windows installer.  [Find those details in the help text](https://github.com/drgerg/mmc4w/blob/main/code/mmc4w_help.md).  

Other than the basic controls, I also want to be able to see the album cover most of the time.  The **Art** button toggles a small window to display embedded or folder art.  The MPD server extracts it from the current song file or from a cover.jpg, .png, .tiff, or .bmp file located in the album folder and provides it.  MMC4W displays it. Dead simple.  That looks like this:

![screen_1.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_1.png)

The black background in this pic is my desktop.  The MMC4W interface is only the two small windows you see there.  Notice two other things about that pic:

- The title of the song and the artist's name are shown in the text area.
- The Windows titlebar is gone.

The **Mode** button toggles the titlebar.  While it's active, you can resize and reposition the windows.  Clicking **'Mode'** again saves positions and sizes.

The text area is active, switching every three seconds between song title - artist name and a line about the status of things as seen here:

![screen_2.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_2.png)

You are able to edit the configuration file (mmc4w.ini) by selecting **Config** | **Edit mmc4w.ini**.  It uses your system's default text editor.

### A Note About Window Positions

The windows are intended to be placed and left alone.  If you want to move them, click the **'Mode'** button.  The titlebars will be visible, and you can move the windows where you want them.  Clicking **'Mode'** again saves their position to the mmc4w.ini file in your installation folder.

I find this to be a perfectly acceptable arrangement.

Again, check the help file for more details.  I hope you enjoy using this as much as I do.


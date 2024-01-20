# MMC4W - Minimal MPD Client for Windows 

January 20 - "When you rush, that's when accidents happen." - v0.9.1 fixes a couple of annoying bugs birthed by my rushing things.  I feel like I have a solid foundation.  There are still things to adjust, but this is looking good.

January 19 - Initial testing of v0.9.0 with the **python-musicpd** library is good.  Thirteen hours straight with no errors.  Testing continues today.  I feel good enough about it to share the installer.  

January 18 - Good progress. Much hope.  

January 17, 2024 - Following v0.8.2, I'm currently reworking MMC4W to use the 'python-musicpd' client libary instead of what I started with (python-mpd2). v0.8.2 works pretty well, but will randomly get lost and need to be restarted.  I'm really looking forward to getting it to be 100% reliable. This will be my daily driver MPD client.

### Intentionally tiny. Unexpectedly mighty. Basic and yet very capable.
> "I don't rent music. I don't trust 'the cloud' to be there when I want it." - me.

I needed a tiny set of controls for a couple of different **[Music Player Daemon](https://www.musicpd.org/)** (MPD) servers here.  

I could not find a Windows MPD client with an interface as small as what I wanted.  So I wrote this one.

Tkinter may not be sexy, but it gets the job done.  MMC4W does exactly what I need, simply and easily.  Play saved playlists, search your library easily for song titles, albums, or by text in an Artist's name.

MMC4W is natively a saved-playlist player.  There is also what I call "True Blue Album Mode" that plays all songs on an album sequentially, first to last.  Play single titles using 'Search by Title'.

There is one fairly simple config step after running the Windows installer.  [Find those details in the help text](https://github.com/drgerg/mmc4w/blob/main/code/mmc4w_help.md).  

The entire interface is intentionally tiny and simple. In its most basic mode it looks like this:

![titlebar.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/titlebar.png)

Other than the basic controls, I also want to be able to see the album cover most of the time.  The **Art** button toggles a small window to display embedded art.  The MPD server extracts it from the current song file and provides it.  MMC4W displays it. Dead simple.  That looks like this:

![screen_1.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_1.png)

The black background in this pic is my desktop.  The MMC4W interface is only the two small windows you see there.  Notice two other things about that pic:

- The title of the song and the artist's name are shown in the text area.
- The Windows titlebar is gone.

The **Mode** button toggles the titlebar.  While it's active, you can reposition the windows.  Clicking **'Mode'** again saves positions.

The text area is active, switching every three seconds between song title - artist name and a line about the status of things as seen here:

![screen_2.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_2.png)

You are able to edit the configuration file (mmc4w.ini) by selecting **File** | **Configure**.  It uses Windows' default text editor.

### A Note About Window Positions

The windows are intended to be placed and left alone.  If you want to move them, click the **'Mode'** button.  The titlebars will be visible, and you can move the windows where you want them.  Clicking **'Mode'** again saves their position to the mmc4w.ini file in your installation folder.

I find this to be a perfectly acceptable arrangement.

Again, check the help file for more details.  I hope you enjoy using this as much as I do.  Let me know if you like it.


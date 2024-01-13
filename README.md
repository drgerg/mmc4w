# MMC4W - Minimal MPD Client for Windows </br> Proves 'Simple' does not equal 'Worthless'
### Intentionally tiny and simple. Basic and yet very capable.

I needed a tiny set of controls for a couple of different **[Music Player Daemon](https://www.musicpd.org/)** (MPD) servers here.  I could not find a Windows MPD client that was as simple as what I wanted.
This one is written in Python, using Tkinter. It may not be sexy, but it does exactly what I need without being obnoxious.  Search your library easily for song titles, albums, or by text in an Artist's name.

MMC4W is primarily a saved-playlist player.  There is also what I call "True Blue Album Mode" that plays all songs on an album sequentially, first to last.

This works for me. [More details are here in the help text](https://github.com/drgerg/mmc4w/blob/main/code/mmc4w_help.md).  
This is playlist-centered.  I wanted to start a playlist and then leave it alone.  I did add the ability to search and play a single title.  I'm planning to make an 'album' mode that plays albums from beginning to end.  Like when I was a child. There I said it.

The entire interface is intentionally tiny and simple. In its most basic mode it looks like this:

![titlebar.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/titlebar.png)

Other than the basic controls, I also want to be able to see the album cover most of the time.  The **Art** button toggles a small window to display embedded art.  The MPD server extracts it from the current song file and provides it.  MMC4W displays it. Dead simple.  That looks like this:

![screen_1.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_1.png)

The black background in this pic is my desktop.  The MMC4W interface is only the two small windows you see there.  Notice two other things about that pic:

- The title of the song and the artist's name are shown in the text area.
- The Windows titlebar is gone.

The **Mode** button toggles the titlebar.  While it's active, you can reposition the windows.  The text area is active, switching every three seconds between song title - artist name and a line about the status of things as seen here:

![screen_2.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_2.png)

You are able to edit the configuration file (mmc4w.ini) by selecting **File** | **Configure**.  It uses Windows' default text editor.

### A Note About Window Positions

The windows are intended to be placed and left alone.  If you want to move them, click the **'Mode'** button.  The titlebars will be visible, and you can move the windows where you want them.  Clicking **'Mode'** again saves their position to the mmc4w.ini file in your installation folder.

I find this to be a perfectly acceptable arrangement.

Again, check the help file for more details.  I hope you enjoy using this as much as I do.  Let me know if you like it.


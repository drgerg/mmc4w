# MMC4W - Minimal MPD Client for Windows
### Intentionally tiny and simple. Basic and yet capable.

I needed a tiny set of controls for a couple of different **[Music Player Daemon](https://www.musicpd.org/)** (MPD) servers here.  I could not find a Windows MPD client that was as simple as what I wanted.
This one is written in Python, using Tkinter and is about as basic as you can get. It does exactly what I need and nothing more.

This works for me. [More details are here in the help text](https://github.com/drgerg/mmc4w/blob/main/code/mmc4w_help.md).  That is exactly what you get when you click **Help** | **Help** in the app.

The entire interface is intentionally tiny and simple. In its most basic mode it looks like this:

![titlebar.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/titlebar.png)

Other than the basic controls, I also want to be able to see the album cover most of the time.  The **Art** button toggles a small window to display embedded art.  The MPD server extracts it from the current song file and provides it.  MMC4W displays it. Dead simple.  That looks like this:

![screen_1.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_1.png)

The black background in this pic is my desktop.  The MMC4W interface is only the two small windows you see there.  Notice two other things about that pic:

- The title of the song and the artist's name are shown in the text area.
- The Windows titlebar is gone.

The **Mode** button toggles the titlebar.  I really like that.  The text area is active, switching between song title - artist name and a line about the status of things as seen here:

![screen_2.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_2.png)

### Things I Might Do Differently

I really do not want to let scope creep bloat this.  However, there are some things that might get included like:

- Dynamic repositioning of all windows.  Right now you can set their initial position in the mmc4w.ini file.  You can also drag the main window if the titlebar is active.  The Art window, however is static. I'm OK with that right now.
- Maybe a second optional window that displays more stats. This is tickling my brain, but I'm not there yet.  


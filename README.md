# MMC4W - Minimal MPD Client for Windows </br> Proves 'Simple' does not equal 'Worthless'
### Intentionally tiny and simple. Basic and yet capable.

I needed a tiny set of controls for a couple of different **[Music Player Daemon](https://www.musicpd.org/)** (MPD) servers here.  I could not find a Windows MPD client that was as simple as what I wanted.
This one is written in Python, using Tkinter. It may not be sexy, but it does exactly what I need without being obnoxious.

This works for me. [More details are here in the help text](https://github.com/drgerg/mmc4w/blob/main/code/mmc4w_help.md).  
This is playlist-centered.  I wanted to start a playlist and then leave it alone.  I did add the ability to search and play a single title.  I'm planning to make an 'album' mode that plays albums from beginning to end.  Like when I was a child. There I said it.

The entire interface is intentionally tiny and simple. In its most basic mode it looks like this:

![titlebar.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/titlebar.png)

Other than the basic controls, I also want to be able to see the album cover most of the time.  The **Art** button toggles a small window to display embedded art.  The MPD server extracts it from the current song file and provides it.  MMC4W displays it. Dead simple.  That looks like this:

![screen_1.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_1.png)

The black background in this pic is my desktop.  The MMC4W interface is only the two small windows you see there.  Notice two other things about that pic:

- The title of the song and the artist's name are shown in the text area.
- The Windows titlebar is gone.

The **Mode** button toggles the titlebar.  I really like that.  The text area is active, switching every three seconds between song title - artist name and a line about the status of things as seen here:

![screen_2.png](https://github.com/drgerg/mmc4w/blob/main/code/_internal/screen_2.png)

You are able to edit the configuration file (mmc4w.ini) by selecting **File** | **Configure**.  It uses Windows' default text editor.

### Things I Might Do Differently

I really do not want to let scope creep bloat this.  However, there are some things that might get included like:

- Dynamic repositioning of all windows.  Right now you can set their initial position in the mmc4w.ini file.  You can also drag the main window if the titlebar is active.  The Art window, however is static. I'm OK with that right now.
- Maybe a second optional window that displays more stats. This is tickling my brain, but I'm not there yet.
- Tweak some details in the main window for those with heightened aesthetic sensitivies. 

### A Note About Window Positions

I put the windows where I wanted them.  Down low and off to the right side.  You can find that down around line 400:

```
window.title("Minimal MPD Client " + version)  # Set window title
winWd = 380  # Set window size
winHt = 80
confparse.read(mmc4wIni)  # get parameters from config .ini file.
win_x = int(confparse.get("mainwindow","win_x"))
win_y = int(confparse.get("mainwindow","win_y"))
tbarini = confparse.get("mainwindow","titlebarstatus")
x_Left = int(window.winfo_screenwidth() - (winWd + win_x))
y_Top = int(window.winfo_screenheight() - (winHt + win_y))
window.geometry(str(winWd) + "x" + str(winHt) + "+{}+{}".format(x_Left, y_Top))
```
As you can see there, you can alter the initial position of the windows in the mmc4w.ini file.  The entries required are relative to the screen width and the width of the window.
I find this to be a perfectly acceptable arrangement.

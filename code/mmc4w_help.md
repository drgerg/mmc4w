# MMC4W - Minimal MPD Client for Windows

This help file was updated for the v0.9.4 release.

## Putting the Music First

**MMC4W** is first and foremost **Minimal**.  That may be a little misleading, because it does quite a lot.  The GUI is minimal so as not to take up much room. That was the original point of this exercise.

**MMC4W** is a MPD Client.  To be clear, you must have access to a running MPD server for this app to be of any value to you.

**MMC4W** is open source, and does not send any data out to anyone anywhere.  It connects only to the MPD server you specify in the configuration file. (mmc4w.ini)

The interface contains the basic required buttons to control a MPD server:

- Vol +, Vol -, Play, Stop, Prev, Pause, Next and Quit.
- A 'Mode' button eliminates the Windows title bar if desired.
- An 'Art' button toggles a very small window that displays embedded album art.  
    - If no embedded art is found, MMC4W's logo is displayed.

### The **'File'** menu contains these functions:

- Configure : Opens mmc4w.ini for editing. Uses Windows configured .ini editor. (Notepad or similar)
- Select Server : Allows you to select a server from the list in mmc4w.ini. Prompts you to select a playlist also.
- Toggle Logging : Toggles logging On or Off.  Restart the app after toggling.
- Reset Win Positions: Puts the two primary windows back where they were originally.
- Create New Saved Playlist : Creates a new empty playlist with your specified name
- Remove Saved Playlist : Permanently deletes a saved playlist. Permanently.
- Exit : Same as the 'Quit' button: exits the app.

### The **'Tools'** menu has these functions:

- Reload Current Title : Reloads data about the current playing song, including art.
- Turn Random On : Turns on random playback. Text area background is white.
- Turn Random Off : Turns on sequential playback. Text area background is navy blue.
- Toggle Repeat : If repeat is 0, play stops when MPD gets to the end of the playlist.
- Toggle Consume : If consume is 1, each song is removed from the playlist after playing.
- Toggle Single : If single is 1, each song is only played once, but left in the list.
- Toggle Titlebar : Exposes the Windows titlebar. This allows repositioning of windows.
- Set Non-Standard Port : Tells you how to set up a non-standard port.

### There is a **'Look'** menu that has these functions:

- Play a Single : Select a single title by title. (also emulates a little console. See Searching.)
- Play an Album : Select an album by album title. Turns on sequential playback.
- Find by Artist : Select a single title by artist. Also get info at the same time.
- Reload Last Playlist : Restore your settings to the last configured playlist.
- Show Songs in Last Playlist : View the list of songs in the last selected PL. Click to play.
- Select a Playlist : Select any playlist available on the connected server.
- Update "Everything" Playlist : Make sure all songs are in the "Everything" playlist.
- Toggle PL Build Mode : Sets PL Build Mode. Easily add or delete songs from saved playlists.

### The 'Help' menu contains:

- Help : This document.
- About : Look here to find your installation path and version number.

## Some Things MMC4W Does NOT Do:

- Does not constantly poll the server. - **MMC4W** checks back with the server when the song is ending.
- Does not discover servers.  You need to know the IP address of any servers you wish to control.
- Does not edit tags, display lyrics, get art from the web, display artist info, wash dishes or vacuum floors.
- Does not tell you what saved playlist was loaded into the queue on a server you just joined. Nobody can do that.

## First Run Process

MMC4W ships with a blank .ini file.  The first time you run it, it will pop up a box like this:

![The Configure dialog.](./_internal/edit_config_dialog.png)

When you press the 'OK' button, **mmc4w** opens mmc4w.ini using the default Windows text editor.  On my system it's Notepad++.  Word processors like **Microsoft Word** should be avoided.  Only use a text editor that edits and saves plain ASCII text.  **Notepad** is perfectly fine for this job.

You need to type in your preferred MPD servers' IP address(es) in the [basic] section as shown.  Be sure to put that trailing comma on there whether you have one or several.

![inside the mmc4w.ini file](./_internal/config_ini_basics.png)

If you have more than one server, just string those IP addresses together as seen there.

After typing your server IP address(es) in the [basic] section, save and close the file.

Restart **MMC4W**.  When it starts, it will attempt to connect to the first server you provided.  You can change the server by using the option under the **'File'** menu.

In the text bar of the app you will see a prompt to select one of that server's playlists.

![Select a playlist prompt](./_internal/select_playlist_prompt.png)

Click on the Look menu and select "Select a Playlist". Once you've clicked on a playlist, you can hit the **'Play'** button.  You may notice an entry following "Current Playlist - ".  You will still want to click on a list in the dropdown even if you choose the same one.

![Select a playlist](./_internal/select_playlist.png)

### Normal Operation

After you press **'Play'**, just kick back and enjoy the music.

MMC4W will show you these basic statistics, alternating between the two lines of text shown in these two images:

![Track name and Artist](./_internal/screen_1.png)</br><span style="color:green; font-size:smaller;">Track number, Track name and Artist.</span>

![Server IP, status, playlist.](./_internal/screen_2.png)</br><span style="color:green; font-size:smaller;">Server, Play Status, PlayList and Elapsed-vs-Duration in seconds.</span>

Random, rePeat, Single and Consume status is shown here.  A capital letter means 'ON', lower case means 'OFF'. 'P' is for rePeat because you can't have two 'R's.

![Random, rePeat, Single and Consume](./_internal/screen_2b.png)

The **'Art'** button toggles the small album art window.

The **'Mode'** button toggles the titlebar like this:

![Titlebar on.](./_internal/titlebar.png)

When the titlebars are on, you can drag the windows around. (You will likely have to expand the art window a bit).  Where you leave the upper-left corners gets saved when you press **'Mode'** again.  Your windows will stay there until you press **'Mode'** again.

The default out-of-the-box values are saved in the mmc4w.ini file at the bottom.  Use those in case things get out of hand.

### Search and Play

There are three options under the **'Look'** menu related to search.

- Play a Single
- Play an Album
- Find by Artist

 All three options use the same window, just differently. There's a 'mode' hint in the titlebar to help you out.

**Note:** The Search window is resizeable.  

 **Play a Single** opens the Search window and allows you to type some search term.  This is a **Title** search.  If any song title in the entire library contains the search term, it will be displayed when you press **[enter]**

![Title Search.](./_internal/search_title.png)</br><span style="color:green; font-size:smaller;">Song title search.</span>

 When you click on one of them, it plays that one title then stops.  Use another **'Look'** menu option to do something else.

 **Play an Album** opens the same Search window.  This time you are searching for text contained in **Album** names.

 Clicking on a list entry loads up the songs on that album and plays them sequentially, first to last.  You will notice the text area turns blue with white text.  That is the visual indicator that **Random Mode** has been turned off.  

![Album Search.](./_internal/album_mode.png)</br><span style="color:green; font-size:smaller;">Album title search.</span>

 I call this "**True Blue Album Mode**".  Use the **'Tools'** menu to turn Random playback on when you want it. No assumptions are made about whether you want random or sequential playback outside of Album Mode.

**Find by Artist** opens the Search window, but this time you are searching by Artist name.  Keep in mind this is the name as it appears in your music library. If you click in the Search: field and just press [enter], you'll get a list of all your songs ordered by Artist.  

![Artist Search.](./_internal/search_artist.png)</br><span style="color:green; font-size:smaller;">Artist search. Click in field and hit Enter for all songs.</span>

This can be useful when you don't know what you're looking for.  Otherwise, type in some text to filter your list.

## Working with Saved Playlists

Saved playlists are the heart of **MMC4W**. To differentiate between **saved playlists** and the list of songs currently being played, the latter is called **"the queue"**.  **Playlists** are lists of songs saved to a file on disk with some meaningful name.

You load playlists into the queue and then MPD plays that queue using the settings in force at the moment.  

MMC4W will create a special playlist called "Everything" that contains all the songs in your library.  That option is found in the **'Look'** Menu.

### You can manipulate playlists in these ways:

 - Load a playlist into the queue.  **Look Menu** - Select a Playlist.
 - Reload the last playlist into the queue.  **Look Menu** - Reload Last Playlist.
 - List the songs in the last loaded playlist. **Look Menu** Show Songs in Last Playlist.
    - (moveable, resizable window)
 - Jump to and play a selected song from the last loaded playlist. **Look Menu** Show Songs in Last Playlist.
 - Create a new empty playlist. **File Menu** - Create New Saved Playlist.
 - Delete a playlist. **File Menu** - Remove Saved Playlist.
 - Add the currently playing song to any saved playlist.
 - Delete the currently playing song from the last loaded saved playlist.

## Adding and Removing Songs in a Saved Playlist:

**MMC4W** lets you add songs to playlists as you go.  No need to stop playback.

![Toggle PL Build Mode](./_internal/plbuildmode1.png)
![PL Build Mode](./_internal/plbuildmode2.png)

1) Use the **Toggle PL Build Mode** option in the **Look Menu** to turn on PL Build Mode. </br>&nbsp;&nbsp;&nbsp;&nbsp;Buttons turn red and green.  
2) If you're not already, play your music.  
3) When you are listening to a song you want to add to a playlist, hit the green **Add** button.  
4) Click on the playlist you want from the list.  

**That's it.**

#### Deleting a song from the current saved playlist is just as easy:

1) In **PL Build Mode**, when you hear a song you want to remove, click the red **'Delete'** button.  
2) Respond to the prompt, and if you selected OK, the song will be gone from the saved playlist.

**You can be intentional:**  
Use the **Play a Single**, **Play an Album**, or **Find By Artist** options under the **Look** menu to play a specific song or album.  
When it's playing, hit the green **Add** button and select the playlist.  

Use **Look** "Show Songs in Last Playlist".  Select the odious song you want to remove.  
Hit the **Delete** button to get rid of it. (or **Add** if you wish. I mean, you never know.)
## The 'mini console'

- Select the 'Play a Single' option.
- In the Search: field, type 'status' (no quotes).  You'll see the current status info.
- Type 'stats' and you'll get server stats appended to the bottom.  Scroll down.
- Type 'quit;' (with the semicolon) and the window closes.

This was something I just didn't want to do without.

## Logging 

Logging can be enabled by using the '**Toggle Logging**' option under the **File** menu.

![Toggle Logging](./_internal/toggle_logging.png)

After using the '**Toggle Logging**' option, restart MMC4W.

MMC4W currently supports two levels of logging: **INFO** and **DEBUG**.  INFO lists basic actions that should be occurring as they occur.  DEBUG adds another layer of potentially useful data to the stream.

![Setting the Log Level](./_internal/logging.png)

To set the logging level, use the '**Configure**' option and edit the **mmc4w.ini** file.  Type either 'info' or 'debug' where indicated (without quotes).

The resulting log file (**mmc4w.log**) can be found in the **_internal** folder in the installation folder.  The log file is deleted and started fresh each time you start **MMC4W**.  If you toggle Off logging, the last log file will remain until you delete it or create a new one by toggling logging On again.

The DEBUG file (**mmc4w_DEBUG.log**) does not start fresh with each run, and is not deleted.

### Other Random Options

Under the **'Tools'** menu there is the **'Set Non-Standard Port'** option.  Choosing that opens a pop-up which provides details about how to set any port other than 6600 (the default MPD port).  Most people will never use this.

## Notes About What Happens Under the Hood

When you press '**Play**', MMC4W reaches out to the configured server and asks for data on the current song.  Then it asks for a status report.  From the returned data, MMC4W calculates how much longer the current song should be playing.  If album art is being displayed, it attempts to get art embedded in the song.  If that is successful, it displays the art.  If not, it displays the MMC4W logo.

MMC4W uses the Python **threading** module to run a timer in conjunction with a small set of global variables.  In this way we're able to keep the interface satisfactorily snappy and avoid having to poll the server every few seconds to determine if a new song is playing.

The Tkinter interface runs continuously waiting for button presses.  Blocking code (like sleep(10)) is avoided at all cost.  As a result, things work.  From my chair, it's perfect.  We'll see how long that perspective lasts, shan't we?

The design of this utility is intentionally simple.  I'm sure there are several 'better' ways it can be done, I just don't know what they are. 

### Minutia

MMC4W was developed and tested in Windows 10.  **MPD** is running on three different computers here, one i7 Ubuntu, one i3 Ubuntu and one Raspberry Pi.  My music library is made up exclusively of FLAC files.  I rip my CD's (remember those?) using [Music Bee](https://getmusicbee.com/).  I create a 'folder.jpg' file for each album and embed the art in the songs using **[MP3TAG](https://www.mp3tag.de/en/)** or **Music Bee** depending on the circumstances.

I hope you enjoy using this as much as I do.<br><br>

  -------------------------------------------- <br>
**MMC4W** is written in <span style="color:red;">Python</span> and complied using <span style="color:red;">Pyinstaller</span>.  The Windows installer is built using the <span style="color:red;">Inno Setup Compiler</span>.  
**Many thanks** to <span style="color:green;">bauripalash (Palash Bauri)</span> for [tkhtmlview](https://github.com/bauripalash/tkhtmlview), which makes this help file window look so good!  
**Also thanks** to [kaliko](https://gitlab.com/kaliko) for the [python-musicpd](https://gitlab.com/kaliko/python-musicpd) library!  
And of course none of this would be possible without the excellent contribution of [MPD](https://github.com/MusicPlayerDaemon) by Max Kellermann.  **Thanks!!**  
&copy;2023-2024 - Gregory A. Sanders (dr.gerg@drgerg.com)

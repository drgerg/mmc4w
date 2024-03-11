Minimal MPD Client - v2.0.7

Check out the offline help under the Help menu. (updated for v2.0.7)

v2.0.7 is a quick bug-fix.  

Replaced os.path with pathlib.
Recoded connection error to accept 'Already Connected' (as it should) and move on.

v2.0.6 Update Notes:

Time came for a refactoring.  The code is better than it was.  
Fewer lines and improved functionality.  
Solved a search issue in PL Builder Mode that caused erroneous PL window entries.  
Created ways to dramatically reduce the size of the mmc4w.ini file.  
The same code now works in both Windows and Linux without modification.  
Provided a way to manage scaled displays. This is still being tested, but seems to work fine.  
A few change in Search and Queue windows:  
 - You can search by typing artist:pink or title:city or album:greatest  
 - You can save the current size and placement of the search window by typing savewin; with the semicolon.  
 - Of course the menu option you used when you opened a window is still the default for that window.  
When playing an album, the album title is shown in place of a playlist name in the text bar.  

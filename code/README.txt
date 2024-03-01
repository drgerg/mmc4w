Minimal MPD Client - v2.0.1

Check out the offline help under the Help menu. (updated for v2.0.0)

Added a Queue menu to support working with the current song queue.
  1) Search as many terms as you want until you find what you want. 
     Then click on an entry to jump to that song.
  2) You can also search using strings like this: artist:mumford or album:greatest.
     If you only use one word, it defaults to being a title search.
  3) The queue is displayed in 'Artist' sorted order, not the actual order of songs.
     The intent is to make it easier to find things by scrolling.
  4) Use quit; in the Search: field to close the window. The semicolon is important.

Folder art is now supported along with embedded art.  
  cover.png, cover.jpg, cover.tiff or cover.bmp are supported filenames.

Changed to 'listvariable' method of populating selection lists.
Added saving and restoring of main window sizes to "Mode" functions.
Corrected a condition in the Search window that caused additional searches to concatenate rather than replace items in the textbox.
Corrected a condition that caused the song duration to display improperly if it were less or more than three digits.

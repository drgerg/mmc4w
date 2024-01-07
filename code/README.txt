Minimal MPD Client - v0.0.5

Check out the offline help under the Help menu.

- Improved connection status handling.
- Added code to compensate for the time Pause is engaged.
- Added  remaining/duration seconds to stat display.
- Added 'Toggle Logging' item to File Menu.
- DEBUG log is written to a separate file from the INFO level log.
    The DEBUG log is not automatically deleted like the INFO log.
- Changed from ttk.Button to tk.Button in order to be able to 
    change the background color of Pause when paused. It's a nice retro look.


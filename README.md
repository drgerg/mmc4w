# mmc4w
## Minimal MPD Client for Windows
### October 14, 2023 - This is a new project, not perfect in any way.
There is a lot of detail work to do before it's "finished finished".

I needed a tiny set of controls for a couple of different **[Music Player Daemon](https://www.musicpd.org/)** (MPD) servers here.  I could not find a Windows MPD client that was as simple as what I wanted.  

This one is written in Python, using Tkinter and is about as basic as you can get.

It does exactly what I need and nothing more.

## Windows Defender flags it as a severe threat
This is pretty common.  This is just [one of many sites](https://medium.com/@markhank/how-to-stop-your-python-programs-being-seen-as-malware-bfd7eb407a7) describing the problem.
When I first installed my own app, Windows stuck it in the quarantine folder and said it was malicious.  I had to add an exception in Defender settings and restore it from the quarantine before I could use it.
If all this troubles you, then don't download the compiled executable installer.  Download the source and run it raw, or compile it yourself.  Sorry, but that's where we are.

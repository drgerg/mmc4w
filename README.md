# mmc4w - Minimal MPD Client for Windows
### Intentionally tiny and simple. Basic and yet capable.
This works for me. [The help menu is here](https://github.com/drgerg/mmc4w/blob/main/code/mmc4w_help.md).

I needed a tiny set of controls for a couple of different **[Music Player Daemon](https://www.musicpd.org/)** (MPD) servers here.  I could not find a Windows MPD client that was as simple as what I wanted.

The entire interface is intentionally tiny and simple. In its most basic mode it looks like this:

![titlebar.jpg](https://github.com/drgerg/mmc4w/blob/main/code/_internal/titlebar.png)

This one is written in Python, using Tkinter and is about as basic as you can get. It does exactly what I need and nothing more.

## Windows Defender falsely flags this and certain other Python apps as a severe threat
When I first installed my own app, Windows stuck it in the quarantine folder and said it was malicious.  I had to add an exception in Defender settings and restore it from the quarantine before I could use it.

What can I say? Look at the code and you can see I've written in nothing that does anything other than control your MPD server to play your music.  

This false positive warning is apparently pretty common.  This is just [one of many sites](https://medium.com/@markhank/how-to-stop-your-python-programs-being-seen-as-malware-bfd7eb407a7) describing the problem.  If I knew of a no-cost way to solve this problem, it would be solved.

If all this troubles you, then don't download the compiled executable installer.  Download the source and run it raw, or compile it yourself.  Sorry, but that's where we are.

mmc4w_diag.py is a simple tool to display the returned data for two commands.

 - client.status()
 - client.currentsong()

This provides a wealth of data about what's going on.
Edit the mmc4w_diag.ini file so it has the IP address of the server you are connecting to.
Then run mmc4w_diag.py from a terminal.  The output should look something like this:
```
mmc4w_diag.py v0.0.2
Powered by the musicpd module
Connected to server 192.168.1.22 on port 6600.

OUTPUT OF CLIENT.STATUS():
volume : 40
repeat : 0
random : 1
single : 0
consume : 1
partition : default
playlist : 102
playlistlength : 691
mixrampdb : 0
state : play
song : 101
songid : 822
time : 324:513
elapsed : 323.813
bitrate : 1102
duration : 512.933
audio : 44100:16:2
nextsong : 391
nextsongid : 1128

OUTPUT OF CLIENT.CURRENTSONG():
file : The Who/The Who - The Ultimate Collection - Disc 2/02-Wont Get Fooled Again.flac
last-modified : 2023-12-18T23:22:01Z
format : 44100:16:2
title : Won't Get Fooled Again
artist : The Who
album : The Who - The Ultimate Collection - Disc 2
genre : Rock
track : 2
date : 2002
time : 513
duration : 512.933
pos : 101
id : 822
```


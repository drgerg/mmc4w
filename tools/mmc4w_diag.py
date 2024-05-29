#!/usr/bin/env python3
# 
# mmc4w_diag.py - 2024 by Gregory A. Sanders (dr.gerg@drgerg.com)
# Minimal MPD Client for Windows Diagnostics Tool
# mmc4w_diag.py uses the python-musicpd library.
##

import sys
from configparser import ConfigParser
import os
import musicpd
from pathlib import Path

version = "v0.0.2"

client = musicpd.MPDClient()                    # create client object

# confparse is for general use for normal text strings.
confparse = ConfigParser()

# cp is for use where lists are involved.
cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})

path_to_dat = Path(__file__).parent
mmc4wIni = path_to_dat / "mmc4w_diag.ini"
workDir = os.path.expanduser("~")
confparse.read(mmc4wIni)
serverip = confparse.get('serverstats', 'lastsrvr')
serverport = confparse.get('serverstats','lastport')

client.connect(serverip, int(serverport))

cs = []
stat = []
stat = client.status()
cs = client.currentsong()
print("\nmmc4w_diag.py v0.0.2\nPowered by the musicpd module\nConnected to server {} on port {}.".format(serverip,serverport))
print("\nOUTPUT OF CLIENT.STATUS():")
for k, v in stat.items():
    print("{} : {}".format(k,v))
print("\nOUTPUT OF CLIENT.CURRENTSONG():")
for k2, v2 in cs.items():
    print("{} : {}".format(k2,v2))

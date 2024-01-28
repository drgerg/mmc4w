#!/usr/bin/env python3
# 
# mmc4w.py - 2024 by Gregory A. Sanders (dr.gerg@drgerg.com)
# Minimal MPD Client for Windows - basic set of controls for an MPD server.
# Take up as little space as possible to get the job done.
# mmc4w.py uses the python-musicpd library.
##

from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.font import Font
from time import sleep
import sys
from configparser import ConfigParser
from os import path
import os
from tkhtmlview import HTMLScrolledText, RenderHTML, HTMLLabel
import musicpd
import threading
from PIL import ImageTk, Image
import time
import logging
import webbrowser

version = "v0.9.7"
# v0.9.7 - Add output selection and local HTTP playback via browser.
# v0.9.6 - Add 'delete current song' to the PL Builder mode and play from 'List Songs'.
# v0.9.5 - Adds two missing PL actions: List songs, and Delete a song.
# v0.9.4 - Adds ability to create new saved playlists and add songs to existing PLs.
# v0.9.3 - Updates to Help text and general tweaks.
# v0.9.2 - Finally reached a solid foundation.
# v0.9.1 - Bugs left over from being in a hurry.
# v0.9.0 - Start over with a different approach.

client = musicpd.MPDClient()                    # create client object

# confparse is for general use for normal text strings.
confparse = ConfigParser()
# cp is for use where lists are involved.
cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})

path_to_dat = path.abspath(path.dirname(__file__))
mmc4wIni = path_to_dat + "/mmc4w.ini"
workDir = os.path.expanduser("~")
confparse.read(mmc4wIni)

lastpl = confparse.get("serverstats","lastsetpl") ## 'lastpl' is the most currently loaded playlist.
if confparse.get('basic','installation') == "":
    confparse.set('basic','installation',path_to_dat)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
#
logLevel = confparse.get('program','loglevel').upper()
logtoggle = confparse.get('program','logging').upper()
if logtoggle == 'OFF':
    logLevel = 'WARNING'

if logLevel == "INFO":
    if os.path.isfile(path_to_dat + "./mmc4w.log"):
        os.remove(path_to_dat + './mmc4w.log')

if logLevel == 'DEBUG':
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w_DEBUG.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.DEBUG,
    )

if logLevel == 'INFO':
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.INFO,
    )

if logLevel == 'WARNING':
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.WARNING,
    )

logger = logging.getLogger(__name__)
musicpd_logger = logging.getLogger('musicpd')
musicpd_logger.setLevel(logging.WARNING)

global serverip,serverport,tbarini,endtime,firstrun
aartvar = 0     ## aartvar tells us whether or not to display the art window.
endtime = time.time()
cxstat = 0      ## 'cxstat' indicates the connection status. '1' is connected.
buttonvar = 'stop'
pstart = 0      ## the time the pause button was pressed.
dur='0'         ## the value from client.getcurrentsong() showing the song's duration.
pause_duration = 0.0
sent = 0
lastvol = confparse.get('serverstats','lastvol')
serverlist = confparse.get('basic','serverlist')
serverip = confparse.get('serverstats', 'lastsrvr')
serverport = confparse.get('basic','serverport')
firstrun = confparse.get('basic','firstrun')
if firstrun == '1':
    ran = 'r'
    rpt = 'p'
    sin = 's'
    con = 'c'

if serverlist == "":
    proceed = messagebox.askokcancel("Edit Config File","OK closes the app and opens mmc4w.ini for editing.")
    if proceed == True:
        os.startfile(mmc4wIni)
        sys.exit()

if serverip == '':
    cp.read(mmc4wIni)
    iplist = cp.getlist('basic','serverlist')
    serverip = iplist[0]
    confparse.set('serverstats','lastsrvr',serverip)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

if confparse.get('serverstats','lastport') != "":
    serverport = confparse.get('serverstats','lastport')
else:
    confparse.set('serverstats','lastport',serverport)
    # logger.info("Writing port to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

if version != confparse.get('program','version'):
    confparse.set('program','version',version)
    # logger.info("Writing version to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

lastpl = confparse.get('serverstats','lastsetpl')

def getoutputs():
    connext()
    outputs = []
    outputsraw = client.outputs()
    for thisop in outputsraw:
        if thisop['outputenabled'] == '1':
            openab = 'Enabled'
        else:
            openab = 'Disabled'
        outputs.append(str('ID: {} "{}" Status: {}'.format(thisop['outputid'],thisop['outputname'],openab)))
    return outputsraw,outputs

def connext():  ## Checks connection, then connects if necessary.
    global serverip,serverport,cxstat
    try:
        client.ping()  # Use ping() to see if we're connected.
        cxstat = 1
    except (musicpd.ConnectionError, ConnectionRefusedError,ConnectionAbortedError) as errvar:
        logger.debug("D1| Initial errvar: {}".format(errvar))
        if errvar == 'Already connected':
            cxstat = 1
            pass
        else:
            cxstat = 0
            try:
                logger.debug("D1| Try to reconnect to {} on port {}".format(serverip,serverport))
                client.connect(serverip, int(serverport))
                cxstat = 1
                logger.debug('D1| 2nd try. cxstat is : ' + str(cxstat))
            except  (ValueError, musicpd.ConnectionError, ConnectionRefusedError,ConnectionAbortedError) as errvar:
                logger.debug("D1| Second level errvar: {}".format(errvar))
                cxstat = 0
                endWithError('Second level connection error:\n' + str(errvar) + '\nQuitting now.')
    return cxstat


def plrandom():  # Set random playback mode.
    global ran
    client.random(1)
    ran = 'R'
    text1['bg']='white'
    text1['fg']='black'

def plnotrandom():  # Set sequential playback mode.
    global ran
    client.random(0)
    ran = 'r'
    text1['bg']='navy'
    text1['fg']='white'

def halt():
    global endtime,buttonvar
    connext()
    buttonvar = 'stop'
    client.stop()
    endtime = time.time()
    return buttonvar

def play():
    global buttonvar,prevbtnstate
    if buttonvar == 'pause':
        pause()
    else:
        connext()
        prevbtnstate = buttonvar
        buttonvar = 'play'
        client.play()
        getcurrsong()

def next():
    global buttonvar
    if buttonvar == 'pause':
        pause()
    else:
        connext()
    try:
        client.next()
    except musicpd.CommandError:
        client.play()
        client.next()
    getcurrsong()

def previous():
    global buttonvar
    if buttonvar == 'pause':
        pause()
    else:
        connext()
    try:
        client.previous()
    except musicpd.CommandError:
        client.play()
        client.previous()
    getcurrsong()

def pause():  # Pause is complicated because of time-keeping.
    global buttonvar,endtime,pstart,pause_duration,eptime,pstate
    logger.debug('Play state at button press: {}.'.format(buttonvar))
    #
    if buttonvar == 'pause':        ## SYSTEM WAS PAUSED
        logger.debug("pause() pstart: {}".format(pstart))
        pause_duration = time.time() - pstart
        logger.debug("time.time(): {}, pstart: {}.".format(time.time(),pstart))
        logger.info(f"0) Playback resumed at {time.time()}. Pause duration: {pause_duration:.2f}")
        oldendtime = endtime
        endtime = endtime + pause_duration
        logger.info('2) New endtime generated in pause(). Old: {}, New {}'.format(oldendtime,endtime))
        button_pause.configure(text='Pause',bg='SystemButtonFace') ## 'systemButtonFace' is the magic word.
        pstate = 'play'
        pstart = 0 
        #                           ## Now client.pause() sets it to PLAY
    if buttonvar == 'play':         ## SYSTEM WAS PLAYING
        pstart = time.time()
        buttonvar = 'pause'
        button_pause.configure(text='Resume',bg="orange")
        logger.info("0) Playback paused at {}.".format(pstart))
        pstate = 'pause'
        #                           ## Now client.pause() sets it to PAUSE
    connext()
    client.pause()
    getcurrstat()

def volup():
    global lastvol
    connext()
    vol_int = int(lastvol)
    if vol_int < 100:
        client.volume(+5)
        vol_int = vol_int + 5
        volbtncolor(vol_int)


def voldn():
    global lastvol
    connext()
    vol_int = int(lastvol)
    if vol_int > 0:
        client.volume(-5)
        vol_int = vol_int - 5
        volbtncolor(vol_int)



def volbtncolor(vol_int):  # Provide visual feedback on volume buttons.
    global lastvol
    lastvol = str(vol_int)
    thisvol = vol_int
    upconf = ['Vol +','SystemButtonFace','black']
    dnconf = ['Vol -','SystemButtonFace','black']
    if thisvol == 100:
        upconf = ['100','gray13','white']
    if thisvol == 95:
        upconf = ['95','gray12','white']
    if thisvol == 90:
        upconf = ['90','AntiqueWhite4','black']
    if thisvol == 85:
        upconf = ['85','AntiqueWhite4','black']
    if thisvol == 80:
        upconf = ['80','AntiqueWhite3','black']
    if thisvol == 75:
        upconf = ['75','AntiqueWhite3','black']
    if thisvol == 70:
        upconf = ['70','AntiqueWhite2','black']
    if thisvol == 65:
        upconf = ['65','AntiqueWhite2','black']
    if thisvol == 60:
        upconf = ['60','AntiqueWhite1','black']
    if thisvol == 55:
        upconf = ['55','AntiqueWhite1','black']
    if thisvol == 50:
        upconf = ['Vol +','SystemButtonFace','black']
        dnconf = ['Vol -','SystemButtonFace','black']
    if thisvol == 45:
        dnconf = ['45','CadetBlue1','black']
    if thisvol == 40:
        dnconf = ['40','CadetBlue1','black']
    if thisvol == 35:
        dnconf = ['35','turquoise1','black']
    if thisvol == 30:
        dnconf = ['30','turquoise1','black']
    if thisvol == 25:
        dnconf = ['25','turquoise2','black']
    if thisvol == 20:
        dnconf = ['20','turquoise2','black']
    if thisvol == 15:
        dnconf = ['15','turquoise3','black']
    if thisvol == 10:
        dnconf = ['10','turquoise3','black']
    if thisvol == 5:
        dnconf = ['5','turquoise4','white']
    if thisvol == 0:
        dnconf = ['0','turquoise4','white']
    button_volup.configure(text=upconf[0],bg=upconf[1],fg=upconf[2])
    button_voldn.configure(text=dnconf[0],bg=dnconf[1],fg=dnconf[2])
    currvolconf = confparse.get('serverstats','lastvol')
    if lastvol != currvolconf:
        confparse.set('serverstats','lastvol',lastvol)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        logger.info('Saved volume to mmc4w.ini. lastvol is {}.'.format(lastvol))

def toglrepeat():
    global rpt
    connext()
    cstats = client.status()
    rptstat = cstats['repeat']
    if rptstat == '0':
        client.repeat(1)
        rpt = 'P'
        msg = 'Repeat is set to ON.'
    else:
        client.repeat(0)
        rpt = 'p'
        msg = 'Repeat is set to OFF.'
    displaytext1(msg)

def toglconsume():
    global con
    connext()
    cstats = client.status()
    cnsmstat = cstats['consume']
    if cnsmstat == '0':
        client.consume(1)
        con = 'C'
        msg = 'Consume is set to ON.'
    else:
        client.consume(0)
        con = 'c'
        msg = 'Consume is set to OFF.'
    displaytext1(msg)

def toglsingle():
    global sin
    connext()
    cstats = client.status()
    snglstat = cstats['single']
    if snglstat == '0':
        client.single(1)
        sin = 'S'
        msg = 'Single is set to ON.'
    else:
        client.single(0)
        sin = 's'
        msg = 'Single is set to OFF.'
    displaytext1(msg)
#
##  DEFINE getcurrsong() - THE MOST POPULAR FUNCTION HERE.
#
def getcurrsong():
    global globsongtitle,endtime,aatgl,sent,pstate,elap,firstrun,prevbtnstate,lastvol,cxstat,buttonvar,ran,rpt,sin,con
    connext()
    if threading.active_count() < 2:
        logger.debug("D9| The threading.active_count() dropped below 2. Quitting.")
        exit()
    logger.info(' = = = = = = getcurrsong = = = = = = = = ')
    logger.debug("D2| Sent: {}".format(sent))
    gsent = sent
    gpstate = ''
    cs = []
    stat = []
    stat = client.status()
    if stat['random'] == '0':
        ran = 'r'
        text1['bg']='navy'
        text1['fg']='white'
    else:
        ran = 'R'
        text1['bg']='white'
        text1['fg']='black'
    if stat['repeat'] == '1':
        rpt = 'P'
    else:
        rpt = 'p'
    if stat['single'] == '1':
        sin = 'S'
    else:
        sin = 's'
    if stat['consume'] == '1':
        con = 'C'
    else:
        con = 'c'
    logger.debug('D2| Got status. state: {}, rand: {}, rpt: {}.'.format(stat['state'],ran,rpt))
    buttonvar = stat['state']
    logger.debug('D2| Retrieving "cs" in getcurrsong().')
    cs = client.currentsong()
    logger.debug('D2| Got cs (client.currentsong()) with a length of {}.'.format(len(cs)))
    if cs == {}:
        client.stop()
        buttonvar = 'stop'
        artWindow(0)
        globsongtitle = "No song in the queue. Go find one."
    else:
        msg,gendtime = getendtime(cs,stat)
        logger.debug('D2| Headed to getaartpic(**cs).')
        getaartpic(**cs)
        window.update()
        if 'volume' in stat:
            lastvol = stat['volume']
            vol_int = int(lastvol)
            volbtncolor(vol_int)
            logger.info('3) Volume is {}, Random is {}, Repeat is {}.'.format(lastvol,stat['random'],stat['repeat']))
        gpstate = stat['state']
        logger.info('3) {}.'.format(msg))
        globsongtitle = msg
        if firstrun != '1' and prevbtnstate != 'stop':
            if msg != confparse.get('serverstats','lastsongtitle'):
                gsent = 0
                logger.info("4) This is a new title. Writing title to mmc4w.ini.")
                confparse.set("serverstats","lastsongtitle",str(msg))
                with open(mmc4wIni, 'w') as SLcnf:
                    confparse.write(SLcnf)
            else:
                logger.info("4) This title is still playing or just finished. Modifying endtime based on dur-elap.")
                gendtime = time.time() + (float(dur)-float(elap))
                gsent = 0
                logger.info("5) gendtime returned to {}. Remaining is {}.".format(gendtime,(float(cs['duration'])-float(elap))))
                if float(cs['duration']) == 0.00:
                    next()
        else:
            logger.info("4) This is the last song you played during your last session.")
        logger.debug('D7| lastvol: {}, gendtime: {}, gpstate: {}, gsent {}.'.format(lastvol,gendtime,gpstate,gsent))
        endtime = gendtime
        pstate = gpstate
        sent = gsent
        prevbtnstate = 'play'
        if threading.active_count() < 2:
            logger.debug("D10| The threading.active_count() dropped below 2. Quitting.")
            exit()
        if pstate == 'stop' or pstate == 'pause':
            logger.info("6) pstate: {}.".format(pstate))
        if cxstat == 0:
            globsongtitle = "Not Connected."
    return cs
#
#
def getendtime(cs,stat):
    global dur,elap
    msg = ""
    dur = cs['duration']
    trk = cs['track'].zfill(2)
    if 'elapsed' in stat:
        elap = stat['elapsed']
    else:
        elap = 0
    remaining = float(dur) - float(elap)
    gendtime = time.time() + remaining
    logger.info('1) endtime generated: {}. Length: {}, Song dur: {}, Elapsed: {}.'.format(gendtime,int(gendtime - time.time()),dur,elap))
    msg = str(trk + '-' + cs["title"] + " - " + cs["artist"])
    return msg,gendtime
#
#
def getaartpic(**cs):
    global aatgl,aartvar
    aadict = {}
    aadict = client.readpicture(cs['file'],0)
    if len(aadict) > 0:
        size = int(aadict['size'])
        done = int(aadict['binary'])
        with open(path_to_dat + '/cover.png', 'wb') as cover:
            cover.write(aadict['data'])
            while size > done:
                aadict = client.readpicture(cs['file'],done)
                done += int(aadict['binary'])
                cover.write(aadict['data'])
        logger.debug('D6| Wrote {} bytes to cover.png.  len(aadict) is: {}'.format(done,len(aadict)))
        aartvar = 1
        try:
            artw.title()
            artw.destroy()
        except (AttributeError,NameError,TclError):
            pass
    else:
        aartvar = 0
    if aatgl == '1':
        logger.info('2) Bottom of getaartpic(). Headed to artWindow(). aartvar is {}, len(aadict) is {}.'.format(aartvar,len(aadict)))
        artWindow(aartvar)
    else:
        logger.debug('D6| aartvar is: {}, len(aadict): {}.'.format(aartvar,len(aadict)))
#
## songtitlefollower() is the threaded timer.
#
def songtitlefollower():
    logger.info("     -----======<<<<  STARTING UP  >>>>======-----")
    logger.info(" ")
    logger.info("---=== Start songtitlefollower() threaded timer. ===---")
    logger.info(" ")
    global endtime,sent,pstate,pstart,pause_duration,eptime,elap
    sent = 0
    eptime = 0
    pstate = 'stop'
    thisendtime = endtime
    while True:
        if threading.active_count() > 2:
            logger.info("There are {} threads now.".format(threading.active_count()))
        sleep(.2)
        if pstate != 'stop' and pstate != 'pause':
            if endtime != thisendtime:
                logger.info("5) Threaded timer got new endtime.")
                thisendtime = endtime
                logger.info("6) New endtime: {}, Length: {}. sent: {}.".format(thisendtime,int(thisendtime - time.time()),sent))
            if thisendtime <= time.time() and sent == 0:
                logger.info("0) Threaded timer ran down. Getting new current song data.")
                sent = 1
                logger.debug("D0| time.time() reached endtime. Calling getcurrsong().")
                logger.info(" - - - - -  songtitlefollower - - - - - - ")
                getcurrsong()

def configurator():
    proceed = messagebox.askokcancel("Edit Config File","OK closes the app and opens mmc4w.ini for editing.")
    if proceed == True:
        os.startfile(mmc4wIni)
        sleep(1)
        exit()

def logtoggler():
    confparse.read(mmc4wIni)
    logtog = confparse.get("program","logging")
    if logtog.upper() == "ON":
        confparse.set('program','logging','off')
        msg = 'Logging turned OFF.'
    elif logtog.upper() == 'OFF':
        confparse.set('program','logging','on')
        msg = 'Logging turned ON.'
    logger.debug("{}. Wrote to .ini file.".format(msg))
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    displaytext1(msg)

def getcurrstat():
    global buttonvar,lastpl
    connext()
    try:
        cstat = client.status()
    except musicpd.ProtocolError as mproterr:
        logger.info('Caught a ProtocolError at getcurrstat().')
        cstat = {}
        connext()
        cstat = client.status()
    buttonvar = cstat["state"]
    logger.debug("getcurrstat() buttonvar: {}".format(buttonvar))
    msg = str("Server: " + serverip[-3:] +" | " + buttonvar + " | PlayList: " + lastpl)
    return msg,buttonvar,lastpl

def plupdate():
    global lastpl,firstrun
    connext()
    cpl = client.listplaylists()
    pl = ""
    for plv in cpl:
        pl = plv['playlist'] + "," + pl
    confparse.read(mmc4wIni)
    lastpl = confparse.get("serverstats","lastsetpl")
    confparse.set("serverstats","playlists",str(pl))
    if lastpl == '':
        confparse.set('serverstats','lastsetpl',cpl[0]['playlist'])
        lastpl = 'Select a saved playlist. "Look" menu.'
    if firstrun == '1':
        confparse.set('basic','firstrun','0')
        firstrun = '0'
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def displaytext1(msg):
    text1.delete("1.0", 'end')
    text1.insert("1.0", msg)

def displaytext2(msg2):
    text1.insert(END, msg2)

def albarttoggle():
    global aatgl,artw,aartvar
    connext()
    confparse.read(mmc4wIni)
    aatgl = confparse.get("albumart","albarttoggle")
    if aatgl == '1':
        try:
            # logger.info("Destroy AArt window.")
            artw.title()
            artw.destroy()
            aatgl = '0'
        except (AttributeError,NameError):
            pass
    else:
        # logger.info("Set aatgl to '1'.")
        aatgl = '1'
        try:
            cs = client.currentsong()
            aadict = client.readpicture(cs['file'],0)
            if len(aadict) > 0:
                aartvar = 1
            else:
                aartvar = 0
            artWindow(aartvar)
        except (ValueError,KeyError):
            pass
    confparse.set("albumart","albarttoggle",aatgl)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def tbtoggle():
    global aatgl
    if aatgl == '1':
        argeo = artw.geometry()
        argeo = argeo.replace('x',' ')
        argeo = argeo.replace('+',' ')
        argeo = argeo.split()
    wingeo = window.geometry()
    wingeo = wingeo.replace('x',' ')
    wingeo = wingeo.replace('+',' ')
    wingeo = wingeo.split()
    x_Left = int(window.winfo_screenwidth())
    y_Top = int(window.winfo_screenheight())
    if aatgl == '1':
        xarw = int(x_Left)-int(argeo[2])
        yarw = int(y_Top)-int(argeo[3])
    xwndw = int(x_Left)-int(wingeo[2])
    ywndw = int(y_Top)-int(wingeo[3])
    if aatgl == '1':
        confparse.set("albumart","aartwin_x",str(xarw))
        confparse.set("albumart","aartwin_y",str(yarw))
    confparse.set("mainwindow","win_x",str(xwndw))
    confparse.set("mainwindow","win_y",str(ywndw))
    tbstatus = window.overrideredirect()
    if tbstatus == None or tbstatus == False:
        window.overrideredirect(1)
        if aatgl == '1':
            artw.overrideredirect(1)
        confparse.set("mainwindow","titlebarstatus",'0')  # Titlebar off (overridden)
    else:
        window.overrideredirect(0)
        if aatgl == '1':
            artw.overrideredirect(0)
        confparse.set("mainwindow","titlebarstatus",'1')  # Titlebar on (not overridden)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    getcurrsong()

def returntoPL():
    global lastpl
    connext()
    confparse.read(mmc4wIni)
    lastpl = confparse.get("serverstats","lastsetpl")
    client.clear()
    try:
        client.load(lastpl)
    except musicpd.CommandError:
        logger.info('R2PL) The last playlist loaded is not available. Select new one.')
        PLSelWindow()

def resetwins():
    confparse.read(mmc4wIni)
    aartwin_x = confparse.get("default_values","aartwin_x")
    aartwin_y = confparse.get("default_values","aartwin_y")
    artwinwd = confparse.get("default_values","artwinwd")
    artwinht = confparse.get("default_values","artwinht")
    win_x = confparse.get("default_values","win_x")
    win_y = confparse.get("default_values","win_y")
    confparse.set("mainwindow","win_x",win_x)
    confparse.set("mainwindow","win_y",win_y)
    confparse.set("albumart","aartwin_x",aartwin_x)
    confparse.set("albumart","aartwin_y",aartwin_y)
    confparse.set("albumart","artwinwd",artwinwd)
    confparse.set("albumart","artwinht",artwinht)
    logger.info('Reset window positions to defaults from mmc4w.ini file.')
    logger.debug('D15| aartwin: {}x{}, main: {}x{}.'.format(aartwin_x,aartwin_y,win_x,win_y))
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    exit()

def nonstdport():
    messagebox.showinfo("Setting a non-standard port","Set your non-standard port by editing the mmc4w.ini file. Use the Configure option in the File menu.\n\nPut your port number in the 'serverport' attribute under the [basic] section. 6600 is the default MPD port.")

def endWithError(msg):
    messagebox.showinfo("UhOh",msg)
    sys.exit()

def exit():
    if confparse.get('program','buildmode') == '1':
        buildpl()
    logger.info("EXIT) Connections closed. Playback not affected. Quitting.")
    sys.exit()


client.timeout = None                     # network timeout in seconds (floats allowed), default: None
client.idletimeout = None               # timeout for fetching the result of the idle command is handled seperately, default: None
artw = None
globsongtitle = ""
aatgl = '0'

def makeeverything():
    connext()
    client.clear()
    pllist = client.listplaylists()
    if 'Everything' in str(pllist):
        client.rm('Everything')
    client.add('/')
    client.save('Everything')
    logger.info('The playlist named "Everything" was just updated.')
    PLSelWindow()
#
##
#
def deletecurrent():
    connext()
    ret = client.listplaylistinfo(lastpl)
    cs = client.currentsong()
    for x in enumerate(ret):
        if x[1]['title'] == cs['title']:
            yeah = x[0]
            doublecheck = messagebox.askyesno(message='Are you sure you want to delete \n"{}" from \n{}?'.format(cs['title'],lastpl))
            if doublecheck == True:
                logger.info('DELCUR) Deleting {}, song number {} from {}.'.format(cs['title'],yeah,lastpl))
                client.playlistdelete(lastpl,yeah)
#
## A CLASS TO CREATE ERROR MESSAGEBOXES (USED VERBATIM FROM STACKOVERFLOW)
## https://stackoverflow.com/questions/6666882/tkinter-python-catching-exceptions
#
class FaultTolerantTk(tk.Tk):
    def report_callback_exception(self, exc, val, tb):
        self.destroy_unmapped_children(self)
        messagebox.showerror('Error', val)

    # NOTE: It's an optional method. Add one if you have multiple windows to open
    def destroy_unmapped_children(self, parent):
        """
        Destroys unmapped windows (empty gray ones which got an error during initialization)
        recursively from bottom (root window) to top (last opened window).
        """
        children = parent.children.copy()
        for index, child in children.items():
            if not child.winfo_ismapped():
                parent.children.pop(index).destroy()
            else:
                self.destroy_unmapped_children(child)
#
##  END ERROR MESSAGEBOX SECTION
#
## WRAP UP AND DISPLAY ==========================================================================================
#
##  THIS IS THE 'ROOT' WINDOW.  IT IS NAMED 'window' rather than 'root'.  ##
# window = FaultTolerantTk()  # Create the root window with abbreviated error messages in popup.
window = Tk()  # Create the root window with errors in console, invisible to Windows.
window.title("Minimal MPD Client " + version)  # Set window title
winWd = 380  # Set window size
winHt = 80
confparse.read(mmc4wIni)  # get parameters from config .ini file.
win_x = int(confparse.get("mainwindow","win_x"))
win_y = int(confparse.get("mainwindow","win_y"))
tbarini = confparse.get("mainwindow","titlebarstatus")
x_Left = int(window.winfo_screenwidth() - (win_x))
y_Top = int(window.winfo_screenheight() - (win_y))
window.geometry(str(winWd) + "x" + str(winHt) + "+{}+{}".format(x_Left, y_Top))
window.config(background='white')  # Set window background color
window.columnconfigure([0,1,2,3,4], weight=0)
window.rowconfigure([0,1,2], weight=0)
if tbarini == '0':
    window.overrideredirect(1)
nnFont = Font(family="Segoe UI", size=10, weight='bold')          ## Set the base font
#
## DEFINE THE LOOKUP WINDOW AND ASSOCIATED FUNCTIONS
#
def lookupwin(lookupT):
    secfind = ''
    if lookupT == 'title':
        srchTxt = 'Title: '
        secfind = 'artist'
    if lookupT == 'album':
        srchTxt = 'Album: '
        secfind = 'artist'
    if lookupT == 'artist':
        srchTxt = 'Artist: '
        secfind = 'title'
    logger.info('Opened {} search window.'.format(lookupT))
    ##
    ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
    def clickedit(event):
        global lastpl
        connext()
        i = listbx.curselection()[0]
        if lookupT == 'album':
            albsngs = client.search(lookupT,str(itemsraw[i]['album']))
            ## We turn rePeat and Random mode off for albums. ##
            client.repeat(0)
            rstat = client.status()['random']
            if rstat == '1':
                client.random(0)
                text1['bg']='navy'  # True Blue album mode
                text1['fg']='white' # Random mode
            client.clear()
            for s in albsngs:
                client.add(s['file'])
            play()
        else:
            client.repeat(0)
            client.clear()
            client.add(itemsraw[i]['file'])
            logger.info('Repeat turned OFF, queue cleared, added {}.'.format(itemsraw[i]['file']))
            play()
        plsngwin.update()
        plsngwin.destroy()
    ##
    ## The tk.Entry box runs this upon <Return>
    def pushret(event):
        connext()
        dispitems = []
        srchterm = editing_item.get().replace('Search: ','')
        editing_item.set('Search: ')
        if srchterm == 'status':
            stats = client.status()
            for s,v in stats.items():
                dispitems.append(s + ' : ' + v)
            for i in dispitems:
                listbx.insert(END,i)
            plsngwin.update()
        if srchterm == 'stats':
            stats = client.stats()
            for s,v in stats.items():
                if s == 'uptime' or s == 'playtime' or s == 'db_playtime':
                    v = int(v)
                    v = time.strftime("%H:%M:%S", time.gmtime(v))
                if s == 'db_update':
                    v = int(v)
                    v = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(v))
                dispitems.append(s + ' : ' + v)
            for i in dispitems:
                listbx.insert(END,i)
            plsngwin.update()
        if srchterm != 'status' and srchterm != 'stats':
            findit = client.search(lookupT,srchterm)
            lastf = ''
            for f in findit:
                thisf = '"'+f[lookupT] + ' - ' + f[secfind] + ' | ' + f['album']+'"'
                thisfrec = dict([('song',thisf), ('file',f['file']),('album',f['album'])])
                if lookupT == 'album':
                    if f[lookupT] != lastf:
                        itemsraw.append(thisfrec)
                        lastf = f[lookupT]
                else:
                    itemsraw.append(thisfrec)
            for sng in itemsraw:
                dispitems.append(sng['song'])
            for i in dispitems:
                listbx.insert(END,i)
            plsngwin.update()
            if srchterm == 'quit;':
                plsngwin.destroy()
    ##
    ## FUNCTION DEFINITIONS DONE - NOW DO THE GUI STUFF
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    swin_x = int(confparse.get("searchwin","swin_x"))
    swin_y = int(confparse.get("searchwin","swin_y"))
    plsngwin = Toplevel(window)
    plsngwin.title("Search & Play " + srchTxt)
    plsngwin.configure(bg='black')
    plsngwin_x=200
    plsngwin_y=200
    plsngwin_xpos = str(int(plsngwin.winfo_screenwidth()- (plsngwin_x + swin_x)))
    plsngwin_ypos = str(int(plsngwin.winfo_screenheight()-(plsngwin_y + swin_y)))
    plsngwin.geometry('300x300+' + plsngwin_xpos + '+' +  plsngwin_ypos)
    plsngwin.columnconfigure([0,1,2,3,4],weight=1)
    plsngwin.rowconfigure([0,1,2,3,4,5,6],weight=1)
    plsngwin.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    itemsraw = []
    dispitems = []
    ## Feeds into update()
    listbx = tk.Listbox(plsngwin)
    listbx.configure(bg='black',fg='white')
    listbx.grid(column=0,row=0,rowspan=6, padx=5,pady=5,sticky='NSEW')
    listbx.bind('<<ListboxSelect>>', clickedit)
    ## Feeds into select()
    editing_item = tk.StringVar()
    entry = tk.Entry(plsngwin, textvariable=editing_item, width=200)
    entry.grid(row=6,column=0)
    entry.insert(0,'Search: ')
    entry.bind('<Return>', pushret)
    if aatgl == '1':
        artWindow(aartvar)
        #
## DEFINE THE ADD-SONG-TO-PLAYLIST WINDOW
#
def addtopl(plaction):

    ##
    ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
    def plclickedit(event):
        global lastpl
        selectlst = listbx.curselection()[0]
        connext()
        if plaction == 'add':
            cs = client.currentsong()
            client.playlistadd(pllist[selectlst],cs['file'])
            logger.info('A2PL) Added {} to {}.'.format(cs['title'],pllist[selectlst]))
        if plaction == 'remove':
            client.rm(pllist[selectlst])
            logger.info('RMPL) Playlist "{}" removed.'.format(pllist[selectlst]))
        a2plwin.update()
        a2plwin.destroy()
    def songlistclick(event):
        songsel = listbx.curselection()[0]
        logger.debug('ATPL) Playlist "{}" was listed in addtopl().'.format(lastpl))
        logger.debug('ATPL) "{}" was selected to play.'.format(songlist[songsel].split('/')[2]))
        connext()
        client.play(songsel)
        cs = getcurrsong()
        # getcurrsong()
        a2plwin.destroy()
        # addtopl('list')
    ## FUNCTION DEFINITIONS DONE - NOW DO THE GUI STUFF
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    swin_x = int(confparse.get("searchwin","swin_x"))
    swin_y = int(confparse.get("searchwin","swin_y"))
    a2plwin = Toplevel(window)
    if plaction == 'list':
        a2plwin.title("List {} - Play Selected".format(lastpl))
    if plaction == 'add':
        a2plwin.title("Add Current Song to Playlist")
    if plaction == 'remove':
        a2plwin.title("Delete the Selected Playlist")
    a2plwin.configure(bg='black')
    a2plwin_x=200
    a2plwin_y=200
    a2plwin_xpos = str(int(a2plwin.winfo_screenwidth()- (a2plwin_x + swin_x)))
    a2plwin_ypos = str(int(a2plwin.winfo_screenheight()-(a2plwin_y + swin_y)))
    a2plwin.geometry('300x300+' + a2plwin_xpos + '+' +  a2plwin_ypos)
    a2plwin.columnconfigure([0,1,2,3],weight=1)
    a2plwin.rowconfigure([0,1,2,3,4,5,6],weight=1)
    a2plwin.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    listbx = tk.Listbox(a2plwin)
    listbx.configure(bg='black',fg='white')
    listbx.grid(column=0,row=0,columnspan = 5, rowspan=7, padx=5,pady=5,sticky='NSEW')
    if plaction != 'list':
        listbx.bind('<<ListboxSelect>>', plclickedit)
    if plaction == 'list':
        listbx.bind('<<ListboxSelect>>', songlistclick)
    scrollbar = Scrollbar(a2plwin, orient='vertical')
    listbx.config(yscrollcommand = scrollbar.set)
    scrollbar.config(command=listbx.yview)
    scrollbar.grid(column=5,row=0, rowspan=7,sticky='NS')
    if plaction == 'add' or plaction == 'remove':
        cp.read(mmc4wIni)
        pllist = cp.getlist('serverstats','playlists')
        for lst in pllist:
            listbx.insert(END,lst)
    if plaction == 'list':
        thislist = confparse.get('serverstats','lastsetpl')
        connext()
        songlist=[]
        if thislist == 'Joined Server Queue':
            songlistq = client.playlistinfo()
            for s in songlistq:
                songlist.append(s['file'])
            logger.info('ATPL) Listed queue songs. Saved PL not known.')
        else:
            songlist = client.listplaylist(thislist)
            logger.info('ATPL) Listed songs from {}.'.format(thislist))
        for s in songlist:
            listbx.insert(END,s)
    if aatgl == '1':
        artWindow(aartvar)
#
## DEFINE THE SERVER SELECTION WINDOW
#
def SrvrWindow(swaction):
    global serverip,firstrun,lastpl
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    srvrw = Toplevel(window)
    if swaction == 'server':
        srvrw.title("Servers")
    srvrwinWd = 300
    srvrwinHt = 30
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    win_x = int(confparse.get("mainwindow","win_x"))
    win_y = int(confparse.get("mainwindow","win_y"))
    x_Left = int(window.winfo_screenwidth() - srvrwinWd - (win_x+60))
    y_Top = int(window.winfo_screenheight() - srvrwinHt - (win_y+120))
    srvrw.config(background="gray")  
    srvrw.geometry(str(srvrwinWd) + "x" + str(srvrwinHt) + "+{}+{}".format(x_Left, y_Top))
    srvrw.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    def rtnplsel(ipvar):
        global serverip,firstrun,lastpl
        client.close()
        msg = ipvar
        displaytext1(msg)
        serverip = ipvar
        confparse.read(mmc4wIni)
        connext()
        confparse.set("serverstats","lastsrvr",ipvar)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        srvrw.destroy()
        logger.debug("serverip: {}".format(serverip))
        lastpl = 'Joined Server Queue'
        confparse.set('serverstats','lastsetpl',lastpl)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        logger.info('0) Connected to server {}.'.format(serverip))
        getcurrsong()
    #
    def outputtggl(outputvar):
        oid = outputvar[4:5]
        client.toggleoutput(oid)
        logger.info('0) Output [{}] toggled to opposite state.'.format(outputvar))
        srvrw.destroy()
    #
    if swaction == 'server':
        cp.read(mmc4wIni)
        iplist = cp.getlist('basic','serverlist')
        ipvar = StringVar(srvrw)
        ipvar.set('Currently - ' + serverip + ' - Click for dropdown list.')
        plselwin = OptionMenu(srvrw,ipvar,*iplist,command=rtnplsel)
    if swaction == 'output':
        outputs = getoutputs()[1]
        outputvar = StringVar(srvrw)
        outputvar.set('  Select Output to Toggle.  ')
        plselwin = OptionMenu(srvrw,outputvar,*outputs,command=outputtggl)
    plselwin.config(width=44)
    plselwin.grid(column=1,row=1,sticky='EW')
#
## DEFINE THE PLAYLIST SELECTION WINDOW
#
def PLSelWindow():
    global serverip,lastpl, aartvar,aatgl
    plupdate()
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    sw = Toplevel(window)
    sw.title("PlayLists")
    swinWd = 300
    swinHt = 30
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    win_x = int(confparse.get("mainwindow","win_x"))
    win_y = int(confparse.get("mainwindow","win_y"))
    x_Left = int(window.winfo_screenwidth() - swinWd - (win_x+60))
    y_Top = int(window.winfo_screenheight() - swinHt - (win_y+120))
    sw.config(background="white")  
    sw.geometry(str(swinWd) + "x" + str(swinHt) + "+{}+{}".format(x_Left, y_Top))
    sw.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    def rtnplsel(plvar):
        global serverip,lastpl
        displaytext1(plvar)
        logger.info('PLSel) Set playlist to "{}".'.format(plvar))
        client.clear()
        client.load(plvar)
        confparse.read(mmc4wIni)
        confparse.set("serverstats","lastsetpl",plvar)
        # confparse.set("serverstats","lookuppl",'0')
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        lastpl = plvar
        sw.destroy()
        sleep(1)
    cp.read(mmc4wIni)
    pllist = cp.getlist('serverstats','playlists')
    lastpl = confparse.get("serverstats","lastsetpl")
    plvar =StringVar(sw)
    plvar.set('Current Playlist - ' + lastpl + ' - Click for list.')
    plselwin = OptionMenu(sw,plvar,*pllist,command=rtnplsel)
    plselwin.config(width=44)
    plselwin.grid(column=1,row=1)
    window.update()
    window.update_idletasks()
    if aatgl == '1':
        artWindow(aartvar)
#
## DEFINE THE ABOUT WINDOW
#
def aboutWindow():
    aw = Toplevel(window)
    aw.title("About MMC4W")
    awinWd = 400  # Set window size and albumart
    awinHt = 400
    x_Left = int(window.winfo_screenwidth() / 2 - awinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - awinHt / 2)
    aw.config(background="white")  # Set window background color
    aw.geometry(str(awinWd) + "x" + str(awinHt) + "+{}+{}".format(x_Left, y_Top))
    # aw.iconbitmap(path_to_dat + './_internal/ico/mmc4w-ico.ico')
    aw.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')
    awlabel = Label(aw, font=18, text ="About MMC4W " + version)
    awlabel.grid(column=0, columnspan=3, row=0, sticky="n")  # Place label in grid
    aw.columnconfigure(0, weight=1)
    aw.rowconfigure(0, weight=1)
    aboutText = Text(aw, height=20, width=170, bd=3, padx=10, pady=10, wrap=WORD, font=nnFont)
    aboutText.grid(column=0, row=1)
    aboutText.insert(INSERT, "MMC4W is installed at\n" + path_to_dat + "\n\nPutting the Music First.\n\nMMC4W is a Windows client for MPD.  It does nothing by itself, but if you have one or more MPD servers on your network, you might like this.\n\n"
                     "This little app holds forth the smallest possible GUI hiding a full set of MPD control functions. Just play the music.\n\nCopyright 2023-2024 Gregory A. Sanders\nhttps://www.drgerg.com")
#
## DEFINE THE HELP WINDOW
#
def helpWindow():
    global aatgl
    if aatgl == '1':
        albarttoggle()
    # pause()
    hw = Toplevel(window)
    hw.tk.call('tk', 'scaling', 1.0)    # This prevents the text being huge on hiDPI displays.
    hw.title("MMC4W Help")
    hwinWd = 800  # Set window size and placement
    hwinHt = 600
    x_Left = int(window.winfo_screenwidth() / 2 - hwinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - hwinHt / 2)
    hw.config(background="white")  # Set window background color
    hw.geometry(str(hwinWd) + "x" + str(hwinHt) + "+{}+{}".format(x_Left, y_Top))
    hw.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')
    hwlabel = HTMLLabel(hw, height=3, html='<h2 style="text-align: center">MMC4W Help</h2>')
    hw.columnconfigure(0, weight=1)
    hw.rowconfigure(1, weight=1)
    helpText = HTMLScrolledText(hw, padx=10, pady=10, html=RenderHTML(path_to_dat + "\\mmc4w_help.html"))
    hwlabel.grid(column=0, row=0, sticky="NSEW")  # Place label in grid
    helpText.grid(column=0, row=1, ipadx=10, ipady=10, sticky="NSEW")
#
## DEFINE THE ART WINDOW
#
def artWindow(aartvar):
    global artw,tbarini
    tbarini = confparse.get("mainwindow","titlebarstatus")
    if aartvar == 1:
        thisimage = (path_to_dat + '/cover.png')
    if aartvar == 0:
        thisimage = path_to_dat + '/ico/mmc4w.png'
    artw = Toplevel(window)
    artw.title("AlbumArt")
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    aartwin_x = int(confparse.get("albumart","aartwin_x"))
    aartwin_y = int(confparse.get("albumart","aartwin_y"))
    artwinWd = int(confparse.get("albumart","artwinWd"))
    artwinHt = int(confparse.get("albumart","artwinHt"))
    x_Left = int(window.winfo_screenwidth() - aartwin_x)
    y_Top = int(window.winfo_screenheight() - aartwin_y)
    artw.config(background="white")  # Set window background color
    artw.geometry(str(artwinWd) + "x" + str(artwinHt) + "+{}+{}".format(x_Left, y_Top))
    artw.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')
    artw.columnconfigure([0,1,2], weight=1)
    artw.rowconfigure(0, weight=1)
    artw.rowconfigure(1, weight=1)
    aart = Image.open(thisimage)
    aart = aart.resize((100,100))
    aart = ImageTk.PhotoImage(aart)
    aart.image = aart  # required for some reason
    aartLabel = Label(artw,image=aart)
    aartLabel.grid(column=0, row=0, padx=5, pady=5)

    if tbarini == '0':
        artw.overrideredirect(1)
    artw.update()
#
## DEFINE BUILD PLAYLIST MODE
#
def buildpl():
    confparse.read(mmc4wIni)
    bpltgl = confparse.get('program','buildmode')
    if bpltgl == '0':  ## If zero (OFF), set to ON and set up for ON.
        confparse.set('program','buildmode','1')
        button_load.configure(text='Add', bg='green', fg='white', command=lambda: addtopl('add'))
        button_tbtog.configure(text='Delete', bg='red', fg='white',command=deletecurrent)
        logger.debug('BPM) PL Build Mode turned ON.') 
    else:
        confparse.set('program','buildmode','0')
        button_load.configure(text='Art', bg='SystemButtonFace', fg='black', command=albarttoggle)
        button_tbtog.configure(text="Mode", bg='SystemButtonFace', fg='black', command=tbtoggle)
        logger.debug('BPM) PL Build Mode turned OFF.') 
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    window.update()
#
## CREATE NEW SAVED PLAYLIST
#
def createnewpl():
    global aartvar,aatgl
    connext()
    artw.destroy()
    newpl = simpledialog.askstring('Playlist Name','Name the New Playlist',parent=window)
    if newpl > "":
        client.clear()
        client.save(newpl)
        PLSelWindow()
        logger.info('NPL) A new saved Playlist named {} was created.'.format(newpl))
#
def browserplayer():
    global buttonvar
    outputsraw = getoutputs()[0]
    thisurl = ''
    for thisop in outputsraw:
        if thisop['plugin'] == 'httpd':
            if thisop['outputenabled'] == '1':
                thisport = confparse.get('serverstats','httpport')
                thisurl = str('http://' + serverip + ':' + thisport)
            else:
                messagebox.showinfo('MMC4W BrowserPlayer','The http output is not enabled.')
    if 'httpd' not in str(outputsraw):
        messagebox.showinfo('MMC4W BrowserPlayer','There is no http output configured on this server.')
    if thisurl > '':
        if buttonvar == 'play':
            webbrowser.open_new(thisurl)
            logger.info('BP) A call to the default browser was made. Music should play.')
        else:
            messagebox.showinfo('MMC4W BrowserPlayer','Press Play before starting BrowserPlayer.')

#
## MENU AND MENU ITEMS
#
Frame(window)
menu = Menu(window)
window.config(menu=menu)
nnFont = Font(family="Segoe UI", size=10)          ## Set the base font
fileMenu = Menu(menu, tearoff=False)
fileMenu.add_command(label="Configure", command=configurator)
fileMenu.add_command(label="Select a Server", command=lambda: SrvrWindow('server'))
fileMenu.add_command(label="Toggle an Output", command=lambda: SrvrWindow('output'))
fileMenu.add_command(label='Toggle Logging', command=logtoggler)
fileMenu.add_command(label='Reset Win Positions', command=resetwins)
fileMenu.add_command(label='Create New Saved Playlist', command=createnewpl)
fileMenu.add_command(label='Remove Saved Playlist',command=lambda: addtopl('remove'))
fileMenu.add_command(label="Exit", command=exit)
menu.add_cascade(label="File", menu=fileMenu)

toolMenu = Menu(menu, tearoff=False)
toolMenu.add_command(label="Reload Current Title", command=getcurrsong)
toolMenu.add_command(label="Turn Random On", command=plrandom)
toolMenu.add_command(label="Turn Random Off", command=plnotrandom)
toolMenu.add_command(label="Toggle Repeat", command=toglrepeat)
toolMenu.add_command(label="Toggle Consume", command=toglconsume)
toolMenu.add_command(label="Toggle Single", command=toglsingle)
toolMenu.add_command(label="Toggle Titlebar", command=tbtoggle)
toolMenu.add_command(label="Set Non-Standard Port", command=nonstdport)
menu.add_cascade(label="Tools", menu=toolMenu)

lookMenu = Menu(menu, tearoff=False)
lookMenu.add_command(label='Play a Single',command=lambda: lookupwin('title'))
lookMenu.add_command(label='Play an Album',command=lambda: lookupwin('album'))
lookMenu.add_command(label='Find by Artist',command=lambda: lookupwin('artist'))
lookMenu.add_command(label='Reload Last Playlist',command=returntoPL)
lookMenu.add_command(label='Show Songs in Last Playlist', command=lambda: addtopl('list'))
lookMenu.add_command(label="Select a Playlist", command=PLSelWindow)
lookMenu.add_command(label='Update "Everything" Playlist', command=makeeverything)
lookMenu.add_command(label="Toggle PL Build Mode", command=buildpl)
lookMenu.add_command(label="Launch Browser Player", command=browserplayer)
menu.add_cascade(label="Look", menu=lookMenu)

helpMenu = Menu(menu, tearoff=False)
helpMenu.add_command(label="Help", command=helpWindow)
helpMenu.add_command(label="About", command=aboutWindow)
menu.add_cascade(label="Help", menu=helpMenu)

window.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')

## Set up text window
text1 = Text(window, height=1, width=52, wrap=WORD, font=nnFont)
text1.grid(column=0, columnspan=5, row=0, padx=5)
#
# Define buttons
button_volup = tk.Button(window, width=9, text="Vol +", font=nnFont, command=volup)                  # 
button_volup.grid(column=0, sticky='E', row=1, padx=1)                     # Place button in grid

button_voldn = tk.Button(window, width=9, text="Vol -", font=nnFont, command=voldn)                  # 
button_voldn.grid(column=1, sticky='W', row=1, padx=1)                     # Place button in grid

button_play = tk.Button(window, width=9, text="Play", font=nnFont, command=play)                  # 
button_play.grid(column=0, sticky='E', row=2, padx=1)                     # Place button in grid

button_stop = tk.Button(window, width=9, text="Stop", font=nnFont, command=halt)                  # 
button_stop.grid(column=1, sticky='W', row=2, padx=1)                     # Place button in grid

button_prev = tk.Button(window, width=9, text="Prev", font=nnFont, command=previous)                  # 
button_prev.grid(column=2, sticky='W', row=2, padx=1)                     # Place button in grid

button_pause = tk.Button(window, width=9, text="Pause", font=nnFont, command=pause)                  # 
button_pause.grid(column=3, sticky='W', row=2, padx=1)                     # Place button in grid

button_next = tk.Button(window, width=9, text="Next", font=nnFont, command=next)                  # 
button_next.grid(column=4, sticky='W', row=2, padx=1)                     # Place button in grid

button_tbtog = tk.Button(window, width=9, text="Mode", font=nnFont, command=tbtoggle)                  # 
button_tbtog.grid(column=2, sticky='W', row=1, padx=1)                     # Place button in grid

button_load = tk.Button(window, width=9, text="Art", font=nnFont, command=albarttoggle)                  #
button_load.grid(column=3, sticky='W', row=1, padx=1)                     # Place button in grid

button_exit = tk.Button(window, width=9, text="Quit", font=nnFont, command=exit)                  #
button_exit.grid(column=4, sticky='W', row=1, padx=1)                     # Place button in grid

## THREADING NOTES =========================================
# while threading.active_count() > 0:
# Make all threads daemon threads, and whenever the main thread dies all threads will die with it.
## END THREADING NOTES =====================================
#
t1 = threading.Thread(target=songtitlefollower)
t1.daemon = True
t1.start()
#
confparse.read(mmc4wIni)
aatgl = confparse.get("albumart","albarttoggle")
abp = confparse.get('program','autobrowserplayer')
evenodd = 1
songused = 0
###
# lastpl is "Last Playlist". dur is "Song Duration". eptime is "Elasped Pause Time".
###
def threesecdisplaytext():
    global evenodd, globsongtitle,buttonvar,lastpl,endtime,dur,eptime,ran,rpt,sin,con
    def eo1():
        global evenodd, globsongtitle
        if evenodd == 1:
            msg = globsongtitle
            evenodd = 2
            displaytext1(msg)
    def eo2():
        global evenodd,buttonvar,dur,endtime,songused
        songlen = dur[:3]
        if buttonvar != 'stop' and buttonvar != 'pause':
            songused = float(dur) - (endtime - time.time())
            if songused >= float(songlen):
                songused = float(songlen)
            songused = str(int(songused))
        if buttonvar == 'pause':
            songused = songused
        if buttonvar == 'stop':
            songused = '0'
            songlen = '0'
        if evenodd == 2:
            # msg = str("Svr: " + serverip[-3:] +" | " + buttonvar + " | PL: " + lastpl)
            msg = str("S: {} | {} | {}{}{}{} | PL:{}".format(serverip[-3:],buttonvar,ran,rpt,sin,con,lastpl))
            msg2=str(' | {}/{}s.'.format(songused,songlen))
            evenodd = 1
            displaytext1(msg)
            displaytext2(msg2)
    window.after(1000,eo1)
    window.after(2500,eo2)
    window.after(3000,threesecdisplaytext)
#
## Start 
prevbtnstate = 'stop'
if firstrun == '1':
    plupdate()
    threesecdisplaytext()
else:
    threesecdisplaytext()
    getcurrsong()
    getoutputs()
    if abp == '1':
        if buttonvar == 'play':
            browserplayer()
logger.info("Down at the bottom. Firstrun: {}".format(firstrun))
window.mainloop()  # Run the (not defined with 'def') main window loop.


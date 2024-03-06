#!/usr/bin/env python3
# 
# mmc4w.py - 2024 by Gregory A. Sanders (dr.gerg@drgerg.com)
# Minimal MPD Client for Windows - basic set of controls for an MPD server.
# Take up as little space as possible to get the job done.
# mmc4w.py uses the python-musicpd library.
##

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

if sys.platform != "win32":
    import subprocess

version = "v2.0.4"
# v2.0.4 - Doing things a better way.
# v2.0.1 - Handling the queue.
# v2.0.0 - Introduced classes for some windows. Tons more stability tweaks.
# v1.0.0 - Fixed error in the fiver() function.
# v0.9.9 - tk.Scrollbars on all windows. Windows are more uniform.


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
    if os.path.isfile(path_to_dat + "/mmc4w.log"):
        os.remove(path_to_dat + '/mmc4w.log')

if logLevel == 'DEBUG':
    logging.basicConfig(
        filename=path_to_dat + "/mmc4w_DEBUG.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.DEBUG,
    )

if logLevel == 'INFO':
    logging.basicConfig(
        filename=path_to_dat + "/mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.INFO,
    )

if logLevel == 'WARNING':
    logging.basicConfig(
        filename=path_to_dat + "/mmc4w.log",
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
elap='0'
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
        if sys.platform == "win32":
            os.startfile(mmc4wIni)
        else:
            subprocess.run(["xdg-open", mmc4wIni])
        sys.exit()

if serverip == '':
    cp.read(mmc4wIni)
    iplist = cp.getlist('basic','serverlist')
    serverip = iplist[0]
    confparse.set('serverstats','lastsrvr',serverip)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    messagebox.showinfo("Server Set","Current server is set to\n" + serverip)

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

tsbinidict = {} # for search windows
tsbinidict['sw_x'] = int(confparse.get("searchwin","swin_x"))
tsbinidict['sw_y'] = int(confparse.get("searchwin","swin_y"))
tsbinidict['swht'] = int(confparse.get("searchwin","swinht"))
tsbinidict['swwd'] = int(confparse.get("searchwin","swinwd"))

artwinidict = {} # for the album art window
artwinidict['sw_x'] = int(confparse.get("albumart","aartwin_x"))
artwinidict['sw_y'] = int(confparse.get("albumart","aartwin_y"))
artwinidict['swht'] = int(confparse.get("albumart","artwinht"))
artwinidict['swwd'] = int(confparse.get("albumart","artwinwd"))

def makebplwindict():
    bplwinidict = {} # for the 'Build Playlist' window
    bplwinidict['sw_x'] = int(confparse.get("buildplwin","bplwin_x"))
    bplwinidict['sw_y'] = int(confparse.get("buildplwin","bplwin_y"))
    bplwinidict['swht'] = int(confparse.get("buildplwin","bplwinht"))
    bplwinidict['swwd'] = int(confparse.get("buildplwin","bplwinwd"))
    return bplwinidict

bplwinidict = makebplwindict()

cp.read(mmc4wIni)
pllist = cp.getlist('serverstats','playlists')
#
## ================= TOPLEVEL WINDOW CLASS DEFINITION ==========================
class TlSbWin(tk.Toplevel):  ## with Listbox and Scrollbar.
    def __init__(self, parent, title, inidict):
        tk.Toplevel.__init__(self)
        self.swin_x = inidict['sw_x']
        self.swin_y = inidict['sw_y']
        self.swinht = inidict['swht']
        self.swinwd = inidict['swwd']
        self.title(title)
        self.configure(bg='black')
        srchwin_xpos = str(int(self.winfo_screenwidth() - self.swin_x))
        srchwin_ypos = str(int(self.winfo_screenheight() - self.swin_y))
        geometrystring = str(self.swinwd) + 'x'+ str(self.swinht) + '+' + srchwin_xpos + '+' +  srchwin_ypos
        self.geometry(geometrystring)
        self.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico')
        # self.iconphoto(False, iconpng)
        self.columnconfigure([0,1,2,3],weight=1)
        self.rowconfigure([0,1,2,3,4,5],weight=1)
        self.rowconfigure(6,weight=0)
        self.listvar = tk.StringVar()
        self.listbx = tk.Listbox(self,listvariable=self.listvar)
        self.listbx.configure(bg='black',fg='white')
        self.listbx.grid(column=0,row=0,columnspan=4,rowspan=6,sticky='NSEW')
        scrollbar = tk.Scrollbar(self, orient='vertical')
        self.listbx.config(yscrollcommand = scrollbar.set)
        scrollbar.config(bg='black',command=self.listbx.yview)
        scrollbar.grid(column=5,row=0,rowspan=6,sticky='NS')

class TlWin(tk.Toplevel):  ## plain - no scrollbar or listbox.
    def __init__(self, parent, title, inidict):
        tk.Toplevel.__init__(self)
        self.swin_x = inidict['sw_x']
        self.swin_y = inidict['sw_y']
        self.swinht = inidict['swht']
        self.swinwd = inidict['swwd']
        self.title(title)
        self.configure(bg='black')
        srchwin_xpos = str(int(self.winfo_screenwidth() - self.swin_x))
        srchwin_ypos = str(int(self.winfo_screenheight() - self.swin_y))
        geometrystring = str(self.swinwd) + 'x'+ str(self.swinht) + '+' + srchwin_xpos + '+' +  srchwin_ypos
        self.geometry(geometrystring)
        self.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico')
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.listvar = tk.StringVar()
        self.listbx = tk.Listbox(self,listvariable=self.listvar)
        self.listbx.configure(bg='black',fg='white')
        self.listbx.grid(column=0,row=0,sticky='NSEW')
        # self.iconphoto(False, iconpng)

class TartWin(tk.Toplevel):  ## for album art.
    def __init__(self, parent, title, artwinidict,aart):
        tk.Toplevel.__init__(self)
        self.swin_x = artwinidict['sw_x']
        self.swin_y = artwinidict['sw_y']
        self.swinht = artwinidict['swht']
        self.swinwd = artwinidict['swwd']
        self.title(title)
        self.configure(bg='black')
        srchwin_xpos = str(int(self.winfo_screenwidth() - self.swin_x))
        srchwin_ypos = str(int(self.winfo_screenheight() - self.swin_y))
        geometrystring = str(self.swinwd) + 'x'+ str(self.swinht) + '+' + srchwin_xpos + '+' +  srchwin_ypos
        self.geometry(geometrystring)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.config(bg="white")  # Set window background color
        self.aartLabel = tk.Label(self,image=aart)
        self.aartLabel.grid(column=0, row=0, padx=5, pady=5)
        self.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico') # - Windows
        # self.iconphoto(False, iconpng) # Linux

## ================  END OF CLASS DEFINITIONS ===================================

def loadplsongs(song):
    connext()
    pls_on_srvr = []
    pl_without_sng = []
    pls_on_srvr = client.listplaylists()
    for i in pls_on_srvr:
        plsongs = client.listplaylistinfo(i['playlist'])
        if song not in str(plsongs):
            pl_without_sng.append(i['playlist'])
    return pl_without_sng

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
    if buttonvar == 'pause':
        pause()
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

def pause2play():
    global pstate,endtime,pstart,buttonvar,pstart,pause_duration,dur,elap
    oldendtime = endtime
    endtime = time.time() + int(float(dur) - float(elap))
    logger.info('2) New endtime generated in pause(). Old: {}, New {}'.format(oldendtime,endtime))
    button_pause.configure(text='Pause',bg='gray90') ## 'systemButtonFace' is the magic word.
    pstate = 'play'
    buttonvar = 'play'
    pstart = 0 
    #                           ## Now client.pause() sets it to PLAY
def play2pause():
    global buttonvar,pstate,endtime,pstart
    pstart = time.time()
    buttonvar = 'pause'
    button_pause.configure(text='Resume',bg="orange")
    logger.info("0) Playback paused at {}.".format(pstart))
    pstate = 'pause'
    #                           ## Now client.pause() sets it to PAUSE

def pause():  # Pause is complicated because of time-keeping.
    global buttonvar,pstate,dur,elap
    logger.debug('Buttonvar state at button press: {}.'.format(buttonvar))
    cstat = getcurrstat()
    if buttonvar == 'pause':        ## SYSTEM WAS PAUSED
        if cstat["state"] == 'pause':
            dur = cstat['duration']
            elap = cstat['elapsed']
            pause2play()
            client.pause()
        if cstat['state'] == 'play':
            getcurrsong()
    elif buttonvar == 'play':         ## SYSTEM WAS PLAYING
        if cstat['state'] == 'pause':
            play2pause()
        if cstat["state"] == 'play':
            elap = cstat['elapsed']
            play2pause()
            connext()
            client.pause()
            # start timer here to check pstate after a time.
            if threading.active_count() < 3:
                t3 = threading.Thread(target=lambda: pausethreadtimer(cstat))
                t3.daemon = True
                t3.start()

def volup():
    global lastvol
    connext()
    vol_int = int(lastvol)
    vpre = lastvol[:]
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

def pausethreadtimer(cstat):
    global buttonvar
    songdur = float(cstat['duration'])
    songelap = float(cstat['elapsed'])
    leftover = int(songdur - songelap)
    for i in range(leftover,0,-1):
        time.sleep(1)
    logger.debug('PTT) PauseThreadedTimer ran down after {} seconds.'.format(leftover))
    getcurrsong()

def btnupdater(newstate):
    global buttonvar, endtime
    if newstate == 'pause':
        button_pause.configure(text='Pause',bg='orange')
        cstat = getcurrstat()
        ## Threaded timer during pause state.
        t2 = threading.Thread(target=lambda: pausethreadtimer(cstat))
        t2.daemon = True
        t2.start()
    if newstate == 'stop' and buttonvar == 'pause':
        button_pause.configure(bg='gray90')
        endtime = time.time()
    if newstate == 'play' and buttonvar == 'pause':
        # button_pause.configure(bg='gray90')
        pause2play()

def volbtncolor(vol_int):  # Provide visual feedback on volume buttons.
    global lastvol
    if lastvol != str(vol_int):
        connext()
        client.setvol(vol_int)
    lastvol = str(vol_int)
    logger.debug('Set volume to {}.'.format(vol_int))
    thisvol = vol_int
    upconf = ['Vol +','gray90','black']
    dnconf = ['Vol -','gray90','black']
    if thisvol == 100:
        upconf = ['100','gray13','white']
    if thisvol == 95:
        upconf = ['95','gray12','white']
    if thisvol == 90:
        upconf = ['90','AntiqueWhite4','white']
    if thisvol == 85:
        upconf = ['85','AntiqueWhite4','white']
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
        upconf = ['Vol +','gray90','black']
        dnconf = ['Vol -','gray90','black']
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
#
##  FIVER() ROUNDS VOLUME NUMBERS TO MULTIPLES OF 5.
#
def fiver(invar):  # invar should be a string of numbers: 0 - 100. Returns string.
    fivevar = ''
    firDig = ''
    secDig = ''
    if len(invar) == 1:
        secDig = invar
    elif len(invar) == 2:
        firDig = invar[:1]
        secDig = invar[1:2]
    if invar == '100':
        fivevar = invar
    zerovals = ('0','1','2')
    zeroplusvals = ('8','9')
    fivevals = ('3','4','5','6','7')
    if secDig in zerovals:
        secDig = '0'
    if secDig in zeroplusvals:
        secDig = '0'
        if firDig == '':
            firDig = '0'
        firDig = str(int(firDig) + 1)
    if secDig in fivevals:
        secDig = '5'
    if fivevar != '100':
        if firDig > "":
            fivevar = firDig + secDig
        else:
            fivevar = secDig
    return fivevar

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

def dbupdate():
    connext()
    cludrtn = client.update()
    logger.info("99) Ran client.update(). Returned {}".format(cludrtn))
#
##  DEFINE getcurrsong() - THE MOST POPULAR FUNCTION HERE.
#
def getcurrsong():
    global globsongtitle,endtime,aatgl,sent,pstate,elap,firstrun,prevbtnstate,lastvol,cxstat,buttonvar,ran,rpt,sin,con,artw
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
    newstate = stat['state']
    btnupdater(newstate)
    buttonvar = newstate
    logger.debug('D2| Retrieving "cs" in getcurrsong().')
    cs = client.currentsong()
    logger.debug('D2| Got cs (client.currentsong()) with a length of {}.'.format(len(cs)))
    if cs == {}:
        client.stop()
        buttonvar = 'stop'
        aart = artWindow(0)
        artw.aartLabel.configure(image=aart)
        globsongtitle = "No song in the queue. Go find one."
    else:
        msg,gendtime = getendtime(cs,stat)
        logger.debug('D2| Headed to getaartpic(**cs).')
        getaartpic(**cs)
        aart = artWindow(1)
        artw.aartLabel.configure(image=aart)
        if 'volume' in stat:
            lastvol = stat['volume']
            vol_fives = fiver(lastvol)
            vol_int = int(vol_fives)
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
        bpltgl = confparse.get('program','buildmode')
        if bpltgl == '1':
            pls_without_song = loadplsongs(cs['title'])
            bplwin.listbx.delete(0,tk.END)
            bplwin.listvar.set(pls_without_song)
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
    remaining = float(dur) - float(elap)
    gendtime = time.time() + remaining
    logger.info('1) endtime generated: {}. Length: {}, Song dur: {}, Elapsed: {}.'.format(gendtime,int(gendtime - time.time()),dur,elap))
    msg = str(trk + '-' + cs["title"] + " - " + cs["artist"])
    return msg,gendtime
#
#
def getaartpic(**cs):
    global aatgl,aartvar
    eadict = {}
    fadict = {}
    eadict = client.readpicture(cs['file'],0)
    if len(eadict) > 0:
        size = int(eadict['size'])
        done = int(eadict['binary'])
        with open(path_to_dat + '/cover.png', 'wb') as cover:
            cover.write(eadict['data'])
            while size > done:
                eadict = client.readpicture(cs['file'],done)
                done += int(eadict['binary'])
                cover.write(eadict['data'])
        logger.debug('D6| Wrote {} bytes to cover.png.  len(eadict) is: {}'.format(done,len(eadict)))
        aartvar = 1
    elif len(eadict) == 0:
        try:
            fadict = client.albumart(cs['file'],0)
            if len(fadict) > 0:
                received = int(fadict.get('binary'))
                size = int(fadict.get('size'))
                with open(path_to_dat + '/cover.png', 'wb') as cover:
                    cover.write(fadict.get('data'))
                    while received < size:
                        fadict = client.albumart(cs['file'], received)
                        cover.write(fadict.get('data'))
                        received += int(fadict.get('binary'))
                logger.debug('D6| Wrote {} bytes to cover.png.  len(fadict) is: {}'.format(received,len(fadict)))
                aartvar = 1
            else:
                aartvar = 0
        except musicpd.CommandError:
            aartvar = 0
            pass
    else:
        aartvar = 0
    if aatgl == '1':
        logger.info('2) Bottom of getaartpic(). Headed to artWindow(). aartvar is {}, len(eadict) is {}, len(fadict) is {}.'.format(aartvar,len(eadict),len(fadict)))
        artWindow(aartvar)
    else:
        logger.debug('D6| aartvar is: {}, len(eadict) is {}, len(fadict) is {}.'.format(aartvar,len(eadict),len(fadict)))
#
## songtitlefollower() is the threaded timer.
#
def songtitlefollower():
    logger.info("     -----======<<<<  STARTING UP  >>>>======-----")
    logger.info(" ")
    logger.info("---=== Start songtitlefollower() threaded timer. ===---")
    logger.info(" ")
    global endtime,sent,pstate,pstart,pause_duration,elap
    sent = 0
    pstate = 'stop'
    thisendtime = endtime
    while True:
        if threading.active_count() > 3:
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
        if sys.platform == "win32":
            os.startfile(mmc4wIni)
        else:
            subprocess.run(["xdg-open", mmc4wIni])
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
    # global buttonvar,lastpl
    connext()
    try:
        cstat = client.status()
    except musicpd.ProtocolError as mproterr:
        logger.info('Caught a ProtocolError at getcurrstat(): {}'.format(mproterr))
        cstat = {}
        connext()
        cstat = client.status()
    # buttonvar = cstat["state"]
    # logger.debug("getcurrstat() buttonvar: {}".format(buttonvar))
    return cstat

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
    text1.insert(tk.END, msg2)

def albarttoggle():
    global aatgl,artw,aartvar
    connext()
    confparse.read(mmc4wIni)
    aatgl = confparse.get("albumart","albarttoggle")
    if aatgl == '1':
        try:
            # logger.info("Destroy AArt window.")
            # artw.title()
            artw.destroy()
            aatgl = '0'
        except (AttributeError,NameError,tk.TclError):
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
            aart = artWindow(1)  ## artWindow now returns aart ready for use.
            artw = TartWin(window, "AlbumArt",artwinidict,aart) # new window instance.
            if tbarini == '0':
                artw.overrideredirect(True)
        except (ValueError,KeyError):
            aartvar = 0
            artWindow(aartvar)
            pass
    confparse.set("albumart","albarttoggle",aatgl)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def setbplwinstats():
    disp_x = str(window.winfo_screenwidth())
    disp_y = str(window.winfo_screenheight())
    bplwingeo = bplwin.geometry()
    bwgeo = bplwingeo.replace('x',' ')
    bwgeo = bwgeo.replace('+',' ')
    bwgeo = bwgeo.split()
    confparse.set("buildplwin","bplwin_x",str(int(disp_x)-int(bwgeo[2])))
    confparse.set("buildplwin","bplwin_y",str(int(disp_y)-int(bwgeo[3])))
    confparse.set("buildplwin","bplwinht",bwgeo[1])
    confparse.set("buildplwin","bplwinwd",bwgeo[0])
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def setWinStats():
    mainwingeo = window.geometry()
    mwgeo = mainwingeo.replace('x',' ')
    mwgeo = mwgeo.replace('+',' ')
    mwgeo = mwgeo.split()
    artwingeo = artw.geometry()
    awgeo = artwingeo.replace('x',' ')
    awgeo = awgeo.replace('+',' ')
    awgeo = awgeo.split()
    disp_x = str(window.winfo_screenwidth())
    disp_y = str(window.winfo_screenheight())
    confparse.set("mainwindow","winwd",mwgeo[0])
    confparse.set("mainwindow","winht",mwgeo[1])
    confparse.set("mainwindow","win_x",str(int(disp_x)-int(mwgeo[2])))
    confparse.set("mainwindow","win_y",str(int(disp_y)-int(mwgeo[3])))
    confparse.set("albumart","aartwin_x",str(int(disp_x)-int(awgeo[2])))
    confparse.set("albumart","aartwin_y",str(int(disp_y)-int(awgeo[3])))
    confparse.set("albumart","artwinwd",awgeo[0])
    confparse.set("albumart","artwinht",awgeo[0])
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)


def tbtoggle():
    global aatgl
    tbstatus = window.overrideredirect()
    if tbstatus == None or tbstatus == False:  # Titlebar is visible, NOT overridden.
        setWinStats()
        window.overrideredirect(1) #             Override it. Turn it OFF.
        if aatgl == '1':
            artw.overrideredirect(1)
        confparse.set("mainwindow","titlebarstatus",'0')  # Set Titlebar status off (overridden)
    else: #                               When Titlebar is NOT visible, it is overridden.
        window.overrideredirect(0) #           Disable Override. Turn titlebar ON.
        if aatgl == '1':
            artw.overrideredirect(0)
        confparse.set("mainwindow","titlebarstatus",'1')  # Set Titlebar status ON (not overridden)
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
    winHt = confparse.get("default_values","winht") # default: winWd = 380
    winWd = confparse.get("default_values","winwd") # default: winHt = 80
    confparse.set("mainwindow","winht",winHt)
    confparse.set("mainwindow","winwd",winWd)
    confparse.set("mainwindow","win_x",win_x)
    confparse.set("mainwindow","win_y",win_y)
    confparse.set("albumart","aartwin_x",aartwin_x)
    confparse.set("albumart","aartwin_y",aartwin_y)
    confparse.set("albumart","artwinwd",artwinwd)
    confparse.set("albumart","artwinht",artwinht)
    logger.info('Reset window positions & sizes to defaults from mmc4w.ini file.')
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
    cp.read(mmc4wIni)
    pllist = cp.getlist('serverstats','playlists')
    # artw.destroy()
    if lastpl in pllist:
        try:
            ret = client.listplaylistinfo(lastpl)
            cs = client.currentsong()
            for x in enumerate(ret):
                if x[1]['title'] == cs['title']:
                    yeah = x[0]
                    doublecheck = messagebox.askyesno(message='Are you sure you want to delete \n"{}" from \n{}?'.format(cs['title'],lastpl))
                    if doublecheck == True:
                        logger.info('DELCUR) Deleting {}, song number {} from {}.'.format(cs['title'],yeah,lastpl))
                        client.playlistdelete(lastpl,yeah)
        except KeyError:
            messagebox.showinfo('No Song is Playing','"Delete" removes the currently playing song\nfrom the last selected playlist.')
            pass
    else:
        messagebox.showinfo('No Playlist Selected','You have not yet selected a saved playlist.')
    if aatgl == '1':
        aart = artWindow(aartvar)  ## artWindow prepares the image, 'configs' the Label and returns image as well.
        artw.aartLabel.configure(image=aart)
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
##  tk.END ERROR MESSAGEBOX SECTION
#
## WRAP UP AND DISPLAY ==========================================================================================
#
##  THIS IS THE 'ROOT' WINDOW.  IT IS NAMED 'window' rather than 'root'.  ##
# window = FaultTolerantTk()  # Create the root window with abbreviated error messages in popup.
window = tk.Tk()  # Create the root window with errors in console, invisible to Windows.
# window.tk.call('tk', 'scaling', 1.0)    # This prevents the text being huge on hiDPI displays.
window.title("Minimal MPD Client " + version)  # Set window title
confparse.read(mmc4wIni)  # get parameters from config .ini file.
winHt = int(confparse.get("mainwindow","winht")) # default: winWd = 380
winWd = int(confparse.get("mainwindow","winwd")) # default: winHt = 80
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
main_frame = tk.Frame(window, )
main_frame.grid(column=0,row=0,padx=2)
main_frame.columnconfigure([0,1,2,3,4], weight=0)
#
## DEFINE THE QUEUE WINDOW
#
def queuewin(qwaction):
    global findit,dispitems,tsbinidict
    ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
    def qwclicked(event):
        global findit,dispitems
        connext()
        t = queuewin.listbx.curselection()[0]
        clikd = dispitems[t].split(" | ")
        for m in findit:
            if clikd[0] == m['artist'] and clikd[1] == m['title'] and clikd[2] == m['album']:
                playit = m['pos']
        # client.play(itemsraw[t]['pos'])
        client.play(playit)
        getcurrsong()
        queuewin.destroy()
    ##
    ## The tk.Entry box runs this upon <Return>
    def pushret(event):
        global findit,dispitems
        connext()
        srchterm = editing_item.get().replace('Search: ','')
        editing_item.set('Search: ')
        if srchterm != 'quit;':
            if ":" in srchterm:
                fullsearch = srchterm.split(":")
                try:
                    findit = client.playlistsearch(fullsearch[0],fullsearch[1])
                except musicpd.CommandError:
                    pass
            else:
                findit = client.playlistsearch('title',srchterm)
            dispitems = []
            for f in findit:
                thisfrec = f['artist'] + ' | ' + f['title'] + ' | ' + f['album']
                dispitems.append(thisfrec)
            queuewin.listbx.delete(0,tk.END)
            dispitems.sort()
            queuewin.listvar.set(dispitems)
        if srchterm == 'quit;':
            queuewin.destroy()
            if aatgl == '1':
                aart = artWindow(aartvar)
                artw.aartLabel.configure(image=aart)
    ##

    queuewin = TlSbWin(window, 'Search the Queue',tsbinidict)
    connext()
    dispitems = []
    findit = client.playlistinfo()
    for f in findit:
        thisfrec = f['artist'] + ' | ' + f['title'] + ' | ' + f['album']
        dispitems.append(thisfrec)
        dispitems.sort()
    queuewin.listvar.set(dispitems)
    ## Feeds into select()
    editing_item = tk.StringVar()
    entry = tk.Entry(queuewin, textvariable=editing_item, width=tsbinidict['sw_x'])
    entry.grid(row=6,column=1,columnspan=5,sticky='NSEW')
    entry.insert(0,'Search: ')
    entry.bind('<Return>', pushret)
    entry.focus_set()
    queuewin.listbx.bind('<<ListboxSelect>>', qwclicked)
    # artw.destroy()


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
        global lastpl, itemsraw
        connext()
        i = plsngwin.listbx.curselection()[0]
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
            lastpl = str(itemsraw[i]['album'])
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
        global itemsraw
        connext()
        dispitems = []
        srchterm = editing_item.get().replace('Search: ','')
        editing_item.set('Search: ')
        if srchterm == 'status':
            stats = client.status()
            for s,v in stats.items():
                dispitems.append(s + ' : ' + v)
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listvar.set(dispitems)
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
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listvar.set(dispitems)
        if srchterm != 'status' and srchterm != 'stats':
            dispitems = []
            itemsraw = []
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
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listvar.set(dispitems)
            if srchterm == 'quit;':
                plsngwin.destroy()
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    plsngwin = TlSbWin(window, 'Search & Play by ' + srchTxt, tsbinidict)
    itemsraw = []
    dispitems = []
    editing_item = tk.StringVar()
    entry = tk.Entry(plsngwin, textvariable=editing_item, width=tsbinidict['sw_x'])
    entry.grid(row=6,column=1,columnspan=5,sticky='NSEW')
    entry.insert(0,'Search: ')
    entry.bind('<Return>', pushret)
    entry.focus_set()
    plsngwin.listbx.bind('<<ListboxSelect>>', clickedit)
    # artw.destroy()
## DEFINE THE ADD-SONG-TO-PLAYLIST WINDOW
#
def addtopl(plaction):
    ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
    plupdate()
    def plclickedit(event):
        global lastpl
        selectlst = a2plwin.listbx.curselection()[0]
        pllist = cp.getlist('serverstats','playlists')
        connext()
        if plaction == 'add':
            cs = client.currentsong()
            addfile = cs['file']
            addpllist = client.listplaylist(pllist[selectlst])
            if addfile in addpllist:
                messagebox.showinfo('Song Already There','{} is already in {}.'.format(addfile.split('/')[2],pllist[selectlst]))
            else:
                client.playlistadd(pllist[selectlst],cs['file'])
                bpltgl = confparse.get('program','buildmode')
                if bpltgl == '1':
                    pls_without_song = loadplsongs(cs['title'])
                    bplwin.listbx.delete(0,tk.END)
                    bplwin.listvar.set(pls_without_song)
                logger.info('A2PL) Added {} to {}.'.format(cs['title'],pllist[selectlst]))
        if plaction == 'remove':
            pllist = cp.getlist('serverstats','playlists')
            doublecheck = messagebox.askyesno(message='Are you sure you want to PERMANENTLY delete \n"{}"?'.format(pllist[selectlst]))
            if doublecheck == True:
                client.rm(pllist[selectlst])
                logger.info('RMPL) Playlist "{}" removed.'.format(pllist[selectlst]))
                plupdate()
        a2plwin.update()
        a2plwin.destroy()
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
    def songlistclick(event):
        songsel = a2plwin.listbx.curselection()[0]
        logger.debug('ATPL) Playlist "{}" was listed in addtopl().'.format(lastpl))
        logger.debug('ATPL) "{}" was selected to play.'.format(songlist[songsel].split('/')[2]))
        connext()
        client.play(songsel)
        cs = getcurrsong()
        a2plwin.destroy()
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
    if plaction == 'list':
        a2title = "List {} - Play Selected".format(lastpl)
    if plaction == 'add':
        a2title = "Add Current Song to Playlist"
    if plaction == 'remove':
        a2title = "Delete the Selected Playlist"
    a2plwin = TlSbWin(window, a2title, tsbinidict)
    a2plwin.configure(bg='black')
    if plaction != 'list':
        a2plwin.listbx.bind('<<ListboxSelect>>', plclickedit)
    if plaction == 'list':
        a2plwin.listbx.bind('<<ListboxSelect>>', songlistclick)
    if plaction == 'add' or plaction == 'remove':
        a2plwin.listbx.bind('<<ListboxSelect>>', plclickedit)
        cp.read(mmc4wIni)
        pllist = cp.getlist('serverstats','playlists')
        for lst in pllist:
            a2plwin.listbx.insert(tk.END,lst)
    if plaction == 'list':
        a2plwin.listbx.bind('<<ListboxSelect>>', songlistclick)
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
            a2plwin.listbx.insert(tk.END,s)
#
## DEFINE THE SERVER SELECTION WINDOW
#
def SrvrWindow(swaction):
    global serverip,firstrun,lastpl
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    if swaction == 'server':
        srvrwtitle = "Servers"
    if swaction == 'output':
        srvrwtitle = "MPD Server Outputs"
    srvrw = TlSbWin(window, srvrwtitle, tsbinidict)
    def rtnplsel(ipvar):
        global serverip,firstrun,lastpl
        client.close()
        selection = srvrw.listbx.curselection()[0]
        msg = ipvar
        displaytext1(msg)
        serverip = iplist[selection]
        confparse.read(mmc4wIni)
        connext()
        confparse.set("serverstats","lastsrvr",serverip)
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
        selection = srvrw.listbx.curselection()[0]
        oid = outputs[selection][4:5]
        client.toggleoutput(oid)
        logger.info('0) Output [{}] toggled to opposite state.'.format(outputvar))
        srvrw.destroy()
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
    #
    if swaction == 'server':
        srvrw.listbx.bind('<<ListboxSelect>>', rtnplsel)
        cp.read(mmc4wIni)
        iplist = cp.getlist('basic','serverlist')
        srvrw.listbx.delete(0,tk.END)
        srvrw.listvar.set(iplist)
    if swaction == 'output':
        srvrw.listbx.bind('<<ListboxSelect>>', outputtggl)
        outputs = getoutputs()[1]
        srvrw.listbx.delete(0,tk.END)
        srvrw.listvar.set(outputs)
    # if artw.winfo_exists():
    #     artw.destroy()
#
## DEFINE THE PLAYLIST SELECTION WINDOW
#
def PLSelWindow():
    global serverip,lastpl, aartvar,aatgl,tsbinidict
    plupdate()
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    plswtitle = "PlayLists"
    plsw = TlSbWin(window, plswtitle, tsbinidict)
    def rtnplsel(plvar):
        global serverip,lastpl
        selection = plsw.listbx.curselection()[0]
        plvar = pllist[selection]
        displaytext1(plvar)
        logger.info('PLSel) Set playlist to "{}".'.format(plvar))
        loadit = messagebox.askyesno("Load Playlist Now?","Load it now?\n'No' will remember your selection\nwithout replacing the queue.")
        if loadit == True:
            client.clear()
            client.load(plvar)
        confparse.read(mmc4wIni)
        confparse.set("serverstats","lastsetpl",plvar)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        lastpl = plvar
        plsw.destroy()
        sleep(1)
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
    cp.read(mmc4wIni)
    pllist = cp.getlist('serverstats','playlists')
    lastpl = confparse.get("serverstats","lastsetpl")
    plsw.listbx.bind('<<ListboxSelect>>', rtnplsel)
    plsw.listbx.delete(0,tk.END)
    plsw.listvar.set(pllist)
    # if artw.winfo_exists():
    #     artw.destroy()
    
#
## DEFINE THE ABOUT WINDOW
#
def aboutWindow():
    aw = tk.Toplevel(window)
    aw.title("About MMC4W")
    awinWd = 400  # Set window size and albumart
    awinHt = 400
    x_Left = int(window.winfo_screenwidth() / 2 - awinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - awinHt / 2)
    aw.config(background="white")  # Set window background color
    aw.geometry(str(awinWd) + "x" + str(awinHt) + "+{}+{}".format(x_Left, y_Top))
    aw.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico')
    # aw.iconphoto(False, iconpng)
    awlabel = tk.Label(aw, font=18, text ="About MMC4W " + version)
    awlabel.grid(column=0, columnspan=3, row=0, sticky="n")  # Place label in grid
    aw.columnconfigure(0, weight=1)
    aw.rowconfigure(0, weight=1)
    aboutText = tk.Text(aw, height=20, width=170, bd=3, padx=10, pady=10, wrap=tk.WORD, font=nnFont)
    aboutText.grid(column=0, row=1)
    aboutText.insert( tk.INSERT, "MMC4W is installed at\n" + path_to_dat + "\n\nPutting the Music First.\n\nMMC4W is a Windows client for MPD.  It does nothing by itself, but if you have one or more MPD servers on your network, you might like this.\n\n"
                     "This little app holds forth the smallest possible GUI hiding a full set of MPD control functions. Just play the music.\n\nCopyright 2023-2024 Gregory A. Sanders\nhttps://www.drgerg.com")
#
## DEFINE THE HELP WINDOW
#
def helpWindow():
    global aatgl
    hw = tk.Toplevel(window)
    hw.title("MMC4W Help")
    hwinWd = 1000  # Set window size and placement
    hwinHt = int(window.winfo_screenheight() * 0.66)
    x_Left = int(window.winfo_screenwidth() / 2 - hwinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - hwinHt / 2)
    hw.config(background="white")  # Set window background color
    hw.geometry(str(hwinWd) + "x" + str(hwinHt) + "+{}+{}".format(x_Left, y_Top))
    hw.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico')
    # hw.iconphoto(False, iconpng) # Linux
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
    global tbarini,artwinidict  ## removed artw from this list.
    tbarini = confparse.get("mainwindow","titlebarstatus")
    if aartvar == 1:
        thisimage = (path_to_dat + '/cover.png')
    if aartvar == 0:
        thisimage = path_to_dat + '/ico/mmc4w.png'
    aart = Image.open(thisimage)
    aart = aart.resize((artwinidict['swht']-10,artwinidict['swwd']-10))
    aart = ImageTk.PhotoImage(aart)
    aart.image = aart  # required for some reason
    return aart
#
## DEFINE BUILD PLAYLIST MODE
#
def buildpl():
    global bplwinidict,bplwin
    confparse.read(mmc4wIni)
    bpltgl = confparse.get('program','buildmode')
    if bpltgl == '0':  ## If zero (OFF), set to ON and set up for ON.
        confparse.set('program','buildmode','1')
        button_load.configure(text='Add', bg='green', fg='white', command=lambda: addtopl('add'))
        button_tbtog.configure(text='Delete', bg='red', fg='white',command=deletecurrent)
        bplwin = TlWin(window, "Playlists Without Current Song",bplwinidict)
        logger.debug('BPM) PL Build Mode turned ON.') 
        getcurrsong()
    else:
        confparse.set('program','buildmode','0')
        button_load.configure(text='Art', bg='gray90', fg='black', command=albarttoggle)
        button_tbtog.configure(text="Mode", bg='gray90', fg='black', command=tbtoggle)
        setbplwinstats()
        if bplwin.winfo_exists():
            bplwin.destroy()
        bplwinidict = makebplwindict()
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
    # artw.destroy()
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
tk.Frame(window)
menu = tk.Menu(window)
window.config(menu=menu)
nnFont = Font(family="Segoe UI", size=10)          ## Set the base font
fileMenu = tk.Menu(menu, tearoff=False)
fileMenu.add_command(label="Configure", command=configurator)
fileMenu.add_command(label="Select a Server", command=lambda: SrvrWindow('server'))
fileMenu.add_command(label="Toggle an Output", command=lambda: SrvrWindow('output'))
fileMenu.add_command(label='Toggle Logging', command=logtoggler)
fileMenu.add_command(label='Reset Win Positions', command=resetwins)
fileMenu.add_command(label='Create New Saved Playlist', command=createnewpl)
fileMenu.add_command(label='Remove Saved Playlist',command=lambda: addtopl('remove'))
fileMenu.add_command(label="Exit", command=exit)
menu.add_cascade(label="File", menu=fileMenu)

toolMenu = tk.Menu(menu, tearoff=False)
toolMenu.add_command(label="Reload Current Title", command=getcurrsong)
toolMenu.add_command(label="Turn Random On", command=plrandom)
toolMenu.add_command(label="Turn Random Off", command=plnotrandom)
toolMenu.add_command(label="Toggle Repeat", command=toglrepeat)
toolMenu.add_command(label="Toggle Consume", command=toglconsume)
toolMenu.add_command(label="Toggle Single", command=toglsingle)
toolMenu.add_command(label="Toggle Titlebar", command=tbtoggle)
toolMenu.add_command(label="Update Database", command=dbupdate)
toolMenu.add_command(label="Set Non-Standard Port", command=nonstdport)
menu.add_cascade(label="Tools", menu=toolMenu)

lookMenu = tk.Menu(menu, tearoff=False)
lookMenu.add_command(label='Play a Single',command=lambda: lookupwin('title'))
lookMenu.add_command(label='Play an Album',command=lambda: lookupwin('album'))
lookMenu.add_command(label='Find by Artist',command=lambda: lookupwin('artist'))
lookMenu.add_command(label='Load Last Selected Playlist',command=returntoPL)
lookMenu.add_command(label='Show Songs in Last Playlist', command=lambda: addtopl('list'))
lookMenu.add_command(label="Select a Playlist", command=PLSelWindow)
lookMenu.add_command(label='Update "Everything" Playlist', command=makeeverything)
lookMenu.add_command(label="Toggle PL Build Mode", command=buildpl)
lookMenu.add_command(label="Launch Browser Player", command=browserplayer)
menu.add_cascade(label="Look", menu=lookMenu)

queueMenu = tk.Menu(menu, tearoff=False)
queueMenu.add_command(label='Find and Play',command=lambda: queuewin('title'))
menu.add_cascade(label="Queue", menu=queueMenu)

helpMenu = tk.Menu(menu, tearoff=False)
helpMenu.add_command(label="Help", command=helpWindow)
helpMenu.add_command(label="About", command=aboutWindow)
menu.add_cascade(label="Help", menu=helpMenu)

window.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico')

## Set up text window
text1 = tk.Text(main_frame, height=1, width=52, wrap= tk.WORD, font=nnFont)
text1.grid(column=0, columnspan=5, row=0, padx=5)
#
# Define buttons
button_volup = tk.Button(main_frame, bg='gray90', width=9, text="Vol +", font=nnFont, command=volup)
button_volup.grid(column=0, sticky='E', row=1, padx=1)                     # Place button in grid

button_voldn = tk.Button(main_frame, bg='gray90', width=9, text="Vol -", font=nnFont, command=voldn)
button_voldn.grid(column=1, sticky='W', row=1, padx=1)                     # Place button in grid

button_play = tk.Button(main_frame, width=9, bg='gray90', text="Play", font=nnFont, command=play)
button_play.grid(column=0, sticky='E', row=2, padx=1)                     # Place button in grid

button_stop = tk.Button(main_frame, width=9, bg='gray90', text="Stop", font=nnFont, command=halt)
button_stop.grid(column=1, sticky='W', row=2, padx=1)                     # Place button in grid

button_prev = tk.Button(main_frame, width=9, bg='gray90', text="Prev", font=nnFont, command=previous)
button_prev.grid(column=2, sticky='W', row=2, padx=1)                     # Place button in grid

button_pause = tk.Button(main_frame, width=9, bg='gray90', text="Pause", font=nnFont, command=pause)
button_pause.grid(column=3, sticky='W', row=2, padx=1)                     # Place button in grid

button_next = tk.Button(main_frame, width=9, bg='gray90', text="Next", font=nnFont, command=next)
button_next.grid(column=4, sticky='W', row=2, padx=1)                     # Place button in grid

button_tbtog = tk.Button(main_frame, width=9, bg='gray90', text="Mode", font=nnFont, command=tbtoggle)
button_tbtog.grid(column=2, sticky='W', row=1, padx=1)                     # Place button in grid

button_load = tk.Button(main_frame, width=9, bg='gray90', text="Art", font=nnFont, command=albarttoggle)
button_load.grid(column=3, sticky='W', row=1, padx=1)                     # Place button in grid

button_exit = tk.Button(main_frame, width=9, bg='gray90', text="Quit", font=nnFont, command=exit)
button_exit.grid(column=4, sticky='W', row=1, padx=1)                     # Place button in grid

## THREADING NOTES =========================================
# while threading.active_count() > 0:
# Make all threads daemon threads, and whenever the main thread dies all threads will die with it.
## tk.END THREADING NOTES =====================================
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
# lastpl is "Last Playlist". dur is "Song Duration".
###
def threesecdisplaytext():
    global evenodd, globsongtitle,buttonvar,lastpl,endtime,dur,ran,rpt,sin,con,elap
    def eo1():
        global evenodd, globsongtitle
        if evenodd == 1:
            msg = globsongtitle
            evenodd = 2
            displaytext1(msg)
    def eo2():
        global evenodd,buttonvar,dur,endtime,songused,elap
        splitdur = dur.split(".")
        songlen = splitdur[0]
        if buttonvar != 'stop' and buttonvar != 'pause':
            songused = float(dur) - (endtime - time.time())
            if songused >= float(songlen):
                songused = float(songlen)
            songused = str(int(songused))
        if buttonvar == 'pause':
            songused = int(float(elap))
            # songused = songused
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
## Do these things right before starting window.mainloop().
prevbtnstate = 'stop'
if firstrun == '1':
    plupdate()
threesecdisplaytext()
confparse.read(mmc4wIni)
bpltgl = confparse.get('program','buildmode')
if bpltgl == '1': # Just on the odd chance it crashed and left this at '1'.
    bplwin = TlWin(window, "Playlists Without Current Song",bplwinidict)
    buildpl()
aart = artWindow(1)
artw = TartWin(window, "AlbumArt",artwinidict,aart)
if tbarini == '0':
    artw.overrideredirect(True)
getcurrsong()
getoutputs()
if abp == '1':
    if buttonvar == 'play':
        browserplayer()
logger.info("Down at the bottom. Firstrun: {}".format(firstrun))
window.mainloop()  # Run the (not defined with 'def') main window loop.


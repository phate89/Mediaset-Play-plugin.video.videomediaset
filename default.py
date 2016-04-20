# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urlparse
from resources.lib.mediaset import Mediaset

# plugin constants
__plugin__ = "plugin.video.videomediaset"
__author__ = "aracnoz"

Addon = xbmcaddon.Addon(id=__plugin__)

# plugin handle
handle = int(sys.argv[1])

# utility functions
def parameters_string_to_dict(parameters):
    paramDict = dict(urlparse.parse_qsl(parameters[1:]))
    return paramDict

def pulisci_cerca(s):
    s = s.lower()
    s = s.replace("à","a")
    s = s.replace("è","e")
    s = s.replace("é","e")
    s = s.replace("ì","i")
    s = s.replace("ò","o")
    s = s.replace("ù","u")
    s = s.replace(" ","-")
    s = s.replace("'","-")
    return s

def parameters (p):
    return sys.argv[0] + '?' + urllib.urlencode(p)

def addDir (s,p):
    item = xbmcgui.ListItem(s)
    return xbmcplugin.addDirectoryItem(handle=handle, url=parameters(p), listitem=item, isFolder=True)

def addDir_ep (s,t,p):
    item = xbmcgui.ListItem("[COLOR blue]"+s+"[/COLOR]",thumbnailImage=t)
    return xbmcplugin.addDirectoryItem(handle=handle, url=parameters(p), listitem=item, isFolder=False)

def stamp_ep(ep):
    addDir_ep(ep["titolo"],ep["thumbs"],{'mode':'playMediaset','title':ep["titolo"],'stream_id':ep["id"],'thumbs':ep["thumbs"],'desc':ep["desc"]})

def stamp_live(ch):
    addDir_ep(ch["titolo"],ch["thumbs"],{'mode':'playLive','title':ch["titolo"],'stream_url':ch["url"],'thumbs':ch["thumbs"],'desc':ch["desc"]})

def endDir():
    return xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

# UI builder functions

def root():
    addDir("Canali Live",{'mode':'canali_live'})
    addDir("Elenco programmi",{'mode':'elenco_programmi'})
    addDir("Ultime puntate News",{'mode':'ultime_puntate','prog_tipo':'news'})
    addDir("Ultime puntate Sport",{'mode':'ultime_puntate','prog_tipo':'sport'})
    addDir("Ultime puntate Intrattenimento",{'mode':'ultime_puntate','prog_tipo':'intrattenimento'})
    addDir("Ultime puntate Fiction",{'mode':'ultime_puntate','prog_tipo':'fiction'})
    addDir("Ultime puntate Elenco canali",{'mode':'ultime_puntate_canali'})
    addDir("Ultime Sport Mediaset",{'mode':'sportmediaset'})
    addDir("Più visti Ieri",{'mode':'piuvisti','range_visti':'ieri'})
    addDir("Più visti Settimana",{'mode':'piuvisti','range_visti':'settimana'})
    addDir("Più visti Mese",{'mode':'piuvisti','range_visti':'mese'})
    addDir("Cerca...",{'mode':'cerca'})
    endDir()

def sportmediaset_root():
    addDir("Highlights",{'mode':'sportmediaset','progsport_tipo':'tutti_i_gol'})
    addDir("Calcio",{'mode':'sportmediaset','progsport_tipo':'calcio'})
    addDir("Champions League",{'mode':'sportmediaset','progsport_tipo':'champions_league'})
    addDir("Europa League",{'mode':'sportmediaset','progsport_tipo':'europa_league'})
    addDir("Altri sport",{'mode':'sportmediaset','progsport_tipo':'altrisport'})
    addDir("Motori",{'mode':'sportmediaset','progsport_tipo':'motori'})
    endDir()

def puntate_canali_root():
    addDir("Italia 1",{'mode':'ultime_puntate','prog_tipo':' i1 '})
    addDir("Canale 5",{'mode':'ultime_puntate','prog_tipo':' c5 '})
    addDir("Rete 4",{'mode':'ultime_puntate','prog_tipo':' r4 '})
    addDir("Italia 2",{'mode':'ultime_puntate','prog_tipo':' i2 '})
    addDir("La 5",{'mode':'ultime_puntate','prog_tipo':' ka '})
    endDir()

def canali_live_root():
    mediaset = Mediaset()
    for ch in mediaset.get_canali_live():
        stamp_live(ch)
    endDir()

def elenco_programmi_root():
    mediaset = Mediaset()
    for lettera in mediaset.get_prog_root():
        addDir(lettera["index"],{'mode':'elenco_programmi','prog_id':lettera["index"]})
    endDir()

def elenco_programmi_list(progId):
    mediaset = Mediaset()
    for lettera in mediaset.get_prog_root():
        if lettera['index'] == progId:
            for programma in lettera["program"]:    
                addDir(programma["label"],{'mode':'elenco_programmi','prog_id':lettera["index"],'prog_url':programma["url"].replace("archivio-news.shtml","archivio-video.shtml")})
    endDir()

def elenco_programmi_epList(progId,progUrl):
    mediaset = Mediaset()
    for ep in mediaset.get_prog_epList(progUrl):
        stamp_ep(ep)
    for season in mediaset.get_prog_seasonList(progUrl):
        addDir(season["titolo"],{'mode':'elenco_programmi','prog_id':progId,'prog_url':season["url"]})
    endDir()

def sportmediaset_epList(progsportTipo):
    mediaset = Mediaset()
    for ep in mediaset.get_sport_epList():
        if (ep["tipo"].lower().find(progsportTipo) > 0): stamp_ep(ep)        
    endDir()

def puntate_epList(progTipo):
    mediaset = Mediaset()
    for ep in mediaset.get_global_epList(0,0):
        if (ep["tipo"].lower().find(progTipo) > 0): stamp_ep(ep)
    endDir()

def piuvisti_epList(rangeVisti):
    mediaset = Mediaset()
    for ep in mediaset.get_global_epList(1,rangeVisti):
        stamp_ep(ep)
    endDir()

def cerca():
    kb = xbmc.Keyboard()
    kb.setHeading("Cerca un programma")
    kb.doModal()
    if kb.isConfirmed():
        text = kb.getText()
        text = pulisci_cerca(text)
        mediaset = Mediaset()
        for lettera in mediaset.get_prog_root():
            for programma in lettera["program"]:
                if (programma["mc"].find(text) > 0):
                    addDir(programma["label"],{'mode':'elenco_programmi','prog_id':lettera["index"],'prog_url':programma["url"].replace("archivio-news.shtml","archivio-video.shtml")})
    endDir()

def playMediaset(title,streamId,thumbs,desc):
    mediaset = Mediaset()
    url = mediaset.get_stream(streamId)

    # Play the item
    item=xbmcgui.ListItem(title, thumbnailImage=thumbs)
    item.setInfo(type="Video", infoLabels={"Title": title, "Plot":desc})

    if (url["mp4"] != ""): stream = url["mp4"]
    else: stream = url["wmv"]

    print "videomediaset: play %s" % stream
    xbmc.Player().play(stream,item)

def playLive(title,streamUrl,thumbs,desc):
    # Play the item
    item=xbmcgui.ListItem(title, thumbnailImage=thumbs)
    item.setInfo(type="Video", infoLabels={"Title": title, "Plot":desc})

    print "videomediaset: play %s" % streamUrl
    xbmc.Player().play(streamUrl,item)

# parameter values
params = parameters_string_to_dict(sys.argv[2])
mode = str(params.get("mode", ""))
progId = str(params.get("prog_id", ""))
progUrl = str(params.get("prog_url", ""))
progTipo = str(params.get("prog_tipo", ""))
progsportTipo = str(params.get("progsport_tipo", ""))
title = str(params.get("title", ""))
streamId = str(params.get("stream_id", ""))
streamUrl = str(params.get("stream_url", ""))
thumbs = str(params.get("thumbs", ""))
desc = str(params.get("desc", ""))
rangeVisti = str(params.get("range_visti", ""))

if mode == "canali_live":
    canali_live_root()

elif mode == "elenco_programmi":
    if progId == "":
        elenco_programmi_root()
    elif progUrl == "":
        elenco_programmi_list(progId)
    else:
        elenco_programmi_epList(progId,progUrl)

elif mode == "sportmediaset":
    if progsportTipo == "":
        sportmediaset_root()
    else:
        sportmediaset_epList(progsportTipo)

elif mode == "ultime_puntate":
    puntate_epList(progTipo)

elif mode == "ultime_puntate_canali":
    puntate_canali_root()

elif mode == "piuvisti":
    piuvisti_epList(rangeVisti)

elif mode == "cerca":
    cerca()

elif mode == "playMediaset":
    playMediaset(title, streamId, thumbs, desc)

elif mode == "playLive":
    playLive(title, streamUrl, thumbs, desc)

else:
    root()


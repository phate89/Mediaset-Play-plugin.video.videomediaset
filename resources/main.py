# -*- coding: utf-8 -*-
from datetime import timedelta
from resources.lib.mediaset import Mediaset
from resources.mediaset_datahelper import _gather_info, _gather_art, _gather_media_type
#from phate89lib import kodiutils, staticutils  # pylint: disable=import-error
from phate89lib import staticutils

#imports for kodiutils
import os
import sys
from urllib.parse import urlencode
import json
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmcvfs

ADDON = xbmcaddon.Addon()
ID = ADDON.getAddonInfo('id')
NAME = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')
PATH = ADDON.getAddonInfo('path')
DATA_PATH = ADDON.getAddonInfo('profile')
PATH_T = xbmcvfs.translatePath(PATH)
DATA_PATH_T = xbmcvfs.translatePath(DATA_PATH)
IMAGE_PATH_T = os.path.join(PATH_T, 'resources', 'media', "")
LANGUAGE = ADDON.getLocalizedString
KODILANGUAGE = xbmc.getLocalizedString

HANDLE = int(sys.argv[1])


class kodiutils:

    def executebuiltin(func, block=False):
        xbmc.executebuiltin(func, block)


    def notify(msg):
        xbmcgui.Dialog().notification(ID, msg)


    def log(msg, level=2):
        message = u'%s: %s' % (ID, msg)
        if level > 1:
            xbmc.log(msg=message, level=xbmc.LOGDEBUG)
        else:
            xbmc.log(msg=message, level=xbmc.LOGINFO)
            if level == 0:
                notify(msg)


    def py2_decode(s):
        return s


    def py2_encode(s):
        return s


    def getSetting(setting):
        return ADDON.getSetting(setting).strip()


    def getSettingAsBool(setting):
        return ADDON.getSetting(setting).strip.lower() == "true"


    def getSettingAsNum(setting):
        num = 0
        try:   
            num = float(ADDON.getSetting(setting).strip)
        except ValueError:
            pass
        return num


    def setSetting(setting, value):
        ADDON.setSetting(id=setting, value=str(value))


    def getKeyboard():
        return xbmc.Keyboard()


    def getKeyboardText(heading, default='', hidden=False):
        kb = xbmc.Keyboard(default, heading)
        kb.setHiddenInput(hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return kb.getText()
        return False


    def showOkDialog(heading, line):
        xbmcgui.Dialog().ok(heading, line)


    def createListItem(label="", params=None, label2=None, thumb=None, fanart=None, poster=None, arts=None, videoInfo=None, properties=None, isFolder=True, path=None, subs=None):
        if arts is None:
            arts = {}
        if properties is None:
            properties = {}
        item = xbmcgui.ListItem(label, label2, path)
        if thumb:
            arts['thumb'] = thumb
        if fanart:
            arts['fanart'] = fanart
        if poster:
            arts['poster'] = poster
        item.setArt(arts)
        item.setInfo('video', videoInfo)
        if subs is not None:
            item.setSubtitles(subs)
        if not isFolder:
            properties['IsPlayable'] = 'true'
        for key, value in list(properties.items()):
            item.setProperty(key, value)
        return item


    def addListItem(label="", params=None, label2=None, thumb=None, fanart=None, poster=None, arts=None, videoInfo=None, properties=None, isFolder=True, path=None, subs=None):

        if isinstance(params, dict):
            url = staticutils.parameters(params)
        else:
            url = params
        if arts is None:
            arts = {}
        if properties is None:
            properties = {}
        item = xbmcgui.ListItem(label, label2, path)
        if thumb:
            arts['thumb'] = thumb
        if fanart:
            arts['fanart'] = fanart
        if poster:
            arts['poster'] = poster
        item.setArt(arts)
        item.setInfo('video', videoInfo)
        if subs is not None:
            item.setSubtitles(subs)
        if not isFolder:
            properties['IsPlayable'] = 'true'
        for key, value in list(properties.items()):
            item.setProperty(key, value)
            
        return xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=item, isFolder=isFolder)


    def setResolvedUrl(url="", solved=True, subs=None, headers=None, ins=None, insdata=None, item=None, exit=True):
        headerUrl = ""
        if headers:
            headerUrl = urlencode(headers)
        item = xbmcgui.ListItem(path=url + "|" + headerUrl) if item is None else item
        if subs is not None:
            item.setSubtitles(subs)
        if ins:
            item.setProperty('inputstreamaddon', ins)
            item.setProperty('inputstream', ins)
            if insdata:
                for key, value in list(insdata.items()):
                    item.setProperty(ins + '.' + key, value)
        xbmcplugin.setResolvedUrl(HANDLE, solved, item)
        if exit:
            sys.exit()


    def append_subtitle(sUrl, subtitlename, sync=False, provider=None):
        #listitem = createListItem({'label': 'Italian', 'label2': subtitlename, 'thumbnailImage': 'it'})
        if not provider:
            tUrl = {'action': 'download', 'subid': sUrl}
        else:
            tUrl = {'action': 'download', 'url': sUrl}
        log("Add subtitle '" + subtitlename + "' to the kist", 3)
        return addListItem(label="Italian", label2=subtitlename, params=tUrl, thumb="it", properties={"sync": 'true' if sync else 'false', "hearing_imp": "false"}, isFolder=False)


    def setContent(ctype='videos'):
        xbmcplugin.setContent(HANDLE, ctype)


    def endScript(message=None, loglevel=2, closedir=True):
        if message:
            log(message, loglevel)
        if closedir:
            xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)
        sys.exit()


    def createAddonFolder():
        if not os.path.isdir(DATA_PATH_T):
            log("Creating the addon data folder")
            os.makedirs(DATA_PATH_T)


    def getShowID():
        json_query = xbmc.executeJSONRPC((
            '{"jsonrpc":"2.0","method":"Player.GetItem","params":'
            '{"playerid":1,"properties":["tvshowid"]},"id":1}'))
        jsn_player_item = json.loads(json_query, 'utf-8', errors='ignore')
        if 'result' in jsn_player_item and jsn_player_item['result']['item']['type'] == 'episode':
            json_query = xbmc.executeJSONRPC((
                '{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetTVShowDetails","params":'
                '{"tvshowid":%s, "properties": ["imdbnumber"]}}') % (
                    jsn_player_item['result']['item']['tvshowid']))
            jsn_ep_det = json.loads(json_query, 'utf-8', errors='ignore')
            if 'result' in jsn_ep_det and jsn_ep_det['result']['tvshowdetails']['imdbnumber'] != '':
                return str(jsn_ep_det['result']['tvshowdetails']['imdbnumber'])
        return False


    def containsLanguage(strlang, langs):
        for lang in strlang.split(','):
            if xbmc.convertLanguage(lang, xbmc.ISO_639_2) in langs:
                return True
        return False


    def isPlayingVideo():
        return xbmc.Player().isPlayingVideo()


    def getInfoLabel(lbl):
        return xbmc.getInfoLabel(lbl)


    def getRegion(r):
        return xbmc.getRegion(r)


    def getEpisodeInfo():
        episode = {}
        episode['tvshow'] = staticutils.normalizeString(
            xbmc.getInfoLabel('VideoPlayer.TVshowtitle'))    # Show
        episode['season'] = xbmc.getInfoLabel(
            'VideoPlayer.Season')                            # Season
        episode['episode'] = xbmc.getInfoLabel(
            'VideoPlayer.Episode')                           # Episode
        file_original_path = xbmc.Player().getPlayingFile()  # Full path

        # Check if season is "Special"
        if str(episode['episode']).lower().find('s') > -1:
            episode['season'] = 0
            episode['episode'] = int(str(episode['episode'])[-1:])

        elif file_original_path.find('rar://') > -1:
            file_original_path = os.path.dirname(file_original_path[6:])

        elif file_original_path.find('stack://') > -1:
            file_original_path = file_original_path.split(' , ')[0][8:]

        episode['filename'] = os.path.splitext(os.path.basename(file_original_path))[0]

        return episode


    def getFormattedDate(dt):
        fmt = getRegion('datelong')
        fmt = fmt.replace("%A", KODILANGUAGE(dt.weekday() + 11))
        fmt = fmt.replace("%B", KODILANGUAGE(dt.month + 20))
        return dt.strftime(py2_encode(fmt))


    log("Starting module '%s' version '%s' with command '%s'" % (NAME, VERSION, sys.argv[2]), 1)


class KodiMediaset(object):

    def __init__(self):
        self.med = Mediaset()
        self.med.log = kodiutils.log
        self.iperpage = int(ADDON.getSetting(itemsperpage).strip)
        self.ua = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')

    def __imposta_range(self, start):
        limit = '{}-{}'.format(start, start + self.iperpage-1)
        return limit

    def __imposta_tipo_media(self, prog):
        kodiutils.setContent(_gather_media_type(prog) + 's')

    def __analizza_elenco(self, progs, setcontent=False, titlewd=False):
        if not progs:
            return
        if setcontent:
            self.__imposta_tipo_media(progs[0])
        for prog in progs:
            infos = _gather_info(prog, titlewd=titlewd)
            arts = _gather_art(prog)
            if 'media' in prog:
                # salta se non ha un media ma ha il tag perchè non riproducibile
                if prog['media']:
                    media = prog['media'][0]
                    args = {'mode': 'video'}
                    if 'pid' in media:
                        args['pid'] = media['pid']
                    elif 'publicUrl' in media:
                        args['pid'] = media['publicUrl'].split('/')[-1]
                    kodiutils.addListItem(infos["title"], args,
                                          videoInfo=infos, arts=arts, isFolder=False)
            elif 'tuningInstruction' in prog:
                data = {'mode': 'live'}
                if prog['tuningInstruction'] and not prog['mediasetstation$eventBased']:
                    vdata = prog['tuningInstruction']['urn:theplatform:tv:location:any']
                    for v in vdata:
                        if v['format'] == 'application/x-mpegURL':
                            data['id'] = v['releasePids'][0]
                        else:
                            data['mid'] = v['releasePids'][0]
                    kodiutils.addListItem(prog["title"], data, videoInfo=infos,
                                          arts=arts, isFolder=False)
            elif 'mediasetprogram$subBrandId' in prog:
                kodiutils.addListItem(prog["description"],
                                      {'mode': 'programma',
                                       'sub_brand_id': prog['mediasetprogram$subBrandId']},
                                      videoInfo=infos, arts=arts)
            elif 'mediasettvseason$brandId' in prog:
                kodiutils.addListItem(prog["mediasettvseason$displaySeason"],
                                      {'mode': 'programma',
                                       'brand_id': prog['mediasettvseason$brandId']},
                                      videoInfo=infos, arts=arts)
            elif 'seriesId' in prog:
                kodiutils.addListItem(prog["title"],
                                      {'mode': 'programma', 'series_id': prog['seriesId'],
                                       'title': prog['title']},
                                      videoInfo=infos, arts=arts)
            else:
                kodiutils.addListItem(prog["title"],
                                      {'mode': 'programma',
                                       'brand_id': prog['mediasetprogram$brandId']},
                                      videoInfo=infos, arts=arts)

    def root(self):
        # kodiutils.addListItem(LANGUAGE(32101), {'mode': 'tutto'})
        kodiutils.addListItem(LANGUAGE(32106), {'mode': 'programmi'})
        kodiutils.addListItem(LANGUAGE(32102), {'mode': 'fiction'})
        kodiutils.addListItem(LANGUAGE(32103), {'mode': 'film'})
        kodiutils.addListItem(LANGUAGE(32104), {'mode': 'kids'})
        kodiutils.addListItem(LANGUAGE(32105), {'mode': 'documentari'})
        kodiutils.addListItem(LANGUAGE(32111), {'mode': 'canali_live'})
        kodiutils.addListItem(LANGUAGE(32113), {'mode': 'guida_tv'})
        kodiutils.addListItem(LANGUAGE(32107), {'mode': 'cerca'})
        kodiutils.endScript()

    def elenco_cerca_root(self):
        kodiutils.addListItem(LANGUAGE(32115), {'mode': 'cerca', 'type': 'programmi'})
        kodiutils.addListItem(LANGUAGE(32116), {'mode': 'cerca', 'type': 'clip'})
        kodiutils.addListItem(LANGUAGE(32117), {'mode': 'cerca', 'type': 'episodi'})
        kodiutils.addListItem(LANGUAGE(32103), {'mode': 'cerca', 'type': 'film'})
        kodiutils.endScript()

    def apri_ricerca(self, sez):
        text = kodiutils.getKeyboardText(LANGUAGE(32131))
        self.elenco_cerca_sezione(sez, text, 1)

    def elenco_cerca_sezione(self, sez, text, page=None):
        switcher = {'programmi': 'CWSEARCHBRAND', 'clip': 'CWSEARCHCLIP',
                    'episodi': 'CWSEARCHEPISODE', 'film': 'CWSEARCHMOVIE'}
        sezcode = switcher.get(sez)
        if text:
            els, hasmore = self.med.Cerca(text, sezcode, pageels=self.iperpage, page=page)
            if els:
                exttitle = {'programmi': False, 'clip': True,
                            'episodi': True, 'film': False}
                self.__analizza_elenco(els, True, titlewd=exttitle.get(sez, False))
                if hasmore:
                    kodiutils.addListItem(LANGUAGE(32130),
                                          {'mode': 'cerca', 'search': text, 'type': sez,
                                           'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_tutto_root(self):
        kodiutils.addListItem(LANGUAGE(32121), {'mode': 'tutto', 'all': 'true'})
        kodiutils.addListItem(LANGUAGE(32122), {'mode': 'tutto', 'all': 'false'})
        kodiutils.endScript()

    def elenco_tutto_lettere(self, inonda):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                   'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '#']
        kodiutils.addListItem(LANGUAGE(
            32121), {'mode': 'tutto', 'all': 'false' if inonda else 'true', 'letter': 'all'})
        for letter in letters:
            kodiutils.addListItem(letter.upper(),
                                  {'mode': 'tutto', 'all': 'false' if inonda else 'true',
                                   'letter': letter})
        kodiutils.endScript()

    def elenco_tutto_lettera(self, inonda, lettera, page=None):
        kodiutils.setContent('videos')
        els, hasmore = self.med.OttieniTuttoLettera(
            lettera, inonda, pageels=self.iperpage, page=page)
        if els:
            self.__analizza_elenco(els)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(32130),
                                      {'mode': 'tutto', 'all': 'false' if inonda else 'true',
                                       'letter': lettera, 'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_tutto_tutti(self, inonda, page=None):
        kodiutils.setContent('videos')
        els, hasmore = self.med.OttieniTutto(inonda, pageels=self.iperpage, page=page)
        if els:
            self.__analizza_elenco(els)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(32130),
                                      {'mode': 'tutto', 'all': 'false' if inonda else 'true',
                                       'letter': 'all', 'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_programmi_root(self):
        # kodiutils.addListItem(LANGUAGE(32121), {'mode': 'programmi', 'all': 'true'})
        # kodiutils.addListItem(LANGUAGE(32122), {'mode': 'programmi', 'all': 'false'})
        for sec in self.med.OttieniCategorieProgrammi():
            if ("uxReference" not in sec):
                continue
            kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
        kodiutils.endScript()

    def elenco_programmi_tutti(self, inonda, page=None):
        kodiutils.setContent('tvshows')
        els, hasmore = self.med.OttieniTuttiProgrammi(inonda, pageels=self.iperpage,
                                                      page=page)
        if els:
            self.__analizza_elenco(els)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(32130),
                                      {'mode': 'programmi', 'all': 'false' if inonda else 'true',
                                       'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_fiction_root(self):
        # kodiutils.addListItem(LANGUAGE(32121), {'mode': 'fiction', 'all': 'true'})
        # kodiutils.addListItem(LANGUAGE(32122), {'mode': 'fiction', 'all': 'false'})
        for sec in self.med.OttieniGeneriFiction():
            if ("uxReference" not in sec):
                continue
            kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
        kodiutils.endScript()

    def elenco_fiction_tutti(self, inonda, page=None):
        kodiutils.setContent('tvshows')
        els, hasmore = self.med.OttieniTutteFiction(
            inonda, pageels=self.iperpage, page=page)
        if els:
            self.__analizza_elenco(els)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(32130),
                                      {'mode': 'fiction', 'all': 'false' if inonda else 'true',
                                       'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_film_root(self):
        # kodiutils.addListItem(LANGUAGE(32121), {'mode': 'film', 'all': 'true'})
        for sec in self.med.OttieniGeneriFilm():
            if ("uxReference" not in sec):
                continue
            kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
        kodiutils.endScript()

    def elenco_film_tutti(self, inonda, page=None):
        kodiutils.setContent('movies')
        els, hasmore = self.med.OttieniFilm(inonda, pageels=self.iperpage, page=page)
        if els:
            self.__analizza_elenco(els)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(32130),
                                      {'mode': 'film', 'all': 'false' if inonda else 'true',
                                       'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_kids_root(self):
        # kodiutils.addListItem(LANGUAGE(32121), {'mode': 'kids', 'all': 'true'})
        for sec in self.med.OttieniGeneriKids():
            if ("uxReference" not in sec):
                continue
            kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
        kodiutils.endScript()

    def elenco_kids_tutti(self, inonda, page=None):
        kodiutils.setContent('tvshows')
        els, hasmore = self.med.OttieniKids(inonda, pageels=self.iperpage, page=page)
        if els:
            self.__analizza_elenco(els)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(32130),
                                      {'mode': 'kids', 'all': 'false' if inonda else 'true',
                                       'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_documentari_root(self):
        # kodiutils.addListItem("Tutto", {'mode': 'documentari', 'all': 'true'})
        for sec in self.med.OttieniGeneriDocumentari():
            if ("uxReference" not in sec):
                continue
            kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
        kodiutils.endScript()

    def elenco_documentari_tutti(self, inonda, page=None):
        kodiutils.setContent('movies')
        els, hasmore = self.med.OttieniDocumentari(
            inonda, pageels=self.iperpage, page=page)
        if els:
            self.__analizza_elenco(els)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(32130),
                                      {'mode': 'documentari', 'all': 'false' if inonda else 'true',
                                       'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_sezione(self, sid, page=None):
        els, hasmore = self.med.OttieniProgrammiGenere(
            sid, pageels=self.iperpage, page=page)
        if els:
            self.__analizza_elenco(els, True)
            if hasmore:
                kodiutils.addListItem(LANGUAGE(
                    32130), {'mode': 'sezione', 'id': sid, 'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_stagioni_list(self, seriesId):
        els = self.med.OttieniStagioni(seriesId, sort='startYear|desc')
        if len(els) == 1:
            self.elenco_sezioni_list(els[0]['mediasettvseason$brandId'])
        else:
            self.__analizza_elenco(els)
            kodiutils.endScript()

    def elenco_sezioni_list(self, brandId):
        els = self.med.OttieniSezioniProgramma(
            brandId, sort='mediasetprogram$order')
        if len(els) == 2:
            self.elenco_video_list(els[1]['mediasetprogram$subBrandId'], 1)
        else:
            els.pop(0)
            self.__analizza_elenco(els)
        kodiutils.endScript()

    def elenco_video_list(self, subBrandId, start):
        if (kodiutils.getSettingAsBool('sortmediaset')):
            sort = 'mediasetprogram$publishInfo_lastPublished|desc'
        else:
            sort = 'mediasetprogram$publishInfo_lastPublished'
        els = self.med.OttieniVideoSezione(
            subBrandId, sort=sort, erange=self.__imposta_range(start))
        self.__analizza_elenco(els, True)
        if len(els) == self.iperpage:
            kodiutils.addListItem(LANGUAGE(32130),
                                  {'mode': 'programma', 'sub_brand_id': subBrandId,
                                   'start': start + self.iperpage})
        kodiutils.endScript()

    def guida_tv_root(self):
        kodiutils.setContent('videos')
        els = self.med.OttieniCanaliLive(sort='ShortTitle')
        for prog in els:
            infos = _gather_info(prog)
            arts = _gather_art(prog)
            if 'tuningInstruction' in prog:
                if prog['tuningInstruction'] and not prog.get('mediasetstation$eventBased', False):
                    kodiutils.addListItem(prog["title"],
                                          {'mode': 'guida_tv', 'id': prog['callSign'],
                                           'week': staticutils.get_timestamp_midnight()},
                                          videoInfo=infos, arts=arts)
        kodiutils.endScript()

    def guida_tv_canale_settimana(self, cid, dt):
        dt = staticutils.get_date_from_timestamp(dt)
        for d in range(0, 16):
            currdate = dt - timedelta(days=d)
            kodiutils.addListItem(kodiutils.getFormattedDate(currdate),
                                  {'mode': 'guida_tv', 'id': cid,
                                   'day': staticutils.get_timestamp_midnight(currdate)})
        # kodiutils.addListItem(LANGUAGE(32136),
        #                       {'mode': 'guida_tv', 'id': cid,
        #                       'week': staticutils.get_timestamp_midnight(dt - timedelta(days=7))})
        kodiutils.endScript()

    def guida_tv_canale_giorno(self, cid, dt):
        res = self.med.OttieniGuidaTV(cid, dt, dt + 86399999)  # 86399999 is one day minus 1 ms
        if 'listings' in res:
            for el in res['listings']:
                if (kodiutils.getSettingAsBool('fullguide') or
                        ('mediasetprogram$hasVod' in el['program'] and
                         el['program']['mediasetprogram$hasVod'])):
                    infos = _gather_info(el)
                    arts = _gather_art(el)
                    s_time = staticutils.get_date_from_timestamp(
                        el['startTime']).strftime("%H:%M")
                    e_time = staticutils.get_date_from_timestamp(
                        el['endTime']).strftime("%H:%M")
                    s = "{s}-{e} - {t}".format(s=s_time, e=e_time,
                                               t=el['mediasetlisting$epgTitle'])
                    kodiutils.addListItem(s,
                                          {'mode': 'video', 'guid': el['program']['guid']},
                                          videoInfo=infos, arts=arts, isFolder=False)
        kodiutils.endScript()

    def canali_live_root(self):
        kodiutils.setContent('videos')
        now = staticutils.get_timestamp()
        els = self.med.OttieniProgrammiLive()  # (sort='title')
        chans = {}
        for chan in els:
            if 'listings' in chan and chan['listings']:
                for prog in chan['listings']:
                    if prog['startTime'] <= now <= prog['endTime']:
                        guid = chan['guid']
                        chans[guid] = {'title': '{} - {}'.format(kodiutils.py2_encode(chan['title']),
                                                                 kodiutils.py2_encode(
                                                                     prog["mediasetlisting$epgTitle"])),
                                       'infos': _gather_info(prog),
                                       'arts': _gather_art(prog),
                                       'restartAllowed': prog['mediasetlisting$restartAllowed']}
        els = self.med.OttieniCanaliLive(sort='ShortTitle')
        for prog in els:
            if (prog['callSign'] in chans and 'tuningInstruction' in prog and
                    prog['tuningInstruction'] and not prog.get('mediasetstation$eventBased', False)):
                chn = chans[prog['callSign']]
                if chn['arts'] == {}:
                    chn['arts'] = _gather_art(prog)
                if chn['restartAllowed']:
                    if kodiutils.getSettingAsBool('splitlive'):
                        kodiutils.addListItem(chn['title'], {'mode': 'live',
                                                             'guid': prog['callSign']},
                                              videoInfo=chn['infos'], arts=chn['arts'])
                        continue
                    vid = self.__ottieni_vid_restart(prog['callSign'])
                    if vid:
                        kodiutils.addListItem(chn['title'], {'mode': 'video', 'pid': vid},
                                              videoInfo=chn['infos'], arts=chn['arts'],
                                              isFolder=False)
                        continue
                data = {'mode': 'live'}
                vdata = prog['tuningInstruction']['urn:theplatform:tv:location:any']
                for v in vdata:
                    if v['format'] == 'application/x-mpegURL':
                        data['id'] = v['releasePids'][0]
                    else:
                        data['mid'] = v['releasePids'][0]
                kodiutils.addListItem(chn['title'], data,
                                      videoInfo=chn['infos'], arts=chn['arts'], isFolder=False)
        kodiutils.endScript()

    def __ottieni_vid_restart(self, guid):
        res = self.med.OttieniLiveStream(guid)
        if ('currentListing' in res[0] and
                res[0]['currentListing']['mediasetlisting$restartAllowed']):
            url = res[0]['currentListing']['restartUrl']
            return url.rpartition('/')[-1]
        return None

    def canali_live_play(self, guid):
        res = self.med.OttieniLiveStream(guid)
        infos = {}
        arts = {}
        title = ''
        if 'currentListing' in res[0]:
            self.__imposta_tipo_media(res[0]['currentListing']['program'])
            infos = _gather_info(res[0]['currentListing'])
            arts = _gather_art(res[0]['currentListing']['program'])
            title = ' - ' + infos['title']
        if 'tuningInstruction' in res[0]:
            data = {'mode': 'live'}
            vdata = res[0]['tuningInstruction']['urn:theplatform:tv:location:any']
            for v in vdata:
                if v['format'] == 'application/x-mpegURL':
                    data['id'] = v['releasePids'][0]
                else:
                    data['mid'] = v['releasePids'][0]
            kodiutils.addListItem(kodiutils.LANGUAGE(32137) + title, data, videoInfo=infos,
                                  arts=arts, isFolder=False)
        if ('currentListing' in res[0] and
                res[0]['currentListing']['mediasetlisting$restartAllowed']):
            url = res[0]['currentListing']['restartUrl']
            vid = url.rpartition('/')[-1]
            kodiutils.addListItem(LANGUAGE(32138) + title, {'mode': 'video', 'pid': vid},
                                  videoInfo=infos, arts=arts, isFolder=False)
        kodiutils.endScript()

    def riproduci_guid(self, guid):
        res = self.med.OttieniInfoDaGuid(guid)
        if not res or 'media' not in res:
            kodiutils.showOkDialog(LANGUAGE(32132),LANGUAGE(32136))
            kodiutils.setResolvedUrl(solved=False)
            return
        self.riproduci_video(res['media'][0]['pid'])

    def riproduci_video(self, pid, live=False):
        from inputstreamhelper import Helper  # pylint: disable=import-error
        kodiutils.log("Trying to get the video from pid" + pid)
        data = self.med.OttieniDatiVideo(pid, live)
        if data['type'] == 'video/mp4':
            kodiutils.setResolvedUrl(data['url'])
            return
        is_helper = Helper('mpd', 'com.widevine.alpha' if data['security'] else None)
        if not is_helper.check_inputstream():
            kodiutils.showOkDialog(LANGUAGE(32132), LANGUAGE(32133))
            kodiutils.setResolvedUrl(solved=False)
            return
        headers = '&User-Agent={useragent}'.format(
            useragent=self.ua)
        props = {'manifest_type': 'mpd', 'stream_headers': headers}
        if data['security']:
            user = kodiutils.getSetting('email')
            password = kodiutils.getSetting('password')
            if user == '' or password == '':
                kodiutils.showOkDialog(LANGUAGE(32132), LANGUAGE(32134))
                kodiutils.setResolvedUrl(solved=False)
                return
            if not self.med.login(user, password):
                kodiutils.showOkDialog(LANGUAGE(32132), LANGUAGE(32135))
                kodiutils.setResolvedUrl(solved=False)
                return
            headers += '&Accept=*/*&Content-Type='
            props['license_type'] = 'com.widevine.alpha'
            props['stream_headers'] = headers
            url = self.med.OttieniWidevineAuthUrl(data['pid'])
            props['license_key'] = '{url}|{headers}|R{{SSM}}|'.format(url=url, headers=headers)

        headers = {'user-agent': self.ua,
                   't-apigw': self.med.apigw, 't-cts': self.med.cts}
        kodiutils.setResolvedUrl(data['url'], headers=headers, ins=is_helper.inputstream_addon,
                                 insdata=props)

    def main(self):
        # parameter values
        params = staticutils.getParams()
        if 'mode' in params:
            page = None
            if 'page' in params:
                try:
                    page = int(params['page'])
                except ValueError:
                    pass
            if params['mode'] == "tutto":
                if 'all' in params:
                    if 'letter' in params:
                        if params['letter'] == 'all':
                            self.elenco_tutto_tutti(None if params['all'] == 'true' else True, page)
                        else:
                            self.elenco_tutto_lettera(
                                None if params['all'] == 'true' else True, params['letter'], page)
                    else:
                        self.elenco_tutto_lettere(None if params['all'] == 'true' else True)
                else:
                    self.elenco_tutto_root()
            if params['mode'] == "fiction":
                if 'all' in params:
                    self.elenco_fiction_tutti(None if params['all'] == 'true' else True, page)
                else:
                    self.elenco_fiction_root()
            if params['mode'] == "programmi":
                if 'all' in params:
                    self.elenco_programmi_tutti(None if params['all'] == 'true' else True, page)
                else:
                    self.elenco_programmi_root()
            if params['mode'] == "film":
                if 'all' in params:
                    self.elenco_film_tutti(None if params['all'] == 'true' else True, page)
                else:
                    self.elenco_film_root()
            if params['mode'] == "kids":
                if 'all' in params:
                    self.elenco_kids_tutti(None if params['all'] == 'true' else True, page)
                else:
                    self.elenco_kids_root()
            if params['mode'] == "documentari":
                if 'all' in params:
                    self.elenco_documentari_tutti(None if params['all'] == 'true' else True, page)
                else:
                    self.elenco_documentari_root()
            if params['mode'] == "cerca":
                if 'type' in params:
                    if 'search' in params:
                        self.elenco_cerca_sezione(params['type'], params['search'], page)
                    else:
                        self.apri_ricerca(params['type'])
                else:
                    self.elenco_cerca_root()
            if params['mode'] == "sezione":
                self.elenco_sezione(params['id'])
            if params['mode'] == "programma":
                if 'series_id' in params:
                    self.elenco_stagioni_list(params['series_id'])
                elif 'sub_brand_id' in params:
                    if 'start' in params:
                        self.elenco_video_list(params['sub_brand_id'], int(params['start']))
                    else:
                        self.elenco_video_list(params['sub_brand_id'], 1)
                elif 'brand_id' in params:
                    self.elenco_sezioni_list(params['brand_id'])
            if params['mode'] == "video":
                if 'pid' in params:
                    self.riproduci_video(params['pid'])
                else:
                    self.riproduci_guid(params['guid'])
            if params['mode'] == "live":
                if 'id' in params:
                    self.riproduci_video(params['id'], True)
                else:
                    self.canali_live_play(params['guid'])
            if params['mode'] == "canali_live":
                self.canali_live_root()
            if params['mode'] == "guida_tv":
                if 'id' in params:
                    if 'week' in params:
                        self.guida_tv_canale_settimana(params['id'], int(params['week']))
                    elif 'day' in params:
                        self.guida_tv_canale_giorno(params['id'], int(params['day']))
                self.guida_tv_root()
        else:
            self.root()

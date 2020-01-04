# -*- coding: utf-8 -*-
from datetime import timedelta
from resources.lib.mediaset import Mediaset
from resources.mediaset_datahelper import __gather_info, __gather_art, __get_date_string
from phate89lib import kodiutils, staticutils  # pylint: disable=import-error
useragent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/67.0.3396.99 Safari/537.36')

mediaset = Mediaset()
mediaset.log = kodiutils.log
itemsperpage = kodiutils.getSetting('itemsperpage')


def __imposta_tipo_media(prog):
    kodiutils.setContent(__ottieni_tipo_media(prog))


def __ottieni_tipo_media(prog):
    if 'programType' in prog:
        if prog['programType'] == 'movie':
            return 'movies'
        if prog['programType'] == 'episode':
            return 'episodes'
    if ('mediasetprogram$brandVerticalSiteCMS' in prog and
            prog['mediasetprogram$brandVerticalSiteCMS'] == 'fiction'):
        return 'tvshows'
    if 'tvSeasonNumber' in prog or 'tvSeasonEpisodeNumber' in prog:
        return 'episodes'
    if 'seriesId' in prog and 'mediasetprogram$subBrandId' not in prog:
        return 'tvshows'
    if ('mediasetprogram$subBrandDescription' in prog and
            (prog['mediasetprogram$subBrandDescription'].lower() == 'film' or
             prog['mediasetprogram$subBrandDescription'].lower() == 'documentario')):
        return 'movies'
    return 'videos'


def __analizza_elenco(progs, setcontent=False):
    if not progs:
        return
    if setcontent:
        __imposta_tipo_media(progs[0])
    for prog in progs:
        infos = __gather_info(prog)
        arts = __gather_art(prog)
        if 'media' in prog:
            # salta se non ha un media ma ha il tag perchè non riproducibile
            if prog['media']:
                kodiutils.addListItem(prog["title"],
                                      {'mode': 'video', 'pid': prog['media'][0]['pid']},
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
            kodiutils.addListItem(prog["title"],
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


def root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32101), {'mode': 'tutto'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32106), {'mode': 'programmi'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32102), {'mode': 'fiction'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32103), {'mode': 'film'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32104), {'mode': 'kids'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32105), {'mode': 'documentari'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32111), {'mode': 'canali_live'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32113), {'mode': 'guida_tv'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32107), {'mode': 'cerca'})
    kodiutils.endScript()


def elenco_cerca_root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32115), {'mode': 'cerca', 'type': 'programmi'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32116), {'mode': 'cerca', 'type': 'clip'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32117), {'mode': 'cerca', 'type': 'episodi'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32103), {'mode': 'cerca', 'type': 'film'})
    kodiutils.endScript()


def apri_ricerca(sez):
    text = kodiutils.getKeyboardText(kodiutils.LANGUAGE(32131))
    elenco_cerca_sezione(sez, text, 1)


def elenco_cerca_sezione(sez, text, page=None):
    switcher = {'programmi': 'CWSEARCHBRAND', 'clip': 'CWSEARCHCLIP',
                'episodi': 'CWSEARCHEPISODE', 'film': 'CWSEARCHMOVIE'}
    sezcode = switcher.get(sez)
    if text:
        els, hasmore = mediaset.Cerca(text, sezcode, pageels=itemsperpage, page=page)
        if els:
            __analizza_elenco(els, True)
            if hasmore:
                kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                      {'mode': 'cerca', 'search': text, 'type': sez,
                                       'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_tutto_root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32121), {'mode': 'tutto', 'all': 'true'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32122), {'mode': 'tutto', 'all': 'false'})
    kodiutils.endScript()


def elenco_tutto_lettere(inonda):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '#']
    kodiutils.addListItem(kodiutils.LANGUAGE(
        32121), {'mode': 'tutto', 'all': 'false' if inonda else 'true', 'letter': 'all'})
    for letter in letters:
        kodiutils.addListItem(letter.upper(),
                              {'mode': 'tutto', 'all': 'false' if inonda else 'true',
                               'letter': letter})
    kodiutils.endScript()


def elenco_tutto_lettera(inonda, lettera, page=None):
    kodiutils.setContent('videos')
    els, hasmore = mediaset.OttieniTuttoLettera(lettera, inonda, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                  {'mode': 'tutto', 'all': 'false' if inonda else 'true',
                                   'letter': lettera, 'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_tutto_tutti(inonda, page=None):
    kodiutils.setContent('videos')
    els, hasmore = mediaset.OttieniTutto(inonda, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                  {'mode': 'tutto', 'all': 'false' if inonda else 'true',
                                   'letter': 'all', 'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_programmi_root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32121), {'mode': 'programmi', 'all': 'true'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32122), {'mode': 'programmi', 'all': 'false'})
    kodiutils.endScript()


def elenco_programmi_tutti(inonda, page=None):
    kodiutils.setContent('tvshows')
    els, hasmore = mediaset.OttieniTuttiProgrammi(inonda, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                  {'mode': 'programmi', 'all': 'false' if inonda else 'true',
                                   'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_fiction_root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32121), {'mode': 'fiction', 'all': 'true'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32122), {'mode': 'fiction', 'all': 'false'})
    for sec in mediaset.OttieniGeneriFiction():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
    kodiutils.endScript()


def elenco_fiction_tutti(inonda, page=None):
    kodiutils.setContent('tvshows')
    els, hasmore = mediaset.OttieniTutteFiction(inonda, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                  {'mode': 'fiction', 'all': 'false' if inonda else 'true',
                                   'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_film_root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32121), {'mode': 'film', 'all': 'true'})
    for sec in mediaset.OttieniGeneriFilm():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
    kodiutils.endScript()


def elenco_film_tutti(inonda, page=None):
    kodiutils.setContent('movies')
    els, hasmore = mediaset.OttieniFilm(inonda, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                  {'mode': 'film', 'all': 'false' if inonda else 'true',
                                   'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_kids_root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32121), {'mode': 'kids', 'all': 'true'})
    for sec in mediaset.OttieniGeneriKids():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
    kodiutils.endScript()


def elenco_kids_tutti(inonda, page=None):
    kodiutils.setContent('tvshows')
    els, hasmore = mediaset.OttieniKids(inonda, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                  {'mode': 'kids', 'all': 'false' if inonda else 'true',
                                   'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_documentari_root():
    kodiutils.addListItem("Tutto", {'mode': 'documentari', 'all': 'true'})
    for sec in mediaset.OttieniGeneriDocumentari():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
    kodiutils.endScript()


def elenco_documentari_tutti(inonda, page=None):
    kodiutils.setContent('movies')
    els, hasmore = mediaset.OttieniDocumentari(inonda, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                  {'mode': 'documentari', 'all': 'false' if inonda else 'true',
                                   'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_sezione(sid, page=None):
    els, hasmore = mediaset.OttieniProgrammiGenere(sid, pageels=itemsperpage, page=page)
    if els:
        __analizza_elenco(els, True)
        if hasmore:
            kodiutils.addListItem(kodiutils.LANGUAGE(
                32130), {'mode': 'sezione', 'id': sid, 'page': page + 1 if page else 2})
    kodiutils.endScript()


def elenco_stagioni_list(seriesId, title):
    els = mediaset.OttieniStagioni(seriesId)
    if len(els) == 1:
        elenco_sezioni_list(els[0]['mediasettvseason$brandId'])
    else:
        # workaround per controllare se è già una stagione e non una serie
        brandId = -1
        for el in els:
            if el['title'] == title:
                brandId = el['mediasettvseason$brandId']
                break
        if brandId == -1:
            __analizza_elenco(els)
            kodiutils.endScript()
        else:
            elenco_sezioni_list(brandId)


def elenco_sezioni_list(brandId):
    els = mediaset.OttieniSezioniProgramma(brandId)
    if len(els) == 2:
        elenco_video_list(els[1]['mediasetprogram$subBrandId'])
    else:
        els.pop(0)
        __analizza_elenco(els)
    kodiutils.endScript()


def elenco_video_list(subBrandId):
    els = mediaset.OttieniVideoSezione(subBrandId)
    __analizza_elenco(els, True)
    kodiutils.endScript()


def canali_live_root():
    kodiutils.setContent('videos')
    els = mediaset.OttieniCanaliLive()
    __analizza_elenco(els)
    kodiutils.endScript()


def guida_tv_root():
    kodiutils.setContent('videos')
    els = mediaset.OttieniCanaliLive()
    for prog in els:
        infos = __gather_info(prog)
        arts = __gather_art(prog)
        if 'tuningInstruction' in prog:
            if prog['tuningInstruction'] and not prog['mediasetstation$eventBased']:
                kodiutils.addListItem(prog["title"],
                                      {'mode': 'guida_tv', 'id': prog['callSign'],
                                       'week': staticutils.get_timestamp_midnight()},
                                      videoInfo=infos, arts=arts)
    kodiutils.endScript()


def guida_tv_canale_settimana(cid, dt):
    dt = staticutils.get_date_from_timestamp(dt)
    for d in range(0, 16):
        currdate = dt - timedelta(days=d)
        kodiutils.addListItem(__get_date_string(currdate),
                              {'mode': 'guida_tv', 'id': cid,
                               'day': staticutils.get_timestamp_midnight(currdate)})
    # kodiutils.addListItem(kodiutils.LANGUAGE(32136),
    #                       {'mode': 'guida_tv', 'id': cid,
    #                        'week': staticutils.get_timestamp_midnight(dt - timedelta(days=7))})
    kodiutils.endScript()


def guida_tv_canale_giorno(cid, dt):
    res = mediaset.OttieniGuidaTV(cid, dt, dt + 86399999)  # 86399999 is one day minus 1 ms
    if 'listings' in res:
        for el in res['listings']:
            if (kodiutils.getSettingAsBool('fullguide') or
                    ('mediasetprogram$hasVod' in el['program'] and
                     el['program']['mediasetprogram$hasVod'])):
                infos = __gather_info(el)
                arts = __gather_art(el)
                s_time = staticutils.get_date_from_timestamp(el['startTime']).strftime("%H:%M")
                e_time = staticutils.get_date_from_timestamp(el['endTime']).strftime("%H:%M")
                s = "{s}:{e} - {t}".format(s=s_time, e=e_time, t=el['mediasetlisting$epgTitle'])
                kodiutils.addListItem(s,
                                      {'mode': 'video', 'guid': el['program']['guid']},
                                      videoInfo=infos, arts=arts, isFolder=False)
    kodiutils.endScript()


def canali_live_root_new():
    kodiutils.setContent('videos')
    now = staticutils.get_timestamp()
    els = mediaset.OttieniProgrammiLive()
    chans = {}
    for chan in els:
        if 'listings' in chan and chan['listings']:
            for prog in chan['listings']:
                if prog['startTime'] <= now <= prog['endTime']:
                    guid = chan['guid']
                    chans[guid] = {'title': chan['title'] + ': ' + prog["mediasetlisting$epgTitle"],
                                   'infos': __gather_info(prog),
                                   'arts': __gather_art(prog),
                                   'restartAllowed': prog['mediasetlisting$restartAllowed']}
    els = mediaset.OttieniCanaliLive()
    for prog in els:
        if (prog['callSign'] in chans and 'tuningInstruction' in prog and
                prog['tuningInstruction'] and not prog['mediasetstation$eventBased']):
            chn = chans[prog['callSign']]
            if chn['arts'] == {}:
                chn['arts'] = __gather_art(prog)
            if chn['restartAllowed']:
                kodiutils.addListItem(chn['title'],
                                      {'mode': 'live', 'guid': prog['callSign']},
                                      videoInfo=chn['infos'], arts=chn['arts'])
            else:
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


def canali_live_play(guid):
    res = mediaset.OttieniLiveStream(guid)
    if 'tuningInstruction' in res[0]:
        data = {'mode': 'live'}
        vdata = res[0]['tuningInstruction']['urn:theplatform:tv:location:any']
        for v in vdata:
            if v['format'] == 'application/x-mpegURL':
                data['id'] = v['releasePids'][0]
            else:
                data['mid'] = v['releasePids'][0]
        kodiutils.addListItem(kodiutils.LANGUAGE(32137), data, isFolder=False)
    if 'currentListing' in res[0] and res[0]['currentListing']['mediasetlisting$restartAllowed']:
        url = res[0]['currentListing']['restartUrl']
        vid = url.rpartition('/')[-1]
        kodiutils.addListItem(kodiutils.LANGUAGE(
            32138), {'mode': 'video', 'pid': vid}, isFolder=False)
    kodiutils.endScript()


def riproduci_guid(guid):
    res = mediaset.OttieniInfoDaGuid(guid)
    if not res or 'media' not in res:
        kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32136))
        kodiutils.setResolvedUrl(solved=False)
        return
    riproduci_video(res['media'][0]['pid'])


def riproduci_video(pid, live=False):
    from inputstreamhelper import Helper
    kodiutils.log("Trying to get the video from pid" + pid)
    data = mediaset.OttieniDatiVideo(pid, live)
    if data['type'] == 'video/mp4':
        kodiutils.setResolvedUrl(data['url'])
        return
    is_helper = Helper('mpd', 'com.widevine.alpha' if data['security'] else None)
    if not is_helper.check_inputstream():
        kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32133))
        kodiutils.setResolvedUrl(solved=False)
        return
    props = {'manifest_type': 'mpd'}
    if data['security']:
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        if user == '' or password == '':
            kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32134))
            kodiutils.setResolvedUrl(solved=False)
            return
        if not mediaset.login(user, password):
            kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32135))
            kodiutils.setResolvedUrl(solved=False)
            return
        props['license_type'] = 'com.widevine.alpha'
        url = (
            'https://widevine.entitlement.theplatform.eu/wv/web/ModularDrm/getRawWidevineLicense?'
            'releasePid={pid}&account=http://access.auth.theplatform.com/data/Account/'
            '2702976343&schema=1.0&token={cts}').format(pid=data['pid'], cts=mediaset.cts)
        headers = 'Accept=*/*&Content-Type=&User-Agent={useragent}'.format(useragent=useragent)
        props['license_key'] = '{url}|{headers}|R{{SSM}}|'.format(url=url, headers=headers)

    headers = {'user-agent': useragent, 't-apigw': mediaset.apigw, 't-cts': mediaset.cts}
    kodiutils.setResolvedUrl(data['url'], headers=headers,
                             ins=is_helper.inputstream_addon, insdata=props)


def main():
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
                        elenco_tutto_tutti(None if params['all'] == 'true' else True, page)
                    else:
                        elenco_tutto_lettera(
                            None if params['all'] == 'true' else True, params['letter'], page)
                else:
                    elenco_tutto_lettere(None if params['all'] == 'true' else True)
            else:
                elenco_tutto_root()
        if params['mode'] == "fiction":
            if 'all' in params:
                elenco_fiction_tutti(None if params['all'] == 'true' else True, page)
            else:
                elenco_fiction_root()
        if params['mode'] == "programmi":
            if 'all' in params:
                elenco_programmi_tutti(None if params['all'] == 'true' else True, page)
            else:
                elenco_programmi_root()
        if params['mode'] == "film":
            if 'all' in params:
                elenco_film_tutti(None if params['all'] == 'true' else True, page)
            else:
                elenco_film_root()
        if params['mode'] == "kids":
            if 'all' in params:
                elenco_kids_tutti(None if params['all'] == 'true' else True, page)
            else:
                elenco_kids_root()
        if params['mode'] == "documentari":
            if 'all' in params:
                elenco_documentari_tutti(None if params['all'] == 'true' else True, page)
            else:
                elenco_documentari_root()
        if params['mode'] == "cerca":
            if 'type' in params:
                if 'search' in params:
                    elenco_cerca_sezione(params['type'], params['search'], page)
                else:
                    apri_ricerca(params['type'])
            else:
                elenco_cerca_root()
        if params['mode'] == "sezione":
            elenco_sezione(params['id'])
        if params['mode'] == "programma":
            if 'series_id' in params:
                elenco_stagioni_list(params['series_id'], params['title'])
            elif 'sub_brand_id' in params:
                elenco_video_list(params['sub_brand_id'])
            elif 'brand_id' in params:
                elenco_sezioni_list(params['brand_id'])
        if params['mode'] == "video":
            if 'pid' in params:
                riproduci_video(params['pid'])
            else:
                riproduci_guid(params['guid'])
        if params['mode'] == "live":
            if 'id' in params:
                riproduci_video(params['id'], True)
            else:
                canali_live_play(params['guid'])
        if params['mode'] == "canali_live":
            canali_live_root()
        if params['mode'] == "guida_tv":
            if 'id' in params:
                if 'week' in params:
                    guida_tv_canale_settimana(params['id'], int(params['week']))
                elif 'day' in params:
                    guida_tv_canale_giorno(params['id'], int(params['day']))
            guida_tv_root()
    else:
        root()

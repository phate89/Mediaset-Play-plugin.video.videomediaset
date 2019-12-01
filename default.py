# -*- coding: utf-8 -*-
from resources.lib.mediaset import Mediaset
from phate89lib import kodiutils, staticutils
import inputstreamhelper

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'

mediaset = Mediaset(kodiutils.getSetting('email'), kodiutils.getSetting('password'))
mediaset.log = kodiutils.log

def root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32101),{'mode':'tutto'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32102),{'mode':'fiction'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32103),{'mode':'film'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32104),{'mode':'kids'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32105),{'mode':'documentari'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32111),{'mode':'canali_live'})
    kodiutils.endScript()

def __gather_info(prog):
    infos = {}
    infos['title']=prog["title"]
    if infos['title'] == '' and 'mediasetprogram$brandTitle' in prog:
        infos['title']=prog["mediasetprogram$brandTitle"]
    
    if 'credits' in prog:
        infos['cast']=[]
        infos['director']=[]
        for person in prog['credits']:
            if person['creditType']=='actor':
                infos['cast'].append(person['personName'])
            elif person['creditType']=='director':
                infos['director'].append(person['personName'])
    plot=""
    plotoutline=""
    #try to find plotoutline
    if 'shortDescription' in prog:
        plotoutline=prog["shortDescription"]
    elif 'mediasettvseason$shortDescription' in prog:
        plotoutline=prog["mediasettvseason$shortDescription"]
    elif 'description' in prog:
        plotoutline=prog["description"]
    elif 'mediasetprogram$brandDescription' in prog:
        plotoutline=prog["mediasetprogram$brandDescription"]
    elif 'mediasetprogram$subBrandDescription' in prog:
        plotoutline=prog["mediasetprogram$subBrandDescription"]
        
    #try to find plot
    if 'longDescription' in prog:
        plot=prog["longDescription"]
    elif 'description' in prog:
        plotoutline=prog["description"]
    elif 'mediasetprogram$brandDescription' in prog:
        plot=prog["mediasetprogram$brandDescription"]
    elif 'mediasetprogram$subBrandDescription' in prog:
        plot=prog["mediasetprogram$subBrandDescription"]
        
    #fill the other if one is empty
    if plot=="":
        plot=plotoutline
    if plotoutline=="":
        plotoutline=plot
    infos['plot'] = plot
    infos['plotoutline'] = plotoutline
    if 'mediasetprogram$duration' in prog:
        infos['duration'] = prog['mediasetprogram$duration']
    if 'mediasetprogram$genres' in prog:
        infos['genre']=prog['mediasetprogram$genres']
    elif 'mediasettvseason$genres' in prog:
        infos['genre']=prog['mediasettvseason$genres']
    if 'year' in prog:
        infos['year']=prog['year']
    if 'tvSeasonNumber' in prog:
        infos['season']=prog['tvSeasonNumber']
    if 'tvSeasonEpisodeNumber' in prog:
        infos['episode']=prog['tvSeasonEpisodeNumber']
    
    return infos
    
def __gather_art(prog):
    arts = {}
    if 'thumbnails' in prog:
        if 'image_vertical-264x396' in prog['thumbnails']:
            arts['poster'] = prog['thumbnails']['image_vertical-264x396']['url']
            arts['thumb'] = arts['poster']
        elif 'channel_logo-100x100' in prog['thumbnails']:
            arts['poster'] = prog['thumbnails']['channel_logo-100x100']['url']
            arts['thumb'] = arts['poster']
            
        if 'brand_cover-1440x513' in prog['thumbnails']:
            arts['banner'] = prog['thumbnails']['brand_cover-1440x513']['url']
        elif 'image_header_poster-1440x630' in prog['thumbnails']:
            arts['banner'] = prog['thumbnails']['image_header_poster-1440x630']['url']
        elif 'image_header_poster-1440x433' in prog['thumbnails']:
            arts['banner'] = prog['thumbnails']['image_header_poster-1440x433']['url']
        if 'image_header_poster-1440x630' in prog['thumbnails']:
            arts['landscape'] = prog['thumbnails']['image_header_poster-1440x630']['url']
        elif 'image_header_poster-1440x433' in prog['thumbnails']:
            arts['landscape'] = prog['thumbnails']['image_header_poster-1440x433']['url']
        if 'brand_logo-210x210' in prog['thumbnails']:
            arts['icon'] = prog['thumbnails']['brand_logo-210x210']['url']
    return arts

def __imposta_tipo_media(prog):
    if 'tvSeasonNumber' in prog or 'tvSeasonEpisodeNumber' in prog:
        kodiutils.setContent('episodes')
    elif 'seriesId' in prog and 'mediasetprogram$subBrandId' not in prog:
        kodiutils.setContent('tvshows')
    elif 'mediasetprogram$subBrandDescription' in prog and (prog['mediasetprogram$subBrandDescription'].lower() == 'film' or prog['mediasetprogram$subBrandDescription'].lower() == 'documentario'):
        kodiutils.setContent('movies')
    else:
        kodiutils.setContent('videos')
    
def __analizza_elenco(progs):
    if len(progs) == 0:
        return
    __imposta_tipo_media(progs[0])
    for prog in progs:
        infos = __gather_info(prog)
        arts=__gather_art(prog)
        if 'media' in prog:
            kodiutils.addListItem(prog["title"],{'mode':'video','pid':prog['media'][0]['pid']},videoInfo=infos,arts=arts,isFolder=False)
        elif 'tuningInstruction' in prog:
            data = {'mode':'live'}
            if prog['tuningInstruction'] and not prog['mediasetstation$eventBased']:
                vdata=prog['tuningInstruction']['urn:theplatform:tv:location:any']
                for v in vdata:
                    if v['format']=='application/x-mpegURL':
                        data['id'] = v['releasePids'][0]
                    else:
                        data['mid'] = v['releasePids'][0]
                kodiutils.addListItem(prog["title"],data,videoInfo=infos,arts=arts,isFolder=False)
        elif 'mediasetprogram$subBrandId' in prog:
            kodiutils.addListItem(prog["description"],{'mode':'programma','sub_brand_id':prog['mediasetprogram$subBrandId']},videoInfo=infos,arts=arts)
        elif 'mediasettvseason$brandId' in prog:
            kodiutils.addListItem(prog["title"],{'mode':'programma','brand_id':prog['mediasettvseason$brandId']},videoInfo=infos,arts=arts)
        #elif 'seriesId' in prog:
        #    kodiutils.addListItem(prog["title"],{'mode':'programma','series_id':prog['seriesId']},videoInfo=infos,arts=arts)
        else:
            kodiutils.addListItem(prog["title"],{'mode':'programma','brand_id':prog['mediasetprogram$brandId']},videoInfo=infos,arts=arts)
    kodiutils.endScript()
    
def elenco_programmi_root():
    kodiutils.addListItem(kodiutils.LANGUAGE(32121),{'mode':'tutto','all':'true'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32122),{'mode':'tutto','all':'false'})
    kodiutils.endScript()

def elenco_programmi_tutti(inonda):
    kodiutils.setContent('tvshows')
    els=mediaset.OttieniTutto(inonda)
    __analizza_elenco(els)

def elenco_fiction_root():
    kodiutils.setContent('videos')
    kodiutils.addListItem(kodiutils.LANGUAGE(32121),{'mode':'fiction','all':'true'})
    kodiutils.addListItem(kodiutils.LANGUAGE(32122),{'mode':'fiction','all':'false'})
    for sec in mediaset.OttieniGeneriFiction():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"],{'mode':'sezione','id':sec['uxReference']})
    kodiutils.endScript()
    
def elenco_fiction_tutti(inonda):
    kodiutils.setContent('tvshows')
    els=mediaset.OttieniTutteFiction(inonda)
    __analizza_elenco(els)
    
def elenco_film_root():
    kodiutils.setContent('videos')
    kodiutils.addListItem(kodiutils.LANGUAGE(32121),{'mode':'film','all':'true'})
    for sec in mediaset.OttieniGeneriFilm():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"],{'mode':'sezione','id':sec['uxReference']})
    kodiutils.endScript()
    
def elenco_film_tutti(inonda):
    kodiutils.setContent('movies')
    els=mediaset.OttieniFilm(inonda)
    __analizza_elenco(els)
    
def elenco_kids_root():
    kodiutils.setContent('videos')
    kodiutils.addListItem(kodiutils.LANGUAGE(32121),{'mode':'kids','all':'true'})
    for sec in mediaset.OttieniGeneriKids():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"],{'mode':'sezione','id':sec['uxReference']})
    kodiutils.endScript()
    
def elenco_kids_tutti(inonda):
    kodiutils.setContent('movies')
    els=mediaset.OttieniKids(inonda)
    __analizza_elenco(els)
    
def elenco_documentari_root():
    kodiutils.setContent('videos')
    kodiutils.addListItem("Tutto",{'mode':'documentari','all':'true'})
    for sec in mediaset.OttieniGeneriDocumentari():
        if ("uxReference" not in sec):
            continue
        kodiutils.addListItem(sec["title"],{'mode':'sezione','id':sec['uxReference']})
    kodiutils.endScript()
    
def elenco_documentari_tutti(inonda):
    kodiutils.setContent('movies')
    els=mediaset.OttieniDocumentari(inonda)
    __analizza_elenco(els)
    
def elenco_sezione(id):
    els=mediaset.OttieniProgrammiGenere(id)
    __analizza_elenco(els)

def elenco_stagioni_list(seriesId):
    els=mediaset.OttieniStagioni(seriesId)
    __analizza_elenco(els)

def elenco_sezioni_list(brandId):
    els=mediaset.OttieniSezioniProgramma(brandId)
    els.pop(0)
    if len(els) == 1:
        elenco_video_list(els[0]['mediasetprogram$subBrandId'])
    else:
        __analizza_elenco(els)

def elenco_video_list(subBrandId):
    els=mediaset.OttieniVideoSezione(subBrandId)
    #els.pop(0)
    __analizza_elenco(els)

# workaround to gather the real url and avoid failings
def __get_real_url(url, ua=None):
    headers={}
    if (ua):
        headers['user-agent']=ua
    res = mediaset.createRequest(url, headers=headers, allow_redirects=False)
    kodiutils.log("Found url " + res.headers['Location'])
    return res.headers['Location']
    
def __get_best_url_possible(url, protocol, id):
    kodiutils.log("Trying to get the url from " + url)
    mediaset.login()
    realurl = __get_real_url(url, useragent)
    is_helper = inputstreamhelper.Helper(protocol)
    print(protocol)
    print(is_helper.check_inputstream())
    headers = {'user-agent':useragent, 't-apigw': mediaset.apigw, 't-cts': mediaset.cts }
    if is_helper.check_inputstream() and not realurl.endswith('mp4'):
        props = {'manifest_type': protocol,
                 'license_type': 'com.widevine.alpha',
                 'license_key': 'https://widevine.entitlement.theplatform.eu/wv/web/ModularDrm/getRawWidevineLicense?releasePid=' + id + '&account=http://access.auth.theplatform.com/data/Account/2702976343&schema=1.0&token=' + mediaset.cts + '|Accept=*/*&Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36|R{SSM}|'
        }
        kodiutils.setResolvedUrl(realurl, headers=headers, ins=is_helper.inputstream_addon, insdata=props)
    else:
        kodiutils.setResolvedUrl(realurl)

def __play_video(pid, live=False):
    url = 'https://link.theplatform.eu/s/PR1GhC/'
    if not live:
        url +='media/'
    url += pid + '?assetTypes=HD,browser,widevine:HD,browser:SD,browser,widevine:SD,browser:SD&auto=true&balance=true&format=smil&formats=MPEG-DASH,MPEG4,M3U&tracking=true'
    kodiutils.log("Trying to get the video from " + url)
    data = mediaset.OttieniDatiVideo(url)
    if data['type']!='video/mp4':
        is_helper = inputstreamhelper.Helper('mpd')
        mediaset.login()
        headers = {'user-agent':useragent, 't-apigw': mediaset.apigw, 't-cts': mediaset.cts }
        if is_helper.check_inputstream():
            props = {'manifest_type': 'mpd',
                    'license_type': 'com.widevine.alpha',
                    'license_key': 'https://widevine.entitlement.theplatform.eu/wv/web/ModularDrm/getRawWidevineLicense?releasePid=' + data['pid'] + '&account=http://access.auth.theplatform.com/data/Account/2702976343&schema=1.0&token=' + mediaset.cts + '|Accept=*/*&Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36|R{SSM}|'
            }
            kodiutils.setResolvedUrl(data['url'], headers=headers, ins=is_helper.inputstream_addon, insdata=props)
            return
    kodiutils.setResolvedUrl(data['url'])

def playVideo(pid):
    # Play the item
    __get_best_url_possible("http://link.theplatform.eu/s/PR1GhC/media/" + pid, "mpd",pid)
  
def playLive(id):
    # Play the item
    __get_best_url_possible("https://link.theplatform.eu/s/PR1GhC/" + id, "hls", id)#, mtype="hls", headers='user-agent='+useragent)

def canali_live_root():
    els=mediaset.OttieniCanaliLive()
    __analizza_elenco(els)

# parameter values
params = staticutils.getParams()

#if not 'mode' in params or params['mode'] != 'video':
#    elenco_video_list('100003454')
#    import sys
#    sys.exit()
if 'mode' in params:
    if params['mode'] == "tutto":
        if 'all' in params:
            elenco_programmi_tutti(None if params['all'] == 'true' else True)
        else:
            elenco_programmi_root()
    if params['mode'] == "fiction":
        if 'all' in params:
            elenco_fiction_tutti(None if params['all'] == 'true' else True)
        else:
            elenco_fiction_root()
    if params['mode'] == "film":
        if 'all' in params:
            elenco_film_tutti(None if params['all'] == 'true' else True)
        else:
            elenco_film_root()
    if params['mode'] == "kids":
        if 'all' in params:
            elenco_kids_tutti(None if params['all'] == 'true' else True)
        else:
            elenco_kids_root()
    if params['mode'] == "documentari":
        if 'all' in params:
            elenco_documentari_tutti(None if params['all'] == 'true' else True)
        else:
            elenco_documentari_root()
    if params['mode'] == "sezione":
        elenco_sezione(params['id'])
    if params['mode'] == "programma":
        if 'series_id' in params:
            elenco_stagioni_list(params['series_id'])
        elif 'sub_brand_id' in params:
            elenco_video_list(params['sub_brand_id'])
        elif 'brand_id' in params:
            elenco_sezioni_list(params['brand_id'])
    if params['mode'] == "video":
        __play_video(params['pid'])
        #playVideo(params['pid'])
    if params['mode'] == "live":
        __play_video(params['id'], True)
        #playLive(params['id'])
    if params['mode'] == "canali_live":
        canali_live_root()
else:
    root()


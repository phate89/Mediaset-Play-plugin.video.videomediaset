from datetime import datetime

def __get_date(dt):
    return datetime.fromtimestamp(dt / 1e3)

def __get_timestamp_midnight(dt):
    return int((dt.replace(hour=0, minute=0, second=0, microsecond=0) - datetime(1970,1,1)).total_seconds())*1000

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

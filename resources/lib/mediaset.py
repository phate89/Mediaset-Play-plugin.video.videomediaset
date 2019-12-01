from phate89lib import rutils
import json
import re
import math
try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode, quote
import xml.etree.ElementTree as ET

class Mediaset(rutils.RUtils):

    USERAGENT="VideoMediaset Kodi Addon"
    
    def __init__(self, email='', password=''):
        self.email = email
        self.password = password
        super(rutils.RUtils, self).__init__()

    def __getAPISession(self):
        res = self.SESSION.get("https://api.one.accedo.tv/session?appKey=59ad346f1de1c4000dfd09c5&uuid=sdd",verify=False)
        self.setHeader('x-session',res.json()['sessionKey'])
        
    def login(self):
        if self.email!='':
            if self.userLogin():
                return True
            else:
                self.log('Falling back to anon login', 4)
        return self.anonymousLogin()
    
    def userLogin(self):
        self.log('Trying to login with user data', 4)
        data = {"loginID": self.email,
                "password": self.password,
                "sessionExpiration": "31536000",
                "targetEnv": "jssdk",
                "include": "profile,data,emails,subscriptions,preferences,",
                "includeUserInfo": "true",
                "loginMode": "standard",
                "lang": "it",
                "APIKey": "3_NhZq9YZgkgeKfN08uFjs3NYGo2Txv4QQTULh0he2w337E-o0DPXzEp4aVnWIR4jg",
                "cid": "mediaset-web-mediaset.it programmi-mediaset Default",
                "source": "showScreenSet",
                "sdk": "js_latest",
                "authMode": "cookie",
                "pageURL": "https://www.mediasetplay.mediaset.it",
                "format": "jsonp",
                "callback": "gigya.callback",
                "utf8": "&#x2713;"}
        res = self.createRequest("https://login.mediaset.it/accounts.login",post=data)
        s = res.text.strip().replace('gigya.callback(','',1)
        if s[-1:] ==';':
            s= s[:-1]
        if s[-1:] ==')':
            s= s[:-1]
        jsn = json.loads(s)
        if jsn['errorCode'] != 0:
            self.log('Login with user data failed', 4)
            return False
        self.__UID = jsn['UID']
        self.__UIDSignature = jsn['UIDSignature']
        self.__signatureTimestamp = jsn['signatureTimestamp']
        return self.__getAPIKeys(True)

    def anonymousLogin(self):
        return self.__getAPIKeys()

    def __getAPIKeys(self, login=False):
        if login:
            data = {"platform": "pc",
                    "UID": self.__UID,
                    "UIDSignature": self.__UIDSignature,
                    "signatureTimestamp": self.__signatureTimestamp,
                    "appName": "web/mediasetplay-web/bd16667" }
            url = "https://api-ott-prod-fe.mediaset.net/PROD/play/idm/account/login/v1.0"
        else:
            data = {"cid": "dc4e7d82-89a5-4a96-acac-d3c7f2ca6d67",
                    "platform": "pc",
                    "appName": "web/mediasetplay-web/576ea90" }
            url = "https://api-ott-prod-fe.mediaset.net/PROD/play/idm/anonymous/login/v1.0"
        res = self.SESSION.post(url,json=data,verify=False)
        jsn = res.json()
        if not jsn['isOk']:
            return False
        
        self.apigw = res.headers['t-apigw']
        self.cts = res.headers['t-cts']
        self.setHeader('t-apigw',self.apigw)
        self.setHeader('t-cts',self.cts)
        self.__tracecid=jsn['response']['traceCid']
        self.__cwid=jsn['response']['cwId']
        self.log('Retrieved keys successfully', 4)
        return True
        
    def __getResponseFromUrl(self,url,format=False):
        self.login()
        if format:
            url = url.format(traceCid=self.__tracecid,cwId=self.__cwid)
        data = self.getJson(url)
        if 'response' in data:
            return data['response']
        return data
    
    def __getEntriesFromUrl(self,url,format=False):
        return self.__getResponseFromUrl(url)['entries']
    
    def __getpagesFromUrl(self,url,page=0):
        url+= "&page={page}"
        if (page!=0):
            return self.__getEntriesFromUrl(url.format(page=page))
        els=[]
        while (True):
            page +=1
            data = self.__getResponseFromUrl(url.format(page=page))
            els.extend(data['entries'])
            if data['hasMore'] == False:
                return els
    
    def __getsectionsFromEntryID(self,id):
        self.__getAPISession()
        jsn = self.getJson("https://api.one.accedo.tv/content/entry/{id}?locale=it".format(id=id))
        id = quote(",".join(jsn["components"]))
        return self.getJson("https://api.one.accedo.tv/content/entries?id={id}&locale=it".format(id=id))['entries']
        
    def __createAZUrl(self,categories=[],inonda=None,pageels=1000):
        url= "https://api-ott-prod-fe.mediaset.net/PROD/play/rec/azlisting/v1.0?"
        els = { "query": "*:*",
                "hitsPerPage": pageels }
        if categories:
            els["categories"] = ",".join(categories)
        if inonda != None:
            els["inOnda"] = str(inonda).lower()
        return url + urlencode(els)
    
    def OttieniTutto(self,inonda=None,page=0):
        self.log('Trying to get the full program list', 4)
        return self.__getpagesFromUrl(self.__createAZUrl(inonda=inonda),page)
        
    def OttieniTuttiProgrammi(self,inonda=None,page=0):
        self.log('Trying to get the tv program list', 4)
        return self.__getpagesFromUrl(self.__createAZUrl(["Programmi Tv"], inonda),page)
        
    def OttieniTutteFiction(self,inonda=None,page=0):
        self.log('Trying to get the fiction list', 4)
        return self.__getpagesFromUrl(self.__createAZUrl(["Fiction"], inonda),page)
        
    def OttieniGeneriFiction(self):
        self.log('Trying to get the fiction sections list', 4)
        return self.__getsectionsFromEntryID("5acfcb3c23eec6000d64a6a4")
        
    def OttieniFilm(self,inonda=None,page=0):
        self.log('Trying to get the movie list', 4)
        return self.__getpagesFromUrl(self.__createAZUrl(["Cinema"], inonda),page)        
        
    def OttieniGeneriFilm(self):
        self.log('Trying to get the movie sections list', 4)
        return self.__getsectionsFromEntryID("5acfcbc423eec6000d64a6bb")
    
    def OttieniKids(self,inonda=None,page=0):
        self.log('Trying to get the kids list', 4)
        return self.__getpagesFromUrl(self.__createAZUrl(["Kids"], inonda),page)        
        
    def OttieniGeneriKids(self):
        self.log('Trying to get the kids sections list', 4)
        return self.__getsectionsFromEntryID("5acfcb8323eec6000d64a6b3")
    
    def OttieniDocumentari(self,inonda=None,page=0):
        self.log('Trying to get the movie list', 4)
        return self.__getpagesFromUrl(self.__createAZUrl(["Documentari"], inonda),page)        
        
    def OttieniGeneriDocumentari(self):
        self.log('Trying to get the movie sections list', 4)
        return self.__getsectionsFromEntryID("5bfd17c423eec6001aec49f9")
    
    def OttieniProgrammiGenere(self,id, page=0):
        self.log('Trying to get the programs from section id ' + id, 4)
        return self.__getEntriesFromUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/rec/cataloguelisting/v1.0?traceCid={traceCid}&platform=pc&cwId={cwId}&uxReference="+id,format=True)

    def OttieniStagioni(self,seriesId):
        self.log('Trying to get the seasons from series id ' + seriesId, 4)
        return self.__getEntriesFromUrl("https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-tv-seasons/feed?bySeriesId={seriesId}&sort=tvSeasonNumber|desc".format(seriesId=seriesId))

    def OttieniSezioniProgramma(self,brandId):
        self.log('Trying to get the sections from brand id ' + brandId, 4)
        return self.__getEntriesFromUrl(url="https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-brands?byCustomValue={brandId}{" + brandId + "}&sort=mediasetprogram$order")
        
    def OttieniVideoSezione(self,subBrandId):
        self.log('Trying to get the videos from section ' + subBrandId, 4)
        return self.__getEntriesFromUrl(url="https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs?byCustomValue={subBrandId}{" + subBrandId + "}&sort=mediasetprogram$publishInfo_lastPublished|desc")
        
    def OttieniCanaliLive(self):
        self.log('Trying to get the live channels list', 4)
        return self.__getEntriesFromUrl('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-stations?sort=ShortTitle')

    def OttieniDatiVideo(self,url):
        text = self.getText(url)
        res = { 'url': '', 'pid': '', 'type':'', 'security': False}
        root = ET.fromstring(text)
        for vid in root.findall('.//{http://www.w3.org/2005/SMIL21/Language}switch'):
            ref = vid.find('./{http://www.w3.org/2005/SMIL21/Language}ref')
            res['url'] = ref.attrib['src']
            res['type'] = ref.attrib['type']
            if 'security' in ref.attrib and ref.attrib['security'] =='commonEncryption':
                res['security'] = True
            par = ref.find('./{http://www.w3.org/2005/SMIL21/Language}param[@name="trackingData"]')
            if par is not None:
                for item in par.attrib['value'].split('|'):
                    [attr, value] = item.split('=',1)
                    if attr=='pid':
                        res['pid'] = value
                        break
            break
        return res
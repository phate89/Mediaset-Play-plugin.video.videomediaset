import urllib
import urllib2
import json
import re
import math
from bs4 import BeautifulSoup

class Mediaset:

    def get_prog_root(self):
    
        url = "http://www.video.mediaset.it/programma/game15.json"
        data = json.load(urllib2.urlopen(url))
        return data["programmi"]["group"]

    def get_prog_epList(self, url):

        arrdata = []
        url = url.replace("http://www.video.mediaset.it","")
        url = "http://www.video.mediaset.it%s" % (url)
        response = urllib2.urlopen(url)
        html = response.read()
        response.close()

        matches = re.search(r'<div class=.+video-([fF]ull|fep).+js_boxvideo.+data-area="(.+)".+data-box="(.+)".+data-items="(.+)".+data-strip=".+_(.+)".+data-template.+data-type="(.+)">',html)
        try:
            programma = matches.group(2)
            stagione = matches.group(3)
            maxres = int(matches.group(4))
            strip = matches.group(5)
            tipo = matches.group(6)
            
        except:
            return arrdata

        totres = 0
        count = 0
        page = 1
        totpage = 0
        url = "http://www.video.mediaset.it/%s/%s/%s.shtml" % (tipo,programma,stagione)

        while (count < maxres):
            nurl = "%s?page=%s&dim=%s" % (url,page,strip)
            response = urllib2.urlopen(nurl)
            html = response.read()
            response.close()
            if (totres == 0):
                try:
                    matches = re.search(r'<div class="box.+data-maxitem="([0-9]+)">',html)
                    totres = int(matches.group(1))
                    maxres = totres
                    totpage = math.ceil(float(totres) / float(strip))
                except:
                    break

            matches = re.findall(r'<div class="box.+data-id="([^"]+)"[\s\S]*?<figure class="imgBox[\s\S]*?<a data-type.+title="([^"]+)".+href="([^"]+)".+data-src="([^"]+)"[\s\S]*?<p class="descr">([\s\S]*?)<',html)
            for res in matches:
                
                tmp = str(BeautifulSoup(res[1]))
                a = {'id': res[0],'titolo':tmp,'thumbs':res[3].replace("176x99","640x360"),'desc':res[4]}
                arrdata.append(a);
                count = count +1

            page = page +1
            if page > totpage: break;

        return arrdata

    def get_prog_seasonList(self, url):

        arrdata = []
        url = url.replace("http://www.video.mediaset.it","")
        url = "http://www.video.mediaset.it%s" % (url)
        response = urllib2.urlopen(url)
        html = response.read()
        response.close()
        matches = re.search(r'href="#">Stagione</a>[\s\S]*?<ul>([\s\S]*?)</ul>',html)
        try:
            seasonHtml = matches.group(1)
        except:
            return arrdata
        

        matches = re.findall(r'<li>[\s\S]*?<a href="([^"]+)".+title="([^"]+)"',seasonHtml)

        for res in matches:
                
            tmp = str(BeautifulSoup(res[1]))
            a = {'url': res[0],'titolo':tmp}
            arrdata.append(a)

        return arrdata

    def get_global_epList(self,mode,range):

        arrdata = []
        if mode == 0: 
            url = "http://www.video.mediaset.it/bacino/bacinostrip_1.shtml?page=all"
        elif mode == 1:
            url = "http://www.video.mediaset.it/piu_visti/piuvisti-%s.shtml?page=all" % range

        response = urllib2.urlopen(url)
        html = response.read()
        response.close()
      
        matches = re.findall(r'<div class="box ([^"]+)"[\s\S]*?<figure class="imgBox[\s\S]*?<a data-type.+title="([^"]+)".+href=.+full.+([0-9][0-9][0-9][0-9][0-9][0-9]).+html".+data-src="([^"]+)"[\s\S]*?<h3 class="brand">[\s\S]*?title="([^"]+)"[\s\S]*?<p class="descr">([\s\S]*?)<',html)
        for res in matches:
            
            tmp = "%s - %s" % (res[4],res[1])    
            tmp = str(BeautifulSoup(tmp))
            a = {'id': res[2],'titolo':tmp,'tipo':res[0],'thumbs':res[3].replace("176x99","640x360"),'desc':res[5]}
            arrdata.append(a);

        return arrdata


    def get_sport_epList(self):

        arrdata = []
        url = "http://www.video.mediaset.it/bacino/bacinostrip_5.shtml?page=all"
        response = urllib2.urlopen(url)
        html = response.read()
        response.close()
      
        matches = re.findall(r'<figure class="imgBox[\s\S]*?<a data-type.+title="([^"]+)".+href="([^"]+)".+data-src="([^"]+)"[\s\S]*?</h3>[\s\S]*?href=.+([0-9][0-9][0-9][0-9][0-9][0-9])[\s\S]*?<p class="descr">([\s\S]*?)<',html)
        for res in matches:
            
            tmp = str(BeautifulSoup(res[0]))
            a = {'id': res[3],'titolo':tmp,'tipo':res[1],'thumbs':res[2].replace("176x99","640x360"),'desc':res[4]}
            arrdata.append(a);

        return arrdata


    def get_canali_live(self):
        
        url = "http://live1.msf.ticdn.it/Content/HLS/Live/Channel(CH%sHA)/Stream(04)/index.m3u8"
        tmb = "https://raw.githubusercontent.com/aracnoz/videomediaset_logo/master/%s.png"

        arrdata = []

        arrdata.append({'titolo':"Canale 5", 'url':url % ('01'),'desc':"",'thumbs':tmb % ("Canale_5")})
        arrdata.append({'titolo':"Italia 1", 'url':url % ('02'),'desc':"",'thumbs':tmb % ("Italia_1")})
        arrdata.append({'titolo':"Rete 4", 'url':url % ('03'),'desc':"",'thumbs':tmb % ("Rete_4")})
        arrdata.append({'titolo':"La 5", 'url':url % ('04'),'desc':"",'thumbs':tmb % ("La_5")})
        arrdata.append({'titolo':"Italia 2", 'url':url % ('05'),'desc':"",'thumbs':tmb % ("Italia_2")})
        arrdata.append({'titolo':"Iris", 'url':url % ('06'),'desc':"",'thumbs':tmb % ("Iris")})
        arrdata.append({'titolo':"Top Crime", 'url':url % ('07'),'desc':"",'thumbs':tmb % ("Top_Crime")})
        arrdata.append({'titolo':"Premium Extra", 'url':url % ('08'),'desc':"",'thumbs':tmb % ("Premium_Extra")})
        arrdata.append({'titolo':"Mediaset Extra", 'url':url % ('09'),'desc':"",'thumbs':tmb % ("Mediaset_Extra")})

        return arrdata

    def get_stream(self, id):

        url = "http://cdnselector.xuniplay.fdnames.com/GetCDN.aspx?streamid=%s&format=json" % (id)

        response = urllib2.urlopen(url)
        html = response.read()
        response.close()

        html = html.replace('(','')
        html = html.replace(')','')
        data = json.loads(html)

        stream = {"wmv":"","mp4":""}
        for vlist in data["videoList"]:
            print "videomediaset: streams %s" % vlist
            if ( vlist.find("/wmv2/") > 0): stream["wmv"] = vlist
            if ( vlist.find("/mp4/") > 0): stream["mp4"] = vlist

        return stream
from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse
from .models import *
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from .models import *
from .tasks import *


def homeview(request):
    games = Game.objects.all()
    data = {
        'games': games,
        'title': 'Home: odds comparision',
    }
    return render(request, 'home.html', data)


def udpatesports(request):
    update_games()
    return redirect('home')

def udpatematch(request,id):
    BMLIST = Bookmarker.objects.values_list('BMID','name')
    BMLIST = [ list(item) for item in BMLIST]
    BMIDLIST = [item[0] for item in BMLIST]
    BMNAMELIST = [item[1] for item in BMLIST]
    timestamp = round((datetime.now()-timedelta(minutes=59)).timestamp() * 1000)
    session = requests.Session()
    session.trust_env = False
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36', 'content-type': 'application/xhtml+xml'}
    endpoint = f'https://xml.sportspunter.com/xml?username=bmalpass&password=malpass82&since={ timestamp }&cid={ id }'
    res = session.get(endpoint, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')

    comid = id
    try:
        country = soup.select('competition')[0].get('country')
    except Exception as e:
        country = ''
    try:
        sport = soup.select('competition')[0].get('sport')
    except Exception as e:
        sport = ''
    try:
        league = soup.select('competition')[0].get('league')
    except Exception as e:
        league = ''
    matches = {}
    for m in soup.select('match'):
        ht = m.select('hometeam')[0].text
        at = m.select('awayteam')[0].text
        tp = m.select('timeplayed')[0].text
        match_name = ht + ' vs ' + at
        Match_Winner_odds = []
        for item in m.select('odds bm'):
            bookmarker = item.get('id')
            try:
                bookmarker = BMNAMELIST[BMIDLIST.index(int(bookmarker))]
            except Exception as e:
                bookmarker = item.get(id)
            try:
                ho = item.select('ho')[0].text
            except Exception as e:
                ho = ''
            try:
                xo = item.select('xo')[0].text
            except Exception as e:
                xo = ""
            try:
                ao = item.select('ao')[0].text
            except Exception as e:
                ao = ''
            total = 0
            if ho != "":
                total += float(ho)
            if xo != "":
                total += float(xo)
            if ao != "":
                total += float(ao)
            total =total/100
            total = format(total,'.2f')
            Match_Winner_odds.append([bookmarker,ho,xo,ao,total])

        if len(Match_Winner_odds) > 0:
            Match_Winner_odds.insert(0, ['Match Winner', ht, 'Draw', at, 'Market %'])
            Match_Winner_odds = list(map(list, zip(*Match_Winner_odds)))
        else:
            Match_Winner_odds=[]
        matches[match_name] = [ht, at, tp, Match_Winner_odds]

    context={
        'matches': matches,
        'country': country,
        'league': league,
        'sport': sport,
        'comid': comid,
    }
    return JsonResponse(context)

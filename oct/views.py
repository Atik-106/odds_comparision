from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from .models import *
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from .models import *

def homeview(request):
    games = Game.objects.all()
    data = {
        'games': games,
        'title': 'Home',
    }
    return render(request, 'home.html', data)


def udpatematch(request,id):
    BMLIST = Bookmarker.objects.values_list('BMID','name')
    BMLIST = [ list(item) for item in BMLIST]
    BMIDLIST = [item[0] for item in BMLIST]
    BMNAMELIST = [item[1] for item in BMLIST]
    timestamp = round((datetime.now()-timedelta(minutes=5)).timestamp() * 1000)
    session = requests.Session()
    session.trust_env = False
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36', 'content-type': 'application/xhtml+xml'}
    endpoint = f'https://xml.sportspunter.com/xml?username=bmalpass&password=malpass82&since={ timestamp }&cid={ id }'
    res = session.get(endpoint, headers=headers, timeout=5)
    soup = BeautifulSoup(res.content, 'html.parser')
    matches = {}
    outrights = []
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
    for m in soup.select('match'):
        ht = m.select('hometeam')[0].text
        at = m.select('awayteam')[0].text
        tp = m.select('timeplayed')[0].text
        match_name = ht + ' vs ' + at
        for tag in m.find_all():
            if 'odds' in tag.name:
                odds_data = []
                for row in tag.select('bm'):
                    mid = row.get('id')
                    mid = BMNAMELIST[BMIDLIST.index(int(mid))]
                    for opt in row.find_all():
                        if opt.name != 'sel':
                            opt_name = opt.name
                            try:
                                odd_val = opt.text
                            except Exception as e:
                                odd_val = ''
                            odds_data.append([mid, opt_name, odd_val])
        odds_data.sort()
        matches[match_name]=[ht,at,tp,odds_data]
    for outright in soup.select('outrights market'):
        market_name = outright.get('name')
        for opt in outright.select('sel'):
            opt_name = opt.get('name')
            for item in opt.select('bm'):
                oid = item.get('id')
                oid = BMNAMELIST[BMIDLIST.index(int(oid))]
                oovalue = item.select('o')[0].text
                outrights.append([market_name,oid,opt_name, oovalue])


    context={
        'matches': matches,
        'outrights': outrights,
        'country': country,
        'league': league,
        'sport': sport,
        'comid': comid,
    }
    return JsonResponse(context)

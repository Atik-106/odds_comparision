from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from .models import *
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from .models import *
from .tasks import *


def homeview(request):
    update_games()
    games = Game.objects.all()
    data = {
        'games': games,
        'title': 'Home: odds comparision',
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
    res = session.get(endpoint, headers=headers)
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
        BL = [item[0] for item in odds_data]
        BL = list(set(BL))
        OL = [item[1] for item in odds_data]
        OL = list(set(OL))
        master_list = []
        for o in OL:
            x = [o]
            for b in BL:
                total = 0
                for l in odds_data:
                    if l[0] == b and l[1] == o and l[2] != '':
                        total += float(l[2].strip())
                x.append(format(total, '.2f'))
            master_list.append(x)
        lr = []
        i = 0
        for col in BL:
            i += 1
            lrtotal = 0
            for item in master_list:
                if item[i] != '':
                    lrtotal += (float(item[i])/100)
            lr.append(format(lrtotal, '.2f'))
        BL.insert(0,"")
        master_list.insert(0,BL)
        lr.insert(0,'Market %')
        master_list.append(lr)
        matches[match_name]=[ht,at,tp,master_list]
    for outright in soup.select('outrights market'):
        market_name = outright.get('name')
        for opt in outright.select('sel'):
            opt_name = opt.get('name')
            for item in opt.select('bm'):
                oid = item.get('id')
                oid = BMNAMELIST[BMIDLIST.index(int(oid))]
                oovalue = item.select('o')[0].text
                outrights.append([market_name,oid,opt_name, oovalue])

    outright_markets = [item[0] for item in outrights]
    outright_markets = list(set(outright_markets))
    outright_markets = [item for item in outright_markets if item is not None]

    master_list_outright = {}
    for m in outright_markets:
        outright_BL = [item[1] for item in outrights if item[0] == m]
        outright_BL = list(set(outright_BL))
        outright_OL = [item[2] for item in outrights if item[0] == m]
        outright_OL = list(set(outright_OL))

        market_table= []
        for o in outright_OL:
            x = [o]
            for b in outright_BL:
                total = 0
                for l in outrights:
                    if l[0] == m and l[1] == b and l[2] == o and l[3] != '':
                        total += float(l[3].strip())
                x.append(format(total, '.2f'))
            market_table.append(x)
        lr = []
        i = 0
        for col in outright_BL:
            i += 1
            lrtotal = 0
            for item in market_table:
                if item[i] != '':
                    lrtotal += (float(item[i]) / 100)
            lr.append(format(lrtotal, '.2f'))
        outright_BL.insert(0, "")
        market_table.insert(0, outright_BL)
        lr.insert(0, 'Market %')
        market_table.append(lr)
        master_list_outright[m]=market_table
    context={
        'matches': matches,
        'outrights': master_list_outright,
        'country': country,
        'league': league,
        'sport': sport,
        'comid': comid,
    }
    return JsonResponse(context)


def update_games():
    import requests
    from bs4 import BeautifulSoup
    from .models import Game, Competition
    from django.shortcuts import get_object_or_404
    session = requests.Session()
    session.trust_env = False
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36', 'content-type': 'application/xhtml+xml'}
    endpoint = 'https://xml.sportspunter.com/xml?function=getcompetitionlist'

    res = session.get(endpoint, headers=headers)
    data =BeautifulSoup(res.content,'html.parser')

    # updating games
    games = []
    comlist = data.select('competition')
    for g in comlist:
        game_name=g.get('sport')
        if game_name not in games:
            games.append(game_name)
    Game.objects.all().delete()
    Game.objects.bulk_create(Game(name=item) for item in games)

    # updating competition
    competitions = []
    for c in comlist:
        name = c.get('leaguename')
        cid = c.get('id')
        sport = c.get('sport')
        if [name,cid,sport] not in competitions:
            competitions.append([name,cid,sport])
    Competition.objects.all().delete()
    competition_object=[]
    for item in competitions:
        g = Game.objects.get(name=item[2])
        obj = Competition(name=item[0], com_id=item[1], game_name=g)
        competition_object.append(obj)

    Competition.objects.bulk_create(competition_object)


def test():
    from datetime import datetime,timedelta
    timestamp = round((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)
    id = 37
    url = f'https://xml.sportspunter.com/xml?username=bmalpass&password=malpass82&since={ timestamp }&cid={ id }'
    print(url)
    print(timestamp)
import requests
import resources as res
from bs4 import BeautifulSoup
from flask import Flask, current_app, render_template
from flask_cors import CORS
from Player import Player
import json


# Create the application instance
app = Flask(__name__, template_folder='frontpage')
CORS(app)
player = Player()



def getValorantGameUpdates():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    URL = "https://api.henrikdev.xyz/valorant/v1/website/en-us?filter=game_updates"
    response = requests.get(URL, headers=headers)
    return response.json()


def getValorantRank(Region, Name, Tag):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    URL = "https://api.henrikdev.xyz/valorant/v2/mmr/" + Region + "/" + Name + "/" + Tag
    response = requests.get(URL, headers=headers)
    return response.json()

# Read the swagger.yml file to configure the endpoints
# app.add_api('swagger.yml')

def news():
    banner = ""
    title = ""
    url = ""
    responseJSON = getValorantGameUpdates()
    # JSON Results Mapping
    banner = responseJSON['data'][0]['banner_url']
    title = responseJSON['data'][0]['title']
    url = responseJSON['data'][0]['url']
    return "Latest VALORANT Patchnotes: " + url


def rank_check(Region: str = "", Name: str = "", Tag: str = ""):
    # Valortant stat calls
    apiResponse = getValorantRank(Region, Name, Tag)
    # VALORANT EPISODE 2 ACT 2
    rank_number = apiResponse['data']['by_season']['e2a2']['final_rank']
    # elo = apiResponse =['data']['current_data']['elo'];
    status = apiResponse['status']
    rank_tier = res.ranks[str(rank_number)]

    if status == '200':
        return str(rank_tier)
    elif status == '451':
        message = apiResponse = ['message']
        return message

def GetStats(name: str = "", tag: str = "", type: str = "") -> Player:
    URL = 'https://tracker.gg/valorant/profile/riot/' + \
        name + '%23' + tag + '/overview?playlist=' + type
    page = requests.get(URL)

    #with open("page.html", "wb") as f:
    #    f.write(page.content)

    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id='app')

    # Initialise Player
    player = Player()
    player.damage.kda = float(results.find_all(
        'span', class_='valorant-highlighted-stat__value')[-1].text)  # Get KDA

    # Get the 4 big stats from main page
    big_stats = results.find('div', class_='giant-stats')
    stats = []
    for stat in big_stats.find_all('div', class_='numbers'):
        stats.append(stat.find('span', class_='value').text)

    # Extract Stats from big 4
    player.damage.dmg = float(stats[0])
    player.damage.kd = float(stats[1])
    player.damage.headshotRate = float(stats[2])
    player.game.winRate = float(stats[3][:-1])

    # Get the main 8 stats
    main_stats = results.find('div', class_="main")
    stats = []
    for stat in main_stats.find_all('div', class_='numbers'):
        stats.append(stat.find('span', class_='value').text.replace(',', ''))

    # Extract stats from the main 8
    player.game.wins = int(stats[0])
    player.damage.kills = int(stats[1])
    player.damage.Headshots = int(stats[2])
    player.damage.deaths = int(stats[3])
    player.damage.assists = int(stats[4])
    player.game.scorePerRound = float(stats[5])
    player.damage.killsPerRound = float(stats[6])
    player.game.firstBlood = int(stats[7])
    player.game.ace = int(stats[8])
    player.game.clutch = int(stats[9])
    player.game.flawless = int(stats[10])
    player.game.mostKills = int(stats[11])

    # Get table of top 3 agents
    agent_stats = results.find('div', class_='top-agents__table-container')
    rows = agent_stats.next.find_all('tr')
    # Remove top label row
    rows.pop(0)
    for i in range(len(rows)):
        row = rows[i]
        player.agents[i].name = row.find('span', class_='agent__name').text
        data = row.find_all('span', class_='name')
        player.agents[i].time = data[0].text
        player.agents[i].matches = int(data[1].text)
        player.agents[i].winRate = float(data[2].text[:-1])
        player.agents[i].kd = float(data[3].text)
        player.agents[i].dmg = float(data[4].text)

    player.game.playtime = results.find('span', class_='playtime').text.strip()[:-10]
    player.game.matches = int(results.find('span', class_='matches').text.strip()[:-8])

    # Get table of accuracy stats
    if type != "escalation":
      accuracy_stats = results.find('div', class_='accuracy__content')
      rows = accuracy_stats.find_all('tr')
      stats = []
      for row in rows:
          data = row.find_all('span', 'stat__value')
          stats.append(data)

      player.accuracy.headRate = float(stats[0][0].text[:-1])
      player.accuracy.head = int(stats[0][1].text)
      player.accuracy.bodyRate = float(stats[1][0].text[:-1])
      player.accuracy.body = int(stats[1][1].text)
      player.accuracy.legRate = float(stats[2][0].text[:-1])
      player.accuracy.leg = int(stats[2][1].text)

    weapon_stats = results.find('div', class_='top-weapons__weapons')
    weapons = results.find_all('div', class_='weapon')
    for i in range(len(weapons)):
        weapon = weapons[i]
        player.weapons[i].name = weapon.find('div', class_='weapon__name').text
        player.weapons[i].type = weapon.find('div', class_='weapon__type').text
        stats = weapon.find_all('span', class_='stat')
        player.weapons[i].headRate = int(stats[0].text[:-1])
        player.weapons[i].bodyRate = int(stats[1].text[:-1])
        player.weapons[i].legRate = int(stats[2].text[:-1])
        player.weapons[i].kills = int(weapon.find('span', class_='value').text.replace(',', ''))
        pass

    if type == 'competitive':
        rank_stats = results.find_all('span', class_='valorant-highlighted-stat__value')[0].text

        api = {
            "rank": rank_stats,
            "kda": player.damage.kda,
            'damage': player.damage.dmg,
            'kd': player.damage.kd,
            'headshot_percentage': player.damage.headshotRate,
            'win_percentage': player.game.winRate,
            "wins": player.game.wins,
            "kills": player.damage.kills,
            "headshots": player.damage.Headshots,
            "deaths": player.damage.deaths,
            "assists": player.damage.assists,
            "scorePerRound": player.game.scorePerRound,
            "killsPerRound": player.damage.killsPerRound,
            "firstBlood": player.game.firstBlood,
            "ace": player.game.ace,
            "clutch": player.game.clutch,
            "flawless": player.game.flawless,
            "mostKills": player.game.mostKills,
            "accuracy_HeadRate": player.accuracy.headRate,
            "accuracy_Head":player.accuracy.head,
            "accuracy_bodyRate":player.accuracy.bodyRate ,
            "accuracy_body":player.accuracy.body,
            "accuracy_legRate":player.accuracy.legRate,
            "accuracy_leg":player.accuracy.leg
        }

        segments = {
            "segments": api
        }

        data = {
          "data": segments
        }
    elif type == 'unrated':
        api = {
            "kda": player.damage.kda,
            'damage': player.damage.dmg,
            'kd': player.damage.kd,
            'headshot_percentage': player.damage.headshotRate,
            'win_percentage': player.game.winRate,
            "wins": player.game.wins,
            "kills": player.damage.kills,
            "headshots": player.damage.Headshots,
            "deaths": player.damage.deaths,
            "assists": player.damage.assists,
            "scorePerRound": player.game.scorePerRound,
            "killsPerRound": player.damage.killsPerRound,
            "firstBlood": player.game.firstBlood,
            "ace": player.game.ace,
            "clutch": player.game.clutch,
            "flawless": player.game.flawless,
            "mostKills": player.game.mostKills,
            "accuracy_HeadRate": player.accuracy.headRate,
            "accuracy_Head":player.accuracy.head,
            "accuracy_bodyRate":player.accuracy.bodyRate ,
            "accuracy_body":player.accuracy.body,
            "accuracy_legRate":player.accuracy.legRate,
            "accuracy_leg":player.accuracy.leg
        }

        segments = {
            "segments": api
        }

        data = {
          "data": segments
        }
    elif type == 'escalation':

        api = {
            "kda": player.damage.kda,
            'damage': player.damage.dmg,
            'kd': player.damage.kd,
            'headshot_percentage': player.damage.headshotRate,
            'win_percentage': player.game.winRate,
            "wins": player.game.wins,
            "kills": player.damage.kills,
            "headshots": player.damage.Headshots,
            "deaths": player.damage.deaths,
            "assists": player.damage.assists,
            "scorePerRound": player.game.scorePerRound,
            "killsPerRound": player.damage.killsPerRound,
            "firstBlood": player.game.firstBlood,
            "ace": player.game.ace,
            "clutch": player.game.clutch,
            "flawless": player.game.flawless,
            "mostKills": player.game.mostKills
        }

        segments = {
            "segements": api
        }

        data = {
          "data": segments
        }


    return data


@app.route('/')
def test():
    return render_template('index.html')
# Create a URL route in our application for '/'


@app.route('/news')
def home():
    return news()


@app.route('/rank/<Region>/<Name>/<Tag>')
def rank(Region, Name, Tag):
    return rank_check(Region, Name, Tag)

@app.route("/stats/<name>/<tag>/<type>")
def v1(name,tag,type):
  return current_app.response_class(json.dumps(GetStats(name,tag,type), indent=4), mimetype="application/json")


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

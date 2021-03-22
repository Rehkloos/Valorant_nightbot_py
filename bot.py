import requests
import resources as res
from flask import Flask, render_template


# Create the application instance
app = Flask(__name__, template_folder='frontpage')


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


banner = ""
title = ""
url = ""
responseJSON = getValorantGameUpdates()
# JSON Results Mapping
banner = responseJSON['data'][0]['banner_url']
title = responseJSON['data'][0]['title']
url = responseJSON['data'][0]['url']


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


@app.route('/')
def test():
    return render_template('index.html')
# Create a URL route in our application for '/'


@app.route('/news')
def home():
    return "Latest VALORANT Patchnotes: " + url


@app.route('/rank/<Region>/<Name>/<Tag>')
def rank(Region, Name, Tag):
    return rank_check(Region, Name, Tag)


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

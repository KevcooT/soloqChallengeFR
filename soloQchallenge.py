import discord
from discord.ext import tasks
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, time
import sqlite3
import aiohttp  
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
from datetime import datetime, timezone, timedelta

# Load environment variables from .env file
load_dotenv()

# Get keys and tokens from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_KEY_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Discord bot setup
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# Data structure to store player data
players = [
    {'alias':'4zr', 'puuid': '', 'summoner_name': '4zr#soloq', 'team':'Kameto', 'streamer_name': '4zrr'},
    {'alias':'Caliste', 'puuid': '', 'summoner_name': 'MOMO KOZUKI#soloq', 'team':'Kameto', 'streamer_name': 'caliste_lol'},
    {'alias':'Kameto','puuid':'','summoner_name':'panaris négligé#soloq', 'team':'Kameto', 'streamer_name': 'kamet0'},
    {'alias':'Manaty','puuid':'','summoner_name':'TUEUR EN SERIE#soloq', 'team':'Kameto', 'streamer_name': 'manatylol'},
    {'alias':'Potent','puuid':'','summoner_name':'Potent#SoloQ', 'team':'Kameto', 'streamer_name': 'potent213'},
    {'alias':'Rin','puuid':'','summoner_name':'rinwi#soloq', 'team':'Kameto', 'streamer_name': 'rin_ad'},
    {'alias':'Saken','puuid':'','summoner_name':'SAKEN#soloq', 'team':'Kameto', 'streamer_name': 'saken_lol'},
    {'alias':'Sixen','puuid':'','summoner_name':'SUCE1Q#soloq', 'team':'Kameto', 'streamer_name': 'sixentv'},
    {'alias':'Slipix','puuid':'','summoner_name':'MORGANAI ENJOYER#SoloQ', 'team':'Kameto', 'streamer_name': 'slipix'},
    {'alias':'Vespa','puuid':'','summoner_name':'Fleur#SOLOQ', 'team':'Kameto', 'streamer_name': 'vespalol'},
    {'alias':'Wao','puuid':'','summoner_name':'KAMETO BIG BOSS#soloq', 'team':'Kameto', 'streamer_name': 'waolol1'},
    {'alias':'Zongo','puuid':'','summoner_name':'ZONGOAT#soloq', 'team':'Kameto', 'streamer_name': 'zongoled0z0'},
    {'alias':'Badlulu','puuid':'','summoner_name':'Badlulu#soloq', 'team':'Tiky', 'streamer_name': 'badluluu'},
    {'alias':'Boukada','puuid':'','summoner_name':'Boukada#soloq', 'team':'Tiky', 'streamer_name': 'boukadaaa'},
    {'alias':'Evalunna','puuid':'','summoner_name':'MADELINE ARGY#soloq', 'team':'Tiky', 'streamer_name': 'evalunna'},
    {'alias':'Gaëthan','puuid':'','summoner_name':'CHASSE A LHOMME#soloq', 'team':'Tiky', 'streamer_name': 'gaethaaan'},
    {'alias':'GoB GG','puuid':'','summoner_name':'GoB GG#soloq', 'team':'Tiky', 'streamer_name': 'gobgg'},
    {'alias':'Isma','puuid':'','summoner_name':'isma#soloq', 'team':'Tiky', 'streamer_name': 'ismaaalol'},
    {'alias':'Joinze','puuid':'','summoner_name':'Joinze#soloq', 'team':'Tiky', 'streamer_name': 'joinzelol'},
    {'alias':'Kamiloo','puuid':'','summoner_name':'Leao mid acc#soloq', 'team':'Tiky', 'streamer_name': 'kamiloo_lol'},
    {'alias':'Narkuss','puuid':'','summoner_name':'Fiddle lover#soloq', 'team':'Tiky', 'streamer_name': 'narkuss_lol'},
    {'alias':'Sayn','puuid':'','summoner_name':'Sayn#soloq', 'team':'Tiky', 'streamer_name': 'sayn_loll'},
    {'alias':'Tiky','puuid':'','summoner_name':'Ester Exposito#soloq', 'team':'Tiky', 'streamer_name': 'tikyjr'},
    {'alias':'Vetheo','puuid':'','summoner_name':'Oriøn#soloq', 'team':'Tiky', 'streamer_name': 'vetheo'},
    {'alias':'Adam','puuid':'','summoner_name':'GODS#soloq', 'team':'Wakz', 'streamer_name': 'ricadam_lol'},
    {'alias':'Aos Si','puuid':'','summoner_name':'Meff 0 to hero#soloq', 'team':'Wakz', 'streamer_name': 'aos_sith'},
    {'alias':'Blue','puuid':'','summoner_name':'EL BARAKI#soloq', 'team':'Wakz', 'streamer_name': 'BlueEG7'},
    {'alias':'Chap','puuid':'','summoner_name':'Chap#soloq', 'team':'Wakz', 'streamer_name': 'chap_gg'},
    {'alias':'Cosmïc','puuid':'','summoner_name':'Cosmïc#soloq', 'team':'Wakz', 'streamer_name': 'cosmiicc_'},
    {'alias':'Hiro','puuid':'','summoner_name':'Arthur Perticoz#soloq', 'team':'Wakz', 'streamer_name': 'hiro_llol'},
    {'alias':'Kitano','puuid':'','summoner_name':'Kitano#soloq', 'team':'Wakz', 'streamer_name': 'kitano_lol'},
    {'alias':'Skewmond','puuid':'','summoner_name':'Davy Jones#soloq', 'team':'Wakz', 'streamer_name': 'skewmond_lol'},
    {'alias':'Stend','puuid':'','summoner_name':'Stend#soloq', 'team':'Wakz', 'streamer_name': 'stend_lol'},
    {'alias':'Stormax','puuid':'','summoner_name':'Stormax#soloq', 'team':'Wakz', 'streamer_name': 'stormax28'},
    {'alias':'Strey','puuid':'','summoner_name':'STREY#soloq', 'team':'Wakz', 'streamer_name': 'strey_lol'},
    {'alias':'Wakz','puuid':'','summoner_name':'DIV2 NEXT ADKING#soloq', 'team':'Wakz', 'streamer_name': 'wakzlol'},
    {'alias':'Chreak','puuid':'','summoner_name':'CLODO CALIBRÉ#soloq', 'team':'Trayton', 'streamer_name': 'chreak'},
    {'alias':'Eika','puuid':'','summoner_name':'Eika#soloq', 'team':'Trayton', 'streamer_name': 'eikap'},
    {'alias':'Exakick','puuid':'','summoner_name':'Docteur Exakick#soloq', 'team':'Trayton', 'streamer_name': 'exakicklol'},
    {'alias':'Matias','puuid':'','summoner_name':'Matias VEINEUX#soloq', 'team':'Trayton', 'streamer_name': 'matiaslaclasse'},
    {'alias':'Myrtus','puuid':'','summoner_name':'Abatteur2kafard#soloq', 'team':'Trayton', 'streamer_name': 'myrtus_lol'},
    {'alias':'Nuc','puuid':'','summoner_name':'Hérisson Diplomé#soloq', 'team':'Trayton', 'streamer_name': 'nuclearintt'},
    {'alias':'Rhobalas','puuid':'','summoner_name':'Letron Jaimes#soloq', 'team':'Trayton', 'streamer_name': 'rhobalas_lol'},
    {'alias':'Splinter','puuid':'','summoner_name':'Splinter#soloq', 'team':'Trayton', 'streamer_name': 'splinter'},
    {'alias':'Trayton','puuid':'','summoner_name':'Trayton#soloq', 'team':'Trayton', 'streamer_name': 'traytonlol'},
    {'alias':'Veignorem','puuid':'','summoner_name':'Veignorem#soloq', 'team':'Trayton', 'streamer_name': 'veignorem'},
    {'alias':'Walou','puuid':'','summoner_name':'Walou Bien Galbé#soloq', 'team':'Trayton', 'streamer_name': 'walou'},
    {'alias':'Zicssi','puuid':'','summoner_name':'Zicssi#soloq', 'team':'Trayton', 'streamer_name': 'zicssi'},
    {'alias':'Nisqy','puuid':'','summoner_name':'RATSQSY#FROST', 'team':'Kameto', 'streamer_name': 'nisqyy'}
]

tierRankValues = {
	    'UNRANKED': { 'IV': 900 },        
	    'IRON': { 'IV': 1000, 'III': 1100, 'II': 1200, 'I': 1300 },
        'BRONZE': { 'IV': 1400, 'III': 1500, 'II': 1600, 'I': 1700 },
        'SILVER': { 'IV': 1800, 'III': 1900, 'II': 2000, 'I': 2100 },
        'GOLD': { 'IV': 2200, 'III': 2300, 'II': 2400, 'I': 2500 },
        'PLATINUM': { 'IV': 2600, 'III': 2700, 'II': 2800, 'I': 2900 },
        'EMERALD' : { 'IV': 3000, 'III': 3100, 'II': 3200, 'I': 3300 },
        'DIAMOND': { 'IV': 3400, 'III': 3500, 'II': 3600, 'I': 3700 },
        'MASTER': { 'I': 3800 },
        'GRANDMASTER': { 'I': 3800 },
        'CHALLENGER': { 'I': 3800 }
    }

twitterHandles = {'Isma': '@ismaa_lol', 'Joinze': '@Joinzelol', 'Trayton': '@TraYt0N', '4zr': '@oh4zr', 'Gaëthan': '@Gaethaaan', 'Vetheo': '@Vetheo_lol', 'Skewmond': '@SkewMond_09', 'Exakick': '@Exakicklol', 'Nisqy': '@Nisqy', 'Matias': '@matiaslaclasse1', 'Potent': '@Potent213', 'Badlulu': '@badlullu', 'Eika': '@Eikalol', 'Zicssi': '@zicssiflay', 'Saken': '@Saken_lol', 'Nuc': '@Nuclear_int', 'Caliste': '@CalisteLoL', 'Strey': '@Streyito', 'Sayn': '@lol_saynnn', 'Blue': '@BlueEG7', 'Stormax': '@Stormax28', 'Hiro': '@Hiro_LoL9', 'Adam': '@Ricadam_lol', 'Splinter': '@MrSplinterlol', 'Vespa': '@Vespa_LOL', 'Myrtus': '@Myrtus_Lol', 'Zongo': '@Zongolol', 'Manaty': '@Manaty_LoL', 'Tiky': '@tikylol', 'Chreak': '@Chreak_Lol', 'Chap': '@Chap_GG', 'Slipix': '@slipixlol', 'Rin': '@adcRin', 'GoB GG': '@GoB_GG', 'Stend': '@Stend_lol', 'Wao': '@Waolol', 'Walou': '@GarouWalou', 'Boukada': '@Boukadaaa', 'Narkuss': '@NarkussLol', 'Kamiloo': '@Kamiloo_LoL', 'Kitano': '@Kitano_LoL', 'Sixen': '@SixenTv', 'Wakz': '@Wakzlol', 'Rhobalas': '@Rhobalasv2', 'Cosmïc': '@cosmiic_lol', 'Evalunna': '@EvalunnaTV', 'Aos Si': '@Aos_Sith', 'Veignorem': '@Veignorem_lol', 'Kameto': '@Kammeto'} 


# Helper function to handle Riot API requests with improved rate limiting
async def riot_api_request(url):
    headers = {'X-Riot-Token': RIOT_API_KEY}
    max_retries = 5
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 429:  # Rate limit hit
                        retry_after = int(response.headers.get('Retry-After', 1))
                        print(f"Rate limit hit. Retrying after {retry_after} seconds.")
                        await asyncio.sleep(retry_after + 1)
                    else:
                        response.raise_for_status()
                        return await response.json()
        except aiohttp.ClientError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise e
    raise Exception("Max retries reached")


def init_db():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS soloqchallenge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        player TEXT,
        wins INTEGER,
        losses INTEGER,
        tier TEXT,
        rank TEXT,
        league_points INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT,
        puuid TEXT,
        player_id TEXT,
        summoner_name TEXT,
        team TEXT,
        streamer_name TEXT
        calculatedRankValue INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS remadeGames (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matchId TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        player TEXT,
        matchId TEXT,
        kills INTEGER,
        soloKills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        tripleKills INTEGER,
        quadraKills INTEGER,
        pentaKills INTEGER,
        pushPings INTEGER,
        championName TEXT,
        firstBloodKill INTEGER,
        enemyTeamEarlySurrender INTEGER,
        goldEarned INTEGER,
        individualPosition TEXT,
        largestKillingSpree INTEGER,
        teamEarlySurrendered INTEGER,
        teamPosition TEXT,
        totalDamageDealtToChampions INTEGER,
        totalMinionsKilled INTEGER,
        totalTimeSpentDead INTEGER,
        totalTimeSpentAlive INTEGER,
        win INTEGER,
        loss INTEGER,
        csPerMinute FLOAT  
    )
    ''')
    conn.commit()
    conn.close()


async def fetch_puuids():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    for player in players:
        summoner_name, tagline = player['summoner_name'].split("#")
        tagline = tagline.lower()

        # Fetch PUUID using Riot ID
        url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tagline}"
        try:
            riot_id_info = await riot_api_request(url)
            player['puuid'] = riot_id_info['puuid']

            # Fetch id using PUUID
            url_account = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{player['puuid']}"
            account_info = await riot_api_request(url_account)
            player['id'] = account_info['id']

            # Check if alias exists in the table
            cursor.execute('SELECT * FROM players WHERE alias = ?', (player['alias'],))
            existing_player = cursor.fetchone()

            if existing_player:
                # Update the existing player's PUUID
                cursor.execute('''
                UPDATE players
                SET puuid = ?, player_id = ?, summoner_name = ?, team = ?, streamer_name = ?
                WHERE alias = ?
                ''', (player['puuid'], player['id'], player['summoner_name'], player['team'], player['streamer_name'], player['alias']))
            else:
                # Insert new player
                cursor.execute('''
                INSERT INTO players (alias, puuid, player_id, summoner_name, team, streamer_name)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (player['alias'], player['puuid'], player['id'], player['summoner_name'], player['team'], player['streamer_name']))
            
            conn.commit()
        except Exception as e:
            print(f"Error fetching PUUID for {player['alias']}: {e}")
    conn.close()


async def fetch_rank_data():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()  

    cursor.execute('SELECT * FROM players')
    db_players = cursor.fetchall()
    
    for player in db_players:        
        alias, puuid, player_id, summoner_name, team, streamer_name = player[1:7]
        if not puuid:
            continue  # Skip if PUUID is not available
        
        # Fetch ranked data
        url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{player_id}"
        try:
            ranked_info = await riot_api_request(url)
            if ranked_info:
                soloq_info = next((queue for queue in ranked_info if queue['queueType'] == 'RANKED_SOLO_5x5'), None)
                if soloq_info:
                    wins = soloq_info['wins']
                    losses = soloq_info['losses']
                    tier = soloq_info['tier']
                    rank = soloq_info['rank']
                    if alias == "Nuc":
                        league_points = soloq_info['leaguePoints'] + 25
                    elif alias == "Nisqy":
                        league_points = soloq_info['leaguePoints'] + 22
                    else:
                        league_points = soloq_info['leaguePoints']
                else:
                    wins, losses, tier, rank, league_points = await fetch_unranked_data(puuid)
            else:
                wins, losses, tier, rank, league_points = await fetch_unranked_data(puuid)

            cursor.execute('''
            INSERT INTO soloqchallenge (time, player, wins, losses, tier, rank, league_points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (now, alias, wins, losses, tier, rank, league_points))

            #add calculated rank value to players
            calculatedRankValue = tierRankValues[tier][rank] + league_points
            cursor.execute('''
                UPDATE players
                 SET calculatedRankValue = ?
                WHERE puuid = ?;
            ''', (calculatedRankValue, puuid))
            conn.commit()

        except Exception as e:
            print(f"Error fetching rank data for {alias}: {e}")

    conn.commit()
    conn.close()


async def fetch_unranked_data(puuid):
    matchListUrl = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start=0&count=5"
    matchList = await riot_api_request(matchListUrl)
    if not matchList:
        return 0, 0, "UNRANKED", "IV", 0
    
    wins = losses = 0
    for match in matchList:
        matchUrl = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match}"
        matchData = await riot_api_request(matchUrl)
        for participant in matchData['info']['participants']:
            if participant['puuid'] == puuid:
                if participant['win']:
                    wins += 1
                else:
                    losses += 1
    
    return wins, losses, "UNRANKED", "IV", 0


async def fetch_match_history(puuid, player_alias):
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    cursor.execute("SELECT time FROM stats WHERE player = ? ORDER BY time desc", (player_alias,))
    t=round(int(cursor.fetchall()[1][0])/1000)
    start = 0
    count = 100


    while True:
        matchHistoryUrl = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={t}&queue=420&start={start}&count={count}"
        matchHistory = await riot_api_request(matchHistoryUrl)

        if not matchHistory:
            continue

        for match_id in matchHistory:
                # Check if match_id already exists in stats table for player
            cursor.execute("SELECT COUNT(*) FROM stats WHERE matchId = ? AND player = ?", (match_id, player_alias))
            if cursor.fetchone()[0] > 0:
                continue

                # Check if match_id is in the remadeGame table
            cursor.execute("SELECT COUNT(*) FROM remadeGames WHERE matchId = ?", (match_id,))
            if cursor.fetchone()[0] > 0:
                print(f'{player_alias} game {match_id} was a remake, skipping')
                continue

            match_details = await fetch_match_details(match_id)
            is_remade = any(participant['gameEndedInEarlySurrender'] for participant in match_details['info']['participants'])
            if is_remade:
                print(f'{player_alias} game {match_id} was a remake, skipping -- added to table')
                cursor.execute("INSERT INTO remadeGames (matchId) VALUES (?)", (match_id,))
                continue  # Skip remade games

            cursor.execute("SELECT puuid FROM players")
            player_puuids = [row[0] for row in cursor.fetchall()]

            for participant in match_details['info']['participants']:
                if participant['puuid'] in player_puuids:
                        # Get the player_alias for the current participant
                    cursor.execute("SELECT alias FROM players WHERE puuid = ?", (participant['puuid'],))
                    current_player_alias = cursor.fetchone()[0]
                    insert_match_data(cursor, match_details, participant, current_player_alias)
                    print(f"Match {match_id} inserted for {current_player_alias}")
        
        start += count
        conn.commit() 
        break



async def fetch_match_details(match_id):
    matchDetailsUrl = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    return await riot_api_request(matchDetailsUrl)


def insert_match_data(cursor, match_details, participant, player_alias):
    timeSpentAlive = match_details['info']['gameDuration'] - participant['totalTimeSpentDead']
    win = 1 if participant['win'] else 0
    loss = 1 - win
    teamEarlySurrendered = 1 if participant['teamEarlySurrendered'] else 0
    enemyTeamEarlySurrender = 1 if participant['gameEndedInEarlySurrender'] and not participant['teamEarlySurrendered'] else 0
    totalMinionsKilled = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
    csPerMinute = totalMinionsKilled / (match_details['info']['gameDuration']/60)
    
    try:
        cursor.execute('''
        INSERT INTO stats (time, player, matchId, kills, soloKills, deaths, assists, tripleKills, quadraKills, pentaKills, 
                           pushPings, championName, firstBloodKill, enemyTeamEarlySurrender, goldEarned, individualPosition, 
                           largestKillingSpree, teamEarlySurrendered, teamPosition, totalDamageDealtToChampions, 
                           totalMinionsKilled, totalTimeSpentDead, totalTimeSpentAlive, win, loss, csPerMinute)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match_details['info']['gameStartTimestamp'], player_alias, match_details['metadata']['matchId'], 
              participant['kills'], participant['challenges']['soloKills'], participant['deaths'], participant['assists'], 
              participant['tripleKills'], participant['quadraKills'], participant['pentaKills'], participant['pushPings'], 
              participant['championName'], participant['firstBloodKill'], enemyTeamEarlySurrender, participant['goldEarned'], 
              participant['individualPosition'], participant['largestKillingSpree'], teamEarlySurrendered, 
              participant['teamPosition'], participant['totalDamageDealtToChampions'], totalMinionsKilled, 
              participant['totalTimeSpentDead'], timeSpentAlive, win, loss, csPerMinute))
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        print(f"Failed to insert data for match {match_details['metadata']['matchId']} and player {player_alias}")
   

# Authenticate with Twitter API
def twitConnection(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN):
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET,
    )
    return client

def twitConnectionv1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)

client = twitConnection(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN)
client_v1 = twitConnectionv1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Function to post a tweet with text and an image
async def post_daily_snapshot():
    client = twitConnection(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN)
    client_v1 = twitConnectionv1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    text = await get_best_performers()
    image_path = f'endResults/snapshots/snapshot.png' 
    try:
        # Run getDayImage.py
        subprocess.run(["python", "getDayImage.py"], check=True)
        
        # Post tweet with image
        myMedia = image_path
        media = client_v1.simple_upload(filename=myMedia)
        media_id = media.media_id
        client.create_tweet(text=text,media_ids=[media_id])
        print(f"Tweet posted successfully at {datetime.now()}")
    except subprocess.CalledProcessError as e:
        print(f"Error running getDayImage.py: {e}")
    except Exception as e:
        print(f"Error posting tweet: {e}")

async def post_portrait_tweet():
    client = twitConnection(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN)
    client_v1 = twitConnectionv1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    today = datetime.now(timezone(timedelta(hours=2))).strftime("%Y-%m-%d")
    today2 = datetime.now(timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M")
    print(f"{today} // {today2}")
    text = f'SoloQ Challenge leaderboard 👇'    
    try:
        # Run getDayImage.py
        subprocess.run(["python", "getPortraitFormat.py"], check=True)
        image_path = 'endResults/hourlyUpdate/soloq_challenge_leaderboard.png'
        # Post tweet with image
        myMedia = image_path
        media = client_v1.simple_upload(filename=myMedia)
        media_id = media.media_id
        client.create_tweet(text=text,media_ids=[media_id])
        print(f"Tweet posted successfully at {datetime.now()}")
    except subprocess.CalledProcessError as e:
        print(f"Error running getDayImage.py: {e}")
    except Exception as e:
        print(f"Error posting tweet: {e}")

# Get best/worst performers of the day
async def get_best_performers():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT time FROM soloqchallenge ORDER by time desc")
    result = cursor.fetchall()
    previous_time = result[48][0]
    current_time = result[0][0]
    previous_values = {}
    current_values = {}
    delta_values = {}

    cursor.execute("""
        SELECT player, tier, rank, league_points, wins, losses
        FROM soloqchallenge
        WHERE time = ?
    """, (previous_time,))
    previous_data = cursor.fetchall()

    for player, tier, rank, lp, wins, losses in previous_data:
        rank_value = tierRankValues[tier][rank] + lp
        winrate = round(wins/(wins+losses)*100)
        previous_values[player] = rank_value, wins, losses, winrate

    cursor.execute("""
        SELECT player, tier, rank, league_points, wins, losses
        FROM soloqchallenge
        WHERE time = ?
    """, (current_time,))
    current_data = cursor.fetchall()

    for player, tier, rank, lp, wins, losses in current_data:
        rank_value = tierRankValues[tier][rank] + lp
        winrate = round(wins/(wins+losses)*100)
        current_values[player] = rank_value, wins, losses, winrate

    for player in current_values:
        rank_value_delta = current_values.get(player)[0] - previous_values.get(player)[0]
        wins_value_delta = current_values.get(player)[1] - previous_values.get(player)[1]
        losses_value_delta = current_values.get(player)[2] - previous_values.get(player)[2]
        if losses_value_delta == wins_value_delta == 0:
            winrate_value_day = 0
        elif losses_value_delta == 0:
            winrate_value_day = 100
        else:
            winrate_value_day = round(wins_value_delta / (wins_value_delta + losses_value_delta)*100)
        delta_values[player] = rank_value_delta, wins_value_delta, losses_value_delta, winrate_value_day


    # Player with most LP
    most_lp_won = max(delta_values.items(), key=lambda x: x[1][0])

    # Player with most LP loss
    most_lp_lost = min(delta_values.items(), key=lambda x: x[1][0])

    # Player with highest winrate
    highest_winrate_player = max(delta_values.items(), key=lambda x: x[1][3])

    text = f'Snapshot du SoloQ Challenge à minuit 🕴️ \n Résumé de la journée 👇 \n Meilleur gain de LP: {twitterHandles.get(most_lp_won[0])}: +{most_lp_won[1][0]} LP 📈 \n Pire perte de LP: {twitterHandles.get(most_lp_lost[0])}: {most_lp_lost[1][0]} LP 📉 \n Meilleur winrate: {twitterHandles.get(highest_winrate_player[0])}: {highest_winrate_player[1][3]}% ({highest_winrate_player[1][1]}W / {highest_winrate_player[1][2]}L)🎯'
    conn.close()
    return text


# Periodic task to fetch and log data every 30mn
@tasks.loop(minutes=30)
async def scheduled_update():
    await fetch_rank_data()
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("BOTERINO EVOLVE")
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puuid, alias FROM players WHERE puuid IS NOT NULL AND puuid != ''")
    players = cursor.fetchall()

    for puuid, alias in players:
        await fetch_match_history(puuid, alias)
    conn.close()
    await channel.send("HISTORY FETCHED")

# Bot startup
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    #init_db() 
    #await fetch_puuids()
    scheduled_update.start()  # Start the periodic task
    """
    # Schedule daily snapshot at midnight
    @tasks.loop(hours=24)
    async def daily_snapshot():
        await post_daily_snapshot()

    # Schedule portrait tweets every 6 hours
    @tasks.loop(hours=6)
    async def portrait_tweet():
        await post_portrait_tweet()

    await asyncio.sleep(60)
    portrait_tweet.start() 
    await asyncio.sleep(43200)
    daily_snapshot.start()
    """
# Run bot
bot.run(DISCORD_BOT_TOKEN)
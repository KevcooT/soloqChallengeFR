import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
import subprocess
import sqlite3

load_dotenv()
# Twitter API credentials
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_KEY_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

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
def post_daily_snapshot():
    client = twitConnection(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN)
    client_v1 = twitConnectionv1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    text = get_best_performers()
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

def post_portrait_tweet():
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

# Schedule to post every day
def schedule_tweet():
    scheduler = BlockingScheduler()
    scheduler.add_job(post_daily_snapshot, 'cron', hour=1, minute=1)  # Triggers every day at 00:01
    scheduler.add_job(post_portrait_tweet, 'cron', hour='1,7,13,19', minute=1)  # Runs every 6 hours, starting at midnight
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler is stopping...")
        scheduler.shutdown(wait=False)  # Gracefully shutdown the scheduler
        print("Scheduler has been stopped.")

# Get best/worst performers of the day
def get_best_performers():
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
            0
        elif losses_value_delta == 0:
            100
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


if __name__ == "__main__":
    schedule_tweet()
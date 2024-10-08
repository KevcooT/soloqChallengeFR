from flask import Flask, render_template, jsonify
import sqlite3


app = Flask(__name__)

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
        'GRANDMASTER': { 'I': 3900 },
        'CHALLENGER': { 'I': 4000 }
    }

masterPlusTierRankValues = {
            'UNRANKED': { 'IV': -3100 },        
            'GOLD': { 'IV': -1600, 'III': -1500, 'II': -1400, 'I': -1300 },
            'PLATINUM': { 'IV': -1200, 'III': -1100, 'II': -1000, 'I': -900 },
            'EMERALD' : { 'IV': -800, 'III': -700, 'II': -600, 'I': -500 },
            'DIAMOND': { 'IV': -400, 'III': -300, 'II': -200, 'I': -100 },
            'MASTER': { 'I': 0 },
            'GRANDMASTER': { 'I': 0 },
            'CHALLENGER': { 'I': 0 }
    }

team_colors = {
        'Kameto': '#0000FF',   # Team Kameto (Blue)
        'Tiky': '#008000',     # Team Tiky (Green)
        'Wakz': '#800080',     # Team Wakz (Purple)
        'Trayton': '#FFA500',  # Team Trayton (Orange)
    }

# Player to team mapping
player_teams = {
        '4zr': 'Kameto', 'Caliste': 'Kameto', 'Kameto': 'Kameto', 'Manaty': 'Kameto',
        'Potent': 'Kameto', 'Rin': 'Kameto', 'Saken': 'Kameto', 'Sixen': 'Kameto',
        'Slipix': 'Kameto', 'Vespa': 'Kameto', 'Wao': 'Kameto', 'Zongo': 'Kameto',
        'Badlulu': 'Tiky', 'Boukada': 'Tiky', 'Evalunna': 'Tiky', 'Gaëthan': 'Tiky',
        'GoB GG': 'Tiky', 'Isma': 'Tiky', 'Joinze': 'Tiky', 'Kamiloo': 'Tiky',
        'Narkuss': 'Tiky', 'Sayn': 'Tiky', 'Tiky': 'Tiky', 'Vetheo': 'Tiky',
        'Adam': 'Wakz', 'Aos Si': 'Wakz', 'Blue': 'Wakz', 'Chap': 'Wakz',
        'Cosmïc': 'Wakz', 'Hiro': 'Wakz', 'Kitano': 'Wakz', 'Skewmond': 'Wakz',
        'Stend': 'Wakz', 'Stormax': 'Wakz', 'Strey': 'Wakz', 'Wakz': 'Wakz',
        'Chreak': 'Trayton', 'Eika': 'Trayton', 'Exakick': 'Trayton', 'Matias': 'Trayton',
        'Myrtus': 'Trayton', 'Nuc': 'Trayton', 'Rhobalas': 'Trayton', 'Splinter': 'Trayton',
        'Trayton': 'Trayton', 'Veignorem': 'Trayton', 'Walou': 'Trayton', 'Zicssi': 'Trayton',
        'Nisqy': 'Tiky'
    }

def get_data():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT time, player, wins, losses, tier, rank, league_points
        FROM soloqchallenge
        ORDER BY time ASC
    ''')
    data = cursor.fetchall()
    conn.close()

    processed_data = {}
    for row in data:
        time, player, wins, losses, tier, rank, league_points = row
        rank_val = tierRankValues[tier][rank] + league_points

        team = player_teams.get(player)
        color = team_colors.get(team, '#000000')

        if player not in processed_data:
            processed_data[player] = {'data': [], 'color': color}
        processed_data[player]['data'].append({
            'time': time,
            'rank_val': rank_val,
            'tier': tier,
            'rank': rank,
            'leaguePoints': league_points,
            'team': team
        })
        
    
    chart_data = []
    for player, info in processed_data.items():
        dataset = {
            'label': player,
            'backgroundColor': info['color'],
            'borderColor': info['color'],
            'data': [{
                'x': entry['time'],
                'y': entry['rank_val'],
                'tier': entry['tier'],
                'rank': entry['rank'],
                'leaguePoints': entry['leaguePoints'],
                'rank_val': entry['rank_val'],
                'team':entry['team']
            } for entry in info['data']]
        }
        chart_data.append(dataset)

    return chart_data

def get_top_players():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT player, wins, losses, tier, rank, league_points
        FROM soloqchallenge
        WHERE time = (SELECT MAX(time) FROM soloqchallenge)
    ''')
    data = cursor.fetchall()
    conn.close()


    player_data = []
    for player, wins, losses, tier, rank, league_points in data:
        rank_val = tierRankValues[tier][rank] + league_points
        win_ratio = wins / (wins + losses) if wins + losses > 0 else 0
        player_data.append({
            'player': player,
            'rank_val': rank_val,
            'tier': tier,
            'rank': rank,
            'league_points': league_points,
            'wins': wins,
            'losses': losses,
            'win_ratio': win_ratio
        })
    
    sorted_players = sorted(player_data, key=lambda x: (x['rank_val'], x['win_ratio']), reverse=True)
    return sorted_players[:3]

def get_all_players():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT player, wins, losses, tier, rank, league_points
        FROM soloqchallenge
        WHERE time = (SELECT MAX(time) FROM soloqchallenge)
    ''')
    data = cursor.fetchall()
    conn.close()


    player_data = []
    for player, wins, losses, tier, rank, league_points in data:
        rank_val = tierRankValues[tier][rank] + league_points
        win_ratio = round(wins / (wins + losses)*100) if wins + losses > 0 else 0
        team = player_teams[player]
        player_data.append({
            'player': player,
            'rank_val': rank_val,
            'tier': tier,
            'rank': rank,
            'league_points': league_points,
            'wins': wins,
            'losses': losses,
            'win_ratio': win_ratio,
            'team': team
        })
    
    sorted_players = sorted(player_data, key=lambda x: (x['rank_val'], x['win_ratio']), reverse=True)
    return sorted_players


def get_team_data():
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT time, player, tier, rank, league_points
        FROM soloqchallenge
        ORDER BY time ASC
    ''')
    data = cursor.fetchall()
    conn.close()

    team_data = {team: {'data': [], 'color': color} for team, color in team_colors.items()}

    for row in data:
        time, player, tier, rank, league_points = row
        team = player_teams.get(player)
        if team:
            master_plus_val = masterPlusTierRankValues[tier][rank] + league_points
            if player == 'Nisqy':
                master_plus_val -= 1560
            
            team_entry = next((x for x in team_data[team]['data'] if x['x'] == time), None)
            if team_entry:
                team_entry['y'] += master_plus_val
            else:
                team_data[team]['data'].append({
                    'x': time,
                    'y': master_plus_val
                })

    return [
        {
            'label': team,
            'backgroundColor': info['color'],
            'borderColor': info['color'],
            'data': sorted(info['data'], key=lambda x: x['x'])
        }
        for team, info in team_data.items()
    ]


@app.route('/')
def index():
    top_players = get_top_players()
    all_players = get_all_players()
    return render_template('index.html', top_players=top_players, all_players=all_players)


@app.route('/data')
def data():
    return jsonify(get_data())


@app.route('/team_data')
def team_data():
    return jsonify(get_team_data())

if __name__ == '__main__':
    app.run(debug=True)
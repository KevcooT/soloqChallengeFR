from datetime import datetime, timezone
import sqlite3
import time
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import tempfile
import pandas as pd
from matplotlib import dates as mdates

position_mapping = {
    'TOP': 'Top',
    'JUNGLE': 'Jungle',
    'MIDDLE': 'Mid',
    'BOTTOM': 'Bot',
    'UTILITY': 'Support'
}

def generate_stats_image(player_alias, player_team, streamer_name):
    background = Image.open("static/assets/background.jpeg").resize((1920, 1080))
    draw = ImageDraw.Draw(background)
    
    # Load Riot Games' theme fonts
    title_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 48)
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 36)
    text_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 28)
    
    # Define Riot Games' gold color palette
    colors = {
        'gold': '#C8AA6E',
        'gold_light': '#F0E6D2',
        'gold_dark': '#785A28',
        'gold_muted': '#C8AA6E80',
        'white': '#FFFFFF'
    }
    
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    
    # First section
    draw_text(draw, page_title, (1665, 240), title_font, colors['gold'])
    draw_player_info(draw, background, player_alias, player_team, title_font, header_font, (50, 50), cursor, colors)
    draw_rank_info(draw, background, cursor, player_alias, header_font, (350, 50), colors)
    draw_rank_chart(background, cursor, player_alias, (700, 50), colors)
    draw_soloq_challenge_logo(background, (1650, 50))
    
    # Match highlights
    draw_match_highlights(draw, background, cursor, player_alias, text_font, (50, 300), colors)
    
    # Winrates and champs
    draw_top_champions(draw, background, cursor, player_alias, text_font, (50, 500), colors)
    draw_role_winrates(draw, background, cursor, player_alias, text_font, (50, 750), colors)
    
    # Info
    draw_info_section(draw, background, cursor, player_alias, streamer_name, text_font, (750, 500), colors)
    
    # Head to head
    generate_faced_report(draw, background, cursor, player_alias, text_font, (1300, 440), colors)
    
    conn.close()
    
    background.save(f"endResults/{player_alias}_stats.png")

def draw_text(draw, text, position, font, text_color):
    draw.text(position, text, font=font, fill=text_color)

def draw_player_info(draw, background, player_alias, player_team, title_font, header_font, position, cursor, colors):

    player_image = Image.open(f"static/assets/{player_alias}.png")
    player_image = player_image.resize((200, 200))
    

    bordered_image = Image.new('RGBA', (204, 204), colors['gold'])
    bordered_image.paste(player_image, (2, 2), player_image.convert('RGBA'))
    

    fine_print_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 16)
    fine_print_text = "Made with love by KevcooT"
    fine_print_position = (position[0], position[1] - 18)  
    draw.text(fine_print_position, fine_print_text, font=fine_print_font, fill=colors['white'])
    
    background.paste(bordered_image, position, bordered_image)
    
    # End rank
    cursor.execute("""
    SELECT time, player, tier, rank, league_points 
    FROM soloqchallenge 
    ORDER BY time
    """)
    all_data = cursor.fetchall()

    player_ranks = {}
    for time, player, tier, rank, lp in all_data:
        if player not in player_ranks:
            player_ranks[player] = []
        player_ranks[player].append((datetime.fromisoformat(time), rank_value(tier, rank) + lp/100))

    player_rank_over_time = {player: [] for player in player_ranks}
    all_times = sorted(set([datetime.fromisoformat(time) for time, _, _, _, _ in all_data]))

    for time in all_times:
        ranks_at_time = []
        for player, ranks in player_ranks.items():
            current_ranks = [r for t, r in ranks if t <= time]
            if current_ranks:
                ranks_at_time.append((player, current_ranks[-1]))

        sorted_players_at_time = sorted(ranks_at_time, key=lambda x: x[1], reverse=True)

        for rank_position, (player, _) in enumerate(sorted_players_at_time, start=1):
            player_rank_over_time[player].append((time, rank_position))

    player_rank_progression = player_rank_over_time[player_alias]
    final_rank = player_rank_progression[-1][1]    
    # Player alias, rank, and team
    if player_alias == "Trayton":
        bone_icon = Image.open("static/assets/bone.png")
        bone_icon = bone_icon.resize((40, 40)) 
        text = f"Trayton "
        text_width = draw.textlength(text, font=title_font)
        draw_text(draw, text, (position[0] + 220, position[1]), title_font, colors['gold_light'])
        background.paste(bone_icon, (position[0] + 220 + int(text_width), position[1] + 15), bone_icon.convert('RGBA'))
        draw_text(draw, f" #{final_rank}", (position[0] + 220 + int(text_width) + 40, position[1]), title_font, colors['gold_light'])
    else:
        draw_text(draw, f"{player_alias} #{final_rank}", (position[0] + 220, position[1]), title_font, colors['gold_light'])
    
    draw_text(draw, f'Team {player_team}', (position[0] + 220, position[1] + 60), header_font, colors['gold_light'])

def draw_rank_info(draw, background, cursor, player_alias, header_font, position, colors):
    cursor.execute("SELECT tier, rank, league_points, wins, losses FROM soloqchallenge WHERE player = ? ORDER BY time DESC LIMIT 1", (player_alias,))
    rank_data = cursor.fetchone()
    if rank_data:
        tier, rank, league_points, wins, losses = rank_data

        rank_image = Image.open(f"static/assets/{tier.lower()}.png")
        rank_image = rank_image.resize((80, 80))
        background.paste(rank_image, (position[0]-80, position[1] + 140), rank_image.convert('RGBA'))
        
        # Win/Loss 
        total_games = wins + losses
        winrate = round(wins / total_games * 100) if total_games > 0 else 0
        win_loss_text = f"{wins}W / {losses}L ({winrate}%)"
        draw_text(draw, win_loss_text, (position[0]-80, position[1] + 110), header_font, colors['gold_light'])
        
        # Rank 
        if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
            rank_text = f"{league_points} LP"
        else:
            rank_text = f"{rank} - {league_points} LP"
        draw_text(draw, rank_text, (position[0] +20, position[1] + 160), header_font, colors['gold_light'])

def generate_rank_chart(player_alias, cursor, colors):
    cursor.execute("""
    SELECT time, player, tier, rank, league_points 
    FROM soloqchallenge 
    ORDER BY time
    """)
    all_data = cursor.fetchall()

    player_ranks = {}
    for time, player, tier, rank, lp in all_data:
        if player not in player_ranks:
            player_ranks[player] = []
        player_ranks[player].append((datetime.fromisoformat(time), rank_value(tier, rank) + lp/100))

    player_rank_over_time = {player: [] for player in player_ranks}
    all_times = sorted(set([datetime.fromisoformat(time) for time, _, _, _, _ in all_data]))

    for time in all_times:
        ranks_at_time = []
        for player, ranks in player_ranks.items():
            current_ranks = [r for t, r in ranks if t <= time]
            if current_ranks:
                ranks_at_time.append((player, current_ranks[-1]))

        sorted_players_at_time = sorted(ranks_at_time, key=lambda x: x[1], reverse=True)

        for rank_position, (player, _) in enumerate(sorted_players_at_time, start=1):
            player_rank_over_time[player].append((time, rank_position))

    player_rank_progression = player_rank_over_time[player_alias]

    plt.figure(figsize=(10, 2.5))
    plt.style.use('dark_background')
    
    times, ranks = zip(*player_rank_progression)
    plt.plot(times, ranks, linewidth=2, color=colors['gold_light'])

    plt.title(f"Challenge Rank Over Time", fontsize=16, fontweight='bold', color=colors['gold'])
    plt.xlabel('Time', fontsize=12, color=colors['gold_light'], labelpad=-30)
    plt.ylabel('Rank', fontsize=12, color=colors['gold_light'])
    plt.gca().invert_yaxis()

    ax = plt.gca()
    ax.set_facecolor('none')
    ax.grid(True, linestyle='--', alpha=0.3, color=colors['gold_muted'])
    
    # Set the y-axis range from 49 to 1
    ax.set_ylim(50, 0)
    
    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    plt.gcf().autofmt_xdate()

    # Add final rank annotation
    final_rank = player_rank_progression[-1][1]
    total_players = len(player_ranks)
    plt.annotate(f'Rank: {final_rank}/{total_players}', 
                 xy=(player_rank_progression[-1][0], final_rank),
                 xytext=(30, 10), textcoords='offset points',
                 color=colors['gold'], fontweight='bold')

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        plt.savefig(temp_file.name, format='png', dpi=100, bbox_inches='tight', transparent=True)
        plt.close()
        temp_file.seek(0)

    chart_image = Image.open(temp_file.name)
    return chart_image

def rank_value(tier, rank):
    tiers = ['UNRANKED', 'IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    ranks = ['IV', 'III', 'II', 'I']
    return tiers.index(tier) * 400 + (ranks.index(rank)) * 100

def draw_rank_chart(background, cursor, player_alias, position, colors):
    chart_image = generate_rank_chart(player_alias, cursor, colors)
    background.paste(chart_image, position, chart_image.convert('RGBA'))

def draw_soloq_challenge_logo(background, position):
    logo = Image.open("static/assets/soloqchallenge.png")
    logo = logo.resize((200, 200))
    background.paste(logo, position, logo.convert('RGBA'))

def draw_match_highlights(draw, background, cursor, player_alias, font, position, colors):
    cursor.execute("""
    SELECT 
        (SELECT championName FROM stats WHERE player = ? ORDER BY kills DESC LIMIT 1) as champion_most_kills,
        MAX(kills) as most_kills,
        (SELECT championName FROM stats WHERE player = ? ORDER BY deaths DESC LIMIT 1) as champion_most_deaths,
        MAX(deaths) as most_deaths,
        (SELECT championName FROM stats WHERE player = ? ORDER BY assists DESC LIMIT 1) as champion_most_assists,
        MAX(assists) as most_assists,
        (SELECT championName FROM stats WHERE player = ? ORDER BY totalDamageDealtToChampions DESC LIMIT 1) as champion_most_damage,
        MAX(totalDamageDealtToChampions) as most_damage,
        (SELECT championName FROM stats WHERE player = ? ORDER BY largestKillingSpree DESC LIMIT 1) as champion_most_spree,
        MAX(largestKillingSpree) as most_spree
    FROM stats
    WHERE player = ?
    """, (player_alias, player_alias, player_alias, player_alias, player_alias, player_alias))
    
    highlights = cursor.fetchone()
    stats_and_champions = [
        ('Most Kills', highlights[0], highlights[1]),
        ('Most Deaths', highlights[2], highlights[3]),
        ('Most Assists', highlights[4], highlights[5]),
        ('Most Damage', highlights[6], highlights[7]),
        ('Largest Spree', highlights[8], highlights[9]),
    ]
    
    for i, (stat, champion, value) in enumerate(stats_and_champions):
        champ_image = Image.open(f"static/assets/champion/{champion}.png").resize((70, 70))
        img_x, img_y = position[0] + i * 360, position[1]
        background.paste(champ_image, (img_x, img_y), champ_image.convert('RGBA'))
        draw_text(draw, f"{stat}\n{value}", (img_x+80, img_y), font, colors['gold_light'])

def draw_top_champions(draw, background, cursor, player_alias, font, position, colors):
    cursor.execute("""
    SELECT 
        championName, 
        COUNT(*) as games, 
        SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN win = 0 THEN 1 ELSE 0 END) as losses,
        CASE 
            WHEN AVG(deaths) = 0 THEN AVG(kills + assists)
            ELSE AVG(kills + assists) / AVG(deaths)
        END as kda
    FROM stats 
    WHERE player = ?
    GROUP BY championName
    ORDER BY games DESC
    LIMIT 5
    """, (player_alias,))
    
    top_champions = cursor.fetchall()
    
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 36)
    draw_text(draw, "Most played", (position[0], position[1]-100), header_font, colors['gold'])
    
    for i, (champion, games, wins, losses, kda) in enumerate(top_champions):
        champ_image = Image.open(f"static/assets/champion/{champion}.png")
        champ_image.thumbnail((50, 50), Image.Resampling.LANCZOS)
        
        img_x, img_y = position[0], position[1] - 50 + i * 60
        background.paste(champ_image, (img_x, img_y), champ_image if champ_image.mode == 'RGBA' else None)
        
        winrate = (wins / games) * 100 if games > 0 else 0
        draw_text(draw, f"{champion} - {wins}W / {losses}L ({round(winrate)}%), {kda:.2f} KDA", (img_x+60, img_y+5), font, colors['gold_light'])

def draw_info_section(draw, background, cursor, player_alias, streamer_name, font, position, colors):
    cursor.execute("""
    SELECT
        SUM(kills) AS total_kills,
        SUM(deaths) AS total_deaths,
        SUM(assists) AS total_assists,
        SUM(tripleKills) AS total_triple_kills,
        SUM(quadraKills) AS total_quadra_kills,
        SUM(pentaKills) AS total_penta_kills,
        AVG(csPerMinute) AS avg_cs_per_min,
        AVG(goldEarned / ((totalTimeSpentAlive+totalTimeSpentDead) / 60)) AS avg_golds_per_min,
        AVG(totalDamageDealtToChampions / ((totalTimeSpentAlive+totalTimeSpentDead) / 60)) AS avg_damage_per_min,
        SUM(firstBloodKill) AS total_first_bloods,
        SUM(totalTimeSpentDead) AS total_time_spent_dead,
        SUM(totalTimeSpentAlive) AS total_time_spent_alive,
        SUM(enemyTeamEarlySurrender) AS total_enemy_team_early_surrender,
        SUM(pushPings) AS total_push_pings
    FROM stats
    WHERE player = ?
    """, (player_alias,))
    stats = cursor.fetchone()
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 36)  
    draw_text(draw, "Stats", (position[0], position[1]-100), header_font, colors['gold'])
    
    def format_time(seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    total_time_spent_dead = format_time(int(stats[10]))
    total_time_spent_alive = format_time(int(stats[11]))
    
    sword_icon = Image.open("static/assets/sword.png").resize((40, 40))  
    minion_icon = Image.open("static/assets/minion.png").resize((40, 40))
    goldcoins_icon = Image.open("static/assets/goldcoins.png").resize((40, 40))
    push_ping_icon = Image.open("static/assets/push_ping.png").resize((40, 40))
    skull_icon = Image.open("static/assets/skull.png").resize((40, 40))
    heart_icon = Image.open("static/assets/heart.png").resize((40, 40))
    
    icon_stats = [
        (sword_icon, 1, stats[0]),
        (skull_icon, 1, f"{stats[1]} ({total_time_spent_dead})"),
        (heart_icon, 1, stats[2]),
        (sword_icon, 3, stats[3]),
        (sword_icon, 4, stats[4]),
        (sword_icon, 5, stats[5]),
        (sword_icon, 1, f"{stats[8]:.0f}/min"),
        (minion_icon, 1, f"{stats[6]:.2f}/min"),
        (goldcoins_icon, 1, f"{stats[7]:.0f}/min"),
        (push_ping_icon, 1,stats[13])
    ]
    
    
    for i, (icon, count, stat) in enumerate(icon_stats):
        y_position = position[1] - 50 + i * 50
        for j in range(count):
            background.paste(icon, (position[0] + j*35, y_position), icon.convert('RGBA'))
        draw_text(draw, str(stat), (position[0] + count*35 + 15, y_position-4), font, colors['gold_light'])
    if player_alias == "Hiro":
        y_position = position[1] + 450
        corbin_icon = Image.open("static/assets/corbin.png").resize((40, 40))
        background.paste(corbin_icon, (position[0], y_position), corbin_icon)
        draw_text(draw, "-1 (???)",(position[0]+50, y_position), font, colors['gold_light'])
'''
    # Draw Twitch stats
    twitch_stats = get_twitch_stats(streamer_name)
    twitch_y = position[1] + 270
    draw_text(draw, "Stream Stats", (position[0], twitch_y), header_font, colors['gold'])
    
    icon_size = (30, 30)
    icons = [
        Image.open("static/assets/clock.png").resize(icon_size),
        Image.open("static/assets/camera.png").resize(icon_size),
        Image.open("static/assets/eye.png").resize(icon_size),
        Image.open("static/assets/eye.png").resize(icon_size),
        Image.open("static/assets/upw.png").resize(icon_size)
    ]
    
    twitch_lines = [
        (twitch_stats['Total Stream Time'], ""),
        (str(twitch_stats['Unique Stream Days']), "streams"),
        (str(twitch_stats['Average Viewers']), "average"),
        (str(twitch_stats['Peak Viewers']), "peak"),
        (str(twitch_stats['Total Followers Gained']), "followers")
    ]
    
    for i, (icon, (line, suffix)) in enumerate(zip(icons, twitch_lines)):
        icon_x, icon_y = position[0], twitch_y + 50 + i * 35
        background.paste(icon, (icon_x, icon_y), icon.convert('RGBA'))
        
        # Calculate text position to align vertically with the icon
        text_x = icon_x + icon_size[0] + 10
        text_y = icon_y - 5
        
        # Draw the main text and suffix
        draw_text(draw, line, (text_x, text_y), font, colors['gold_light'])
        if suffix:
            suffix_x = text_x + draw.textlength(line, font=font) + 5
            draw_text(draw, suffix, (suffix_x, text_y), font, colors['gold_light'])
'''
def draw_role_winrates(draw, background, cursor, player_alias, font, canvas_position, colors):
    cursor.execute("""
    SELECT 
        individualPosition,
        SUM(win) * 100.0 / COUNT(*) AS win_rate,
        SUM(win) as wins,
        SUM(loss) as losses,
        COUNT(*) as games_played
    FROM stats
    WHERE player = ?
    GROUP BY individualPosition
    ORDER BY games_played DESC
    """, (player_alias,))
    position_win_rates = cursor.fetchall()
    mapped_results = []
    for position, win_rate, wins, losses, games_played in position_win_rates:
        mapped_position = position_mapping.get(position, position)
        mapped_results.append((mapped_position, win_rate, wins, losses, games_played))
    
    x, y = int(canvas_position[0]), int(canvas_position[1])

    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 36)
    draw_text(draw, "Win Rate by Role", (x, y), header_font, colors['gold'])

    for i, (position_name, win_rate, wins, losses, games_played) in enumerate(mapped_results):
        role_image = Image.open(f"static/assets/role/{position_name}.png").resize((50, 50))
        img_x, img_y = x, y + 50 + i * 50
        background.paste(role_image, (img_x, img_y), role_image.convert('RGBA'))
        draw_text(draw, f"{position_name} - {wins}W / {losses}L ({round(win_rate)}%)", (img_x+60, img_y+5), font, colors['gold_light'])

def generate_faced_report(draw, background, cursor, player_alias, font, position, colors):
    cursor.execute("""
    SELECT 
        s2.player AS other_player, 
        s1.win AS player_win,
        s2.win AS other_win
    FROM 
        stats s1 
    JOIN 
        stats s2 ON s1.matchId = s2.matchId AND s1.player != s2.player
    WHERE 
        s1.player = ?
    ORDER BY 
        s1.matchId DESC
    """, (player_alias,))
    
    data = cursor.fetchall()
    if not data:
        return

    df = pd.DataFrame(data, columns=['other_player', 'player_win', 'other_win'])
    df['relationship'] = df.apply(lambda row: 'Ally' if row['player_win'] == row['other_win'] else 'Opponent', axis=1)

    start_x, start_y = position

    # Draw the title
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 36)
    draw_text(draw, "Matchups", (start_x, start_y - 40), header_font, colors['gold'])

    # Draw opponents table
    draw_matchup_table(draw, background, df, font, (start_x, start_y), colors, "Opponents", is_opponent=True)

    # Draw allies table
    draw_matchup_table(draw, background, df, font, (start_x, start_y + 338), colors, "Allies", is_opponent=False)

def draw_matchup_table(draw, background, df, font, position, colors, title, is_opponent):
    start_x, start_y = position

    # Draw the subtitle
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 28)
    draw_text(draw, title, (start_x, start_y), header_font, colors['gold'])

    # Filter data
    relationship = 'Opponent' if is_opponent else 'Ally'
    data_to_draw = df[df['relationship'] == relationship]

    # Draw the player icons
    icon_size = (80, 80)
    icons_per_row = 5
    row_height = 100
    frame_thickness = 4
    for i, row in enumerate(data_to_draw.itertuples()):
        x = start_x + (i % icons_per_row) * (icon_size[0] + 20)
        y = start_y + 40 + (i // icons_per_row) * row_height

        player_image = Image.open(f"static/assets/{row.other_player}.png")
        player_image = player_image.resize(icon_size)

        # Create a new image with a colored frame
        framed_image = Image.new('RGBA', (icon_size[0] + 2*frame_thickness, icon_size[1] + 2*frame_thickness))
        frame_color = (46, 204, 113, 255) if row.player_win else (217, 30, 24, 255)  # Green if won, red if lost
        framed_image.paste(frame_color, [0, 0, framed_image.size[0], framed_image.size[1]])
        framed_image.paste(player_image, (frame_thickness, frame_thickness), player_image.convert('RGBA'))

        background.paste(framed_image, (x - frame_thickness, y - frame_thickness), framed_image.convert('RGBA'))

def get_twitch_stats(streamer_name):
    df = pd.read_csv(r"C:/Python/twitchdata.csv")
    
    # Remove the particle after the day number and convert 'Stream start time' to datetime
    df['Stream start time'] = df['Stream start time'].str.replace(r'(\d+)(st|nd|rd|th)', r'\1', regex=True)
    df['Stream start time'] = pd.to_datetime(df['Stream start time'], format='%A %d %B %Y %H:%M', dayfirst=True)
    
    
    # Rename columns if necessary
    df = df.rename(columns={
        'Stream length (mins)': 'Stream length (mins)',
        'Avg viewers': 'Average viewers',
        'Peak viewers': 'Peak viewers',
        'Followers gained': 'Followers gained'
    })
    
    # Filter the data between Sept 4th and Sept 25th (excluded) 2024
    start_date = datetime(2024, 9, 4)
    end_date = datetime(2024, 9, 25)
    df = df[(df['Stream start time'] >= start_date) & (df['Stream start time'] < end_date)]
    
    # Extract the channel name from the Stream URL and filter for the specific streamer
    df['Channel Name'] = df['Stream URL'].str.split('channel/').str[-1].str.split('/').str[0]
    df = df[df['Channel Name'] == streamer_name.lower()]
    
    # Initialize variables
    total_stream_minutes = 0
    unique_stream_days = set()
    total_viewers = 0
    max_peak_viewers = 0
    total_followers_gained = 0
    stream_count = 0
    
    # Iterate through the DataFrame to calculate
    for _, row in df.iterrows():
        total_stream_minutes += row['Stream length (mins)']
        unique_stream_days.add(row['Stream start time'].date())
        total_viewers += row['Average viewers']
        max_peak_viewers = max(max_peak_viewers, row['Peak viewers'])
        total_followers_gained += row['Followers gained']
        stream_count += 1
    
    # Calculate average viewers
    avg_viewers = total_viewers / stream_count if stream_count > 0 else 0
    
    # Convert total stream minutes to days, hours, minutes format
    days, remaining_minutes = divmod(total_stream_minutes, 24 * 60)
    hours, minutes = divmod(remaining_minutes, 60)
    total_stream_time = f"{days}d {hours}h {minutes}m"
    
    # Return the results as a dictionary
    return {
        'Total Stream Time': total_stream_time,
        'Unique Stream Days': len(unique_stream_days),
        'Average Viewers': round(float(avg_viewers)),
        'Peak Viewers': int(max_peak_viewers),
        'Total Followers Gained': int(total_followers_gained)
    }


def main():
    start = time.time()
    print(start)
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puuid, alias, team, streamer_name FROM players WHERE puuid IS NOT NULL AND puuid != '' ORDER BY calculatedRankValue desc")
    players = cursor.fetchall() 
    print(players)
    for puuid, alias, team, streamer_mane in players:
        time_for_player = time.time()
        generate_stats_image(alias, team, streamer_mane)
        print(f"Stats image generated for {alias}")
        print(f"Time taken: {time.time() - time_for_player} seconds")
    end = time.time()
    print(f"Time taken: {end - start} seconds")

if __name__ == "__main__":
    page_title = input("Enter the page title: ")
    main()
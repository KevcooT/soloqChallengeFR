from datetime import datetime, timezone, timedelta
import sqlite3
import time
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import tempfile
import pandas as pd
from matplotlib import dates as mdates
import os

position_mapping = {
    'TOP': 'Top',
    'JUNGLE': 'Jungle',
    'MIDDLE': 'Mid',
    'BOTTOM': 'Bot',
    'UTILITY': 'Support'
}

tierRankValues = {
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

def calculate_rank_value(tier, rank, league_points):
    return tierRankValues[tier][rank] + league_points

def generate_stats_image():
    background = Image.open("static/assets/finalBackground.png").resize((1920, 1080))
    draw = ImageDraw.Draw(background)
    
    # Load Riot Games' theme fonts
    title_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 48)
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 36)
    text_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 28)
    footer_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 16)
    
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
    
    # Register the calculate_rank_value function with SQLite
    conn.create_function("calculate_rank_value", 3, calculate_rank_value)
    
    # Get the latest timestamp
    cursor.execute("SELECT MAX(time) FROM soloqchallenge")
    latest_time = cursor.fetchone()[0]
    x,y = 0,0
    titlePageText = "Team Ranking"
    name_bbox = title_font.getbbox(titlePageText)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width) // 2
    draw_text(draw, titlePageText, (name_x, y + 25), title_font, colors['gold'])
        
    # Draw gold lines
    line_height = 2
    draw.line([(x + 120, y + 60), (name_x - 20, y + 60)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, y + 60), (background.width - 20, y + 60)], fill=colors['gold'], width=line_height)
    
    # Draw footer
    draw_text(draw, "Made with love by KevcooT",(0, background.height-20), footer_font, colors['gold_light'])
    
    # Draw sections
    draw_icon_and_chart(background, cursor, (0, 0), (800, 100), colors, latest_time)
    draw_team_ranking(draw, background, cursor, header_font, text_font, (50, 150), colors, latest_time)
    draw_top_5_stats(draw, background, cursor, header_font, text_font, (50, 500), colors, latest_time)
    
    conn.close()
    
    background.save(f"endResults/snapshots/snapshot.png")
    background.save(f"endResults/lastDay/teamResult.png")

def draw_text(draw, text, position, font, text_color):
    draw.text(position, text, font=font, fill=text_color)

def draw_icon_and_chart(background, cursor, icon_position, chart_position, colors, latest_time):
    # Draw icon
    icon = Image.open("static/assets/soloqchallenge.png").resize((100, 100))
    background.paste(icon, icon_position, icon.convert('RGBA'))
    
    # Draw chart
    draw_team_rank_chart(background, cursor, chart_position, colors, latest_time)

def draw_team_ranking(draw, background, cursor, header_font, text_font, position, colors, latest_time):
    cursor.execute("""
    SELECT p.team, 
           SUM(s.wins) as total_wins, 
           SUM(s.losses) as total_losses,
           SUM(CASE 
               WHEN p.alias = 'Kameto' THEN calculate_rank_value(s.tier, s.rank, s.league_points) + 400
               WHEN p.alias = 'Nisqy' THEN calculate_rank_value(s.tier, s.rank, s.league_points) - 1300
               ELSE calculate_rank_value(s.tier, s.rank, s.league_points)
           END) as total_rank_value
    FROM players p
    JOIN soloqchallenge s ON p.alias = s.player
    WHERE s.time = ?
    GROUP BY p.team
    ORDER BY total_rank_value DESC
    """, (latest_time,))
    team_rankings = cursor.fetchall()

    for i, (team, wins, losses, rank_value) in enumerate(team_rankings):
        y = position[1] + 50 + i * 40
        draw_text(draw, f"{i+1} Team {team}: {wins}W / {losses}L ({(wins/(wins+losses))*100:.0f}%) {rank_value} LP", (position[0], y), text_font, colors['gold_light'])

def draw_team_rank_chart(background, cursor, position, colors, latest_time):
    cursor.execute("""
    WITH daily_ranks AS (
        SELECT 
            datetime(s.time, '+1 hour') as date, 
            p.team, 
            SUM(CASE 
                WHEN p.alias = 'Kameto' THEN calculate_rank_value(s.tier, s.rank, s.league_points) + 400
                WHEN p.alias = 'Nisqy' THEN calculate_rank_value(s.tier, s.rank, s.league_points) - 1300
                ELSE calculate_rank_value(s.tier, s.rank, s.league_points)
            END) as total_rank_value,
            ROW_NUMBER() OVER (PARTITION BY DATE(s.time, '+1 hour'), p.team ORDER BY s.time DESC) as rn
        FROM soloqchallenge s
        JOIN players p ON s.player = p.alias
        GROUP BY DATE(s.time, '+1 hour'), p.team, s.time
    )
    SELECT date, team, total_rank_value
    FROM daily_ranks
    WHERE rn = 1
    ORDER BY date 
    """)
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=['date', 'team', 'total_rank_value'])
    df['date'] = pd.to_datetime(df['date'])

    plt.figure(figsize=(12, 4))
    plt.style.use('dark_background')

    for team in df['team'].unique():
        team_data = df[df['team'] == team]
        plt.plot(team_data['date'], team_data['total_rank_value'], label=f'Team {team}', color=team_colors[team])

    plt.title("Team LP Over Time", fontsize=16, fontweight='bold', color=colors['gold_light'])
    plt.xlabel('Date', fontsize=12, color=colors['gold_light'])
    plt.ylabel('Total LP', fontsize=12, color=colors['gold_light'])

    ax = plt.gca()
    ax.set_facecolor('none')
    ax.grid(True, linestyle='--', alpha=0.3, color=colors['gold_muted'])

    plt.legend(loc='best')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    plt.gcf().autofmt_xdate()
    five_days_ago = pd.Timestamp.now() - pd.Timedelta(days=5)
    plt.xlim(left=five_days_ago)
    plt.ylim(bottom = 2000)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        plt.savefig(temp_file.name, format='png', dpi=100, bbox_inches='tight', transparent=True)
        plt.close()
        temp_file.seek(0)

    chart_image = Image.open(temp_file.name)
    background.paste(chart_image, position, chart_image.convert('RGBA'))

    

def draw_top_5_stats(draw, background, cursor, title_font, text_font, position, colors, latest_time):
    stats = [
        ("KDA", "CAST(ROUND((st.kills + st.assists) * 100.0 / CASE WHEN st.deaths = 0 THEN 1 ELSE st.deaths END, 0) AS FLOAT) / 100.0"),
        ("Kills", "st.kills"),
        ("Deaths", "st.deaths"),
        ("Assists", "st.assists"),
        ("LP", "league_points"),
        ("Win%", "ROUND(CAST(s.wins AS FLOAT) / (s.wins + s.losses) * 100, 0)"),
        ("CS/min", "ROUND(CAST(st.totalMinionsKilled AS FLOAT) / ((st.totalTimeSpentAlive + st.totalTimeSpentDead) / 60), 2)"),
        ("Damage/min", "ROUND(CAST(st.totalDamageDealtToChampions AS FLOAT) / ((st.totalTimeSpentAlive + st.totalTimeSpentDead) / 60), 0)")
    ]
    x,y = position
    titleText = "Top 5"
    name_bbox = title_font.getbbox(titleText)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width) // 2
    draw_text(draw, titleText, (name_x, y + 25), title_font, colors['gold'])
        
    # Draw gold lines
    line_height = 2 
    draw.line([(20, y + 60), (name_x - 20, y + 60)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, y + 60), (background.width - 20, y + 60)], fill=colors['gold'], width=line_height)

    # Adjust layout
    stats_per_column = 4
    column_width = 500  
    row_height = 220    
    player_height = 35  

    for i, (stat_name, stat_query) in enumerate(stats):
        cursor.execute(f"""
        SELECT p.alias, {stat_query} as stat_value, st.mostPlayedPosition
        FROM players p
        JOIN soloqchallenge s ON p.alias = s.player
        JOIN (
            SELECT player,
                   SUM(kills) as kills,
                   SUM(deaths) as deaths,
                   SUM(assists) as assists,
                   SUM(totalMinionsKilled) as totalMinionsKilled,
                   SUM(totalTimeSpentAlive) as totalTimeSpentAlive,
                   SUM(totalTimeSpentDead) as totalTimeSpentDead,
                   SUM(totalDamageDealtToChampions) as totalDamageDealtToChampions,
                   (SELECT individualPosition 
                    FROM stats st2 
                    WHERE st2.player = st1.player 
                    GROUP BY individualPosition 
                    ORDER BY COUNT(individualPosition) DESC 
                    LIMIT 1) as mostPlayedPosition
            FROM stats st1
            GROUP BY player
        ) st ON p.alias = st.player
        WHERE s.time = ?
        ORDER BY stat_value DESC
        LIMIT 5
        """, (latest_time,))
        top_5 = cursor.fetchall()

        column = i % stats_per_column
        row = i // stats_per_column
        x = position[0] + column * column_width
        y = position[1] + 70 + row * row_height

        draw_text(draw, stat_name, (x, y), text_font, colors['gold'])
        for j, (player, value, mostPlayedPosition) in enumerate(top_5):
            player_icon = Image.open(f"static/assets/{player}.png").resize((30, 30))  
            role_icon = Image.open(f"static/assets/role/{position_mapping.get(mostPlayedPosition, mostPlayedPosition)}.png").resize((30, 30)) 
            icon_y = y + 40 + j * player_height 
            background.paste(player_icon, (x, icon_y), player_icon.convert('RGBA'))
            background.paste(role_icon, (x + 35, icon_y), role_icon.convert('RGBA'))
            text_y = icon_y - 5
            
            # Format the value based on the stat name
            if stat_name == "KDA":
                formatted_value = f"{value:.2f}"
            elif stat_name == "Win%":
                formatted_value = f"{value:.0f}%"
            elif stat_name == "Damage/min":
                formatted_value = f"{value:.0f}"
            else:
                formatted_value = str(value)
            
            draw_text(draw, f"{j+1}  {player}: {formatted_value}", (x + 80, text_y), text_font, colors['gold_light'])
    
    

def main():
    generate_stats_image()
    print("Stats image generated as snapshot.png")

if __name__ == "__main__":
    main()
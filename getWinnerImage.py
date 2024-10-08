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

twitterHandles = {'Isma': '@ismaa_lol', 'Joinze': '@Joinzelol', 'Trayton': '@TraYt0N', '4zr': '@oh4zr', 'Gaëthan': '@Gaethaaan', 'Vetheo': '@Vetheo_lol', 'Skewmond': '@SkewMond_09', 'Exakick': '@Exakicklol', 'Nisqy': '@Nisqy', 'Matias': '@matiaslaclasse1', 'Potent': '@Potent213', 'Badlulu': '@badlullu', 'Eika': '@Eikalol', 'Zicssi': '@zicssiflay', 'Saken': '@Saken_lol', 'Nuc': '@Nuclear_int', 'Caliste': '@CalisteLoL', 'Strey': '@Streyito', 'Sayn': '@lol_saynnn', 'Blue': '@BlueEG7', 'Stormax': '@Stormax28', 'Hiro': '@Hiro_LoL9', 'Adam': '@Ricadam_lol', 'Splinter': '@MrSplinterlol', 'Vespa': '@Vespa_LOL', 'Myrtus': '@Myrtus_Lol', 'Zongo': '@Zongolol', 'Manaty': '@Manaty_LoL', 'Tiky': '@tikylol', 'Chreak': '@Chreak_Lol', 'Chap': '@Chap_GG', 'Slipix': '@slipixlol', 'Rin': '@adcRin', 'GoB GG': '@GoB_GG', 'Stend': '@Stend_lol', 'Wao': '@Waolol', 'Walou': '@GarouWalou', 'Boukada': '@Boukadaaa', 'Narkuss': '@NarkussLol', 'Kamiloo': '@Kamiloo_LoL', 'Kitano': '@Kitano_LoL', 'Sixen': '@SixenTv', 'Wakz': '@Wakzlol', 'Rhobalas': '@Rhobalasv2', 'Cosmïc': '@cosmiic_lol', 'Evalunna': '@EvalunnaTV', 'Aos Si': '@Aos_Sith', 'Veignorem': '@Veignorem_lol', 'Kameto': '@Kammeto'} 

# Load Riot Games' theme fonts
title_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 48)
header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 36)
text_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 28)
subtext_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 22)
footer_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 16)

    # Define Riot Games' gold color palette
colors = {
        'gold': '#C8AA6E',
        'gold_light': '#F0E6D2',
        'gold_dark': '#785A28',
        'gold_muted': '#C8AA6E80',
        'white': '#FFFFFF',
        'black': '#010A13',
        'blue': '#0AC8B9'
    }

def calculate_rank_value(tier, rank, league_points):
    return tierRankValues[tier][rank] + league_points


def generate_stats_image(playerName):
    background = Image.open("static/assets/finalBackground.png").resize((1920, 1080))
    draw = ImageDraw.Draw(background)
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    conn.create_function("calculate_rank_value", 3, calculate_rank_value)
    draw_top_row(draw, background, cursor, playerName, (0,0), colors)
    draw_role_winrates(draw, background, cursor, playerName, (20, 70), colors)
    generate_faced_report(draw, background, cursor, playerName, (1300, 70), colors)
    draw_general_stats(draw, background, cursor, playerName, (1300, 380), colors)
    draw_LP_chart(draw, background, cursor, playerName, (0, 700), colors)
    draw_last_20_games(draw, background, cursor, playerName, (0, 550), colors)
    draw_text(draw, "Made with love by KevcooT",(0, background.height-20), footer_font, colors['gold_light'])
    background.save(f"endResults/lastDay/winnerStats.png")

def draw_text(draw, text, position, font, text_color):
    draw.text(position, text, font=font, fill=text_color)

def draw_centered_title_with_lines(draw, background, text, y, colors, title_font, line_height=2):
    name_bbox = title_font.getbbox(text)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width) // 2
    draw_text(draw, text, (name_x, y), title_font, colors['gold'])
        
    # Draw gold lines
    line_y = y + 35  # Adjusted to align with the title
    draw.line([(20, line_y), (name_x - 20, line_y)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, line_y), (background.width - 20, line_y)], fill=colors['gold'], width=line_height)
        
    return line_y + 40  # Return the y-coordinate for content below the lines

def draw_top_row(draw, background, cursor, playerName, position, colors):
    x, y = position
    
    # Load and paste the soloqchallenge.png icon
    icon = Image.open("static/assets/soloqchallenge.png").resize((100, 100))  
    background.paste(icon, (x, y), icon.convert('RGBA'))
    
    name_bbox = title_font.getbbox(playerName)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width) // 2
    draw_text(draw, playerName, (name_x, y + 25), title_font, colors['gold'])
        
    # Draw gold lines
    line_height = 2  
    draw.line([(x + 120, y + 60), (name_x - 20, y + 60)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, y + 60), (background.width - 20, y + 60)], fill=colors['gold'], width=line_height)

    # Add player icon
    player_icon_size = 250  
    player_icon_path = f"static/assets/{playerName}.png"
    
    player_icon = Image.open(player_icon_path).resize((player_icon_size, player_icon_size))
        
    # Create a new image for the border
    bordered_player_icon = Image.new('RGBA', (player_icon_size + 8, player_icon_size + 8), (0, 0, 0, 0))
        
    # Draw the gold border
    border_draw = ImageDraw.Draw(bordered_player_icon)
    border_draw.rectangle([0, 0, player_icon_size + 7, player_icon_size + 7], outline=colors['gold'], width=4)
        
    # Paste the player icon onto the bordered image
    bordered_player_icon.paste(player_icon, (4, 4), player_icon.convert('RGBA'))
        
    # Calculate position to align with playerName title
    player_icon_x = (background.width - player_icon_size) // 2
    player_icon_y = y + 100
        
    # Paste the bordered player icon onto the background
    background.paste(bordered_player_icon, (player_icon_x, player_icon_y), bordered_player_icon)

    # Fetch player's rank, LP, wins, and losses
    cursor.execute("""
        SELECT tier, rank, league_points, wins, losses
        FROM soloqchallenge
        WHERE player = ?
        ORDER BY time DESC
        LIMIT 1
    """, (playerName,))
    player_data = cursor.fetchone()
    
    if player_data:
        tier, rank, league_points, wins, losses = player_data
        
        # Load and resize rank icon
        rank_icon_path = f"static/assets/{tier.lower()}.png"
        rank_icon_size = 100  # Adjust size as needed
        rank_icon = Image.open(rank_icon_path).resize((rank_icon_size, rank_icon_size))
        
        # Calculate position for rank icon (centered below player icon)
        rank_icon_x = player_icon_x + (player_icon_size - rank_icon_size) // 2
        rank_icon_y = player_icon_y + player_icon_size + 20  # 20 pixels below player icon
        
        # Paste rank icon
        background.paste(rank_icon, (rank_icon_x, rank_icon_y), rank_icon.convert('RGBA'))
        
        # Add LP text
        lp_text = f"{league_points} LP"
        lp_bbox = text_font.getbbox(lp_text)
        lp_width = lp_bbox[2] - lp_bbox[0]
        lp_x = rank_icon_x + (rank_icon_size - lp_width) // 2
        lp_y = rank_icon_y + rank_icon_size + 10  # 10 pixels below rank icon
        
        draw_text(draw, lp_text, (lp_x, lp_y), text_font, colors['gold_light'])
        
        # Add wins/losses and winrate
        total_games = wins + losses
        winrate = (wins / total_games) * 100 if total_games > 0 else 0
        
        # Calculate positions
        stats_y = lp_y + 30  # 30 pixels below LP text
        stats_x = rank_icon_x + (rank_icon_size // 2)  # Center of the rank icon
        
        # Calculate total width of all elements
        wins_text = f"{wins}W"
        losses_text = f"{losses}L"
        winrate_text = f"({winrate:.0f}%)"
        
        wins_bbox = text_font.getbbox(wins_text)
        losses_bbox = text_font.getbbox(losses_text)
        winrate_bbox = text_font.getbbox(winrate_text)
        
        wins_width = wins_bbox[2] - wins_bbox[0]
        losses_width = losses_bbox[2] - losses_bbox[0]
        winrate_width = winrate_bbox[2] - winrate_bbox[0]
        
        total_width = wins_width + losses_width + winrate_width + 20  # 20 for spacing
        
        # Calculate starting x position to center everything
        start_x = stats_x - (total_width // 2)
        
        # Draw wins in green
        wins_x = start_x
        draw_text(draw, wins_text, (wins_x, stats_y), text_font, (0, 255, 0))
        
        # Draw losses in red
        losses_x = wins_x + wins_width + 10  # 10 pixels right of wins
        draw_text(draw, losses_text, (losses_x, stats_y), text_font, (255, 0, 0))
        
        # Draw winrate
        winrate_x = losses_x + losses_width + 10  # 10 pixels right of losses
        draw_text(draw, winrate_text, (winrate_x, stats_y), text_font, colors['gold_light'])

def draw_LP_chart(draw, background, cursor, playerName, position, colors):
    x, y = position
    draw_centered_title_with_lines(draw, background, "LP over Time", y, colors, title_font)
    y += 70

    cursor.execute(
        """SELECT time,
            calculate_rank_value(tier, rank, league_points) as total_rank_value
        FROM soloqchallenge
        WHERE player = ?
        ORDER BY time ASC
    """, (playerName,))
    player_data = cursor.fetchall()

    df = pd.DataFrame(player_data, columns=['time', 'total_rank_value'])
    df['time'] = pd.to_datetime(df['time'])

    plt.figure(figsize=(background.width / 100, 3.25)) 
    plt.style.use('dark_background')
    plt.plot(df['time'], df['total_rank_value'], color=colors['gold'])
    plt.xlabel('Date', fontsize=8, color=colors['gold_light'])
    plt.ylabel('LP', fontsize=8, color=colors['gold_light'])

    ax = plt.gca()
    ax.set_facecolor('none')
    ax.grid(True, linestyle='--', alpha=0.3, color=colors['gold_muted'])

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    plt.gcf().autofmt_xdate(rotation=45, ha='right')  # Rotate date labels
    plt.xlim(left=pd.to_datetime('2024-09-07'), right=df['time'].max())
    plt.ylim(bottom=0)
    
    plt.tight_layout()  # Adjust layout to fit everything
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        plt.savefig(temp_file.name, format='png', dpi=100, bbox_inches='tight', transparent=True)
        plt.close()
        temp_file.seek(0)

    chart_image = Image.open(temp_file.name)
    chart_image = chart_image.resize((background.width - 40, int(chart_image.height * (background.width - 40) / chart_image.width)), Image.LANCZOS)
    background.paste(chart_image, (x + 20, y), chart_image.convert('RGBA'))


def generate_faced_report(draw, background, cursor, playerName, position, colors):
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
    """, (playerName,))
    
    data = cursor.fetchall()
    if not data:
        return

    df = pd.DataFrame(data, columns=['other_player', 'player_win', 'other_win'])
    df['relationship'] = df.apply(lambda row: 'Ally' if row['player_win'] == row['other_win'] else 'Opponent', axis=1)

    x, y = position

    # Draw the title
    headToHeadText = "Head to Head"
    name_bbox = title_font.getbbox(headToHeadText)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width - 250)
    draw_text(draw, headToHeadText, (name_x, y), title_font, colors['gold'])
        
    # Draw gold lines
    line_height = 2  # Adjust as needed
    draw.line([(x - 175, y + 30), (name_x - 20, y + 30)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, y + 30), (background.width - 20, y + 30)], fill=colors['gold'], width=line_height)

    # Draw opponents table
    draw_matchup_table(draw, background, df, (x-175, y+50), colors, "", is_opponent=True)

    # Draw allies table
    #draw_matchup_table(draw, background, df, (x-175, y + 280), colors, "Allies", is_opponent=False)


def draw_matchup_table(draw, background, df, position, colors, title, is_opponent):
    start_x, start_y = position

    # Draw the subtitle
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 28)
    draw_text(draw, title, (start_x, start_y), header_font, colors['gold'])

    # Filter data
    relationship = 'Opponent' if is_opponent else 'Ally'
    data_to_draw = df[df['relationship'] == relationship]

    # Draw the player icons
    icon_size = (60, 60)  
    icons_per_row = 10
    row_height = 80  
    frame_thickness = 3  
    for i, row in enumerate(data_to_draw.itertuples()):
        x = start_x + (i % icons_per_row) * (icon_size[0] + 15) 
        y = start_y + 40 + (i // icons_per_row) * row_height

        player_image = Image.open(f"static/assets/{row.other_player}.png")
        player_image = player_image.resize(icon_size)

        # Create a new image with a colored frame
        framed_image = Image.new('RGBA', (icon_size[0] + 2*frame_thickness, icon_size[1] + 2*frame_thickness))
        frame_color = (0, 255, 0, 255) if row.player_win else (255, 0, 0, 255)  # Green if won, red if lost
        framed_image.paste(frame_color, [0, 0, framed_image.size[0], framed_image.size[1]])
        framed_image.paste(player_image, (frame_thickness, frame_thickness), player_image.convert('RGBA'))

        background.paste(framed_image, (x - frame_thickness, y - frame_thickness), framed_image.convert('RGBA'))


def draw_general_stats(draw, background, cursor, playerName, position, colors):
    # Draw the title
    x,y = position
    statsText = "Stats"
    name_bbox = title_font.getbbox(statsText)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width - 335)
    draw_text(draw, statsText, (name_x, y), title_font, colors['gold'])
        
    # Draw gold lines
    line_height = 2  
    draw.line([(x - 175, y + 30), (name_x - 20, y + 30)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, y + 30), (background.width - 20, y + 30)], fill=colors['gold'], width=line_height)

    cursor.execute("""
    SELECT
        SUM(kills) AS total_kills,
        SUM(deaths) AS total_deaths,
        SUM(assists) AS total_assists,
        SUM(pentaKills) AS total_penta_kills,
        AVG(csPerMinute) AS avg_cs_per_min,
        AVG(goldEarned / ((totalTimeSpentAlive+totalTimeSpentDead) / 60)) AS avg_golds_per_min,
        AVG(totalDamageDealtToChampions / ((totalTimeSpentAlive+totalTimeSpentDead) / 60)) AS avg_damage_per_min,
        SUM(pushPings) AS total_push_pings
    FROM stats
    WHERE player = ?
    """, (playerName,))
    stats = cursor.fetchone()
    
    sword_icon = Image.open("static/assets/sword.png").resize((40, 40))
    skull_icon = Image.open("static/assets/skull.png").resize((40, 40))
    heart_icon = Image.open("static/assets/heart.png").resize((40, 40))
    penta_icon = Image.open("static/assets/penta.png").resize((40, 40))
    minion_icon = Image.open("static/assets/minion.png").resize((40, 40))
    goldcoins_icon = Image.open("static/assets/goldcoins.png").resize((40, 40))
    push_ping_icon = Image.open("static/assets/push_ping.png").resize((40, 40))
    
    icon_stats = [
        [(sword_icon, stats[0]), (skull_icon, stats[1]), (heart_icon, stats[2]), (penta_icon, stats[3])],
        [(sword_icon, f"{stats[6]:.0f}/min"), (minion_icon, f"{stats[4]:.2f}/min"), (goldcoins_icon, f"{stats[5]:.0f}/min"), (push_ping_icon, stats[7])]
    ]
    
    for i, row in enumerate(icon_stats):
        y_position = position[1] + 75 + i * 70  
        x_offset = - 175
        for icon, stat in row:
            background.paste(icon, (position[0] + x_offset, y_position), icon.convert('RGBA'))
            draw_text(draw, str(stat), (position[0] + x_offset + 45, y_position-4), text_font, colors['gold_light'])
            x_offset += 200 



def draw_role_winrates(draw, background, cursor, player_alias, canvas_position, colors):
    cursor.execute("""
    SELECT 
        individualPosition,
        SUM(win) * 100.0 / COUNT(*) AS win_rate,
        SUM(win) as wins,
        SUM(loss) as losses,
        COUNT(*) as games_played,
        championName,
        AVG(kills) as avg_kills,
        AVG(deaths) as avg_deaths,
        AVG(assists) as avg_assists
    FROM stats
    WHERE player = ?
    GROUP BY individualPosition, championName
    ORDER BY individualPosition, games_played DESC
    """, (player_alias,))
    position_stats = cursor.fetchall()
    
    mapped_results = {}
    for position, win_rate, wins, losses, games_played, championName, avg_kills, avg_deaths, avg_assists in position_stats:
        mapped_position = position_mapping.get(position, position)
        if mapped_position not in mapped_results:
            mapped_results[mapped_position] = {
                'wins': wins,
                'losses': losses,
                'games_played': games_played,
                'champions': []
            }
        else:
            mapped_results[mapped_position]['wins'] += wins
            mapped_results[mapped_position]['losses'] += losses
            mapped_results[mapped_position]['games_played'] += games_played
        
        kda = "Perfect" if avg_deaths == 0 else f"{avg_kills:.1f} / {avg_deaths:.1f} / {avg_assists:.1f}"
        mapped_results[mapped_position]['champions'].append({
            'name': championName,
            'wins': wins,
            'losses': losses,
            'games_played': games_played,
            'kda': kda
        })
    
    x, y = int(canvas_position[0]), int(canvas_position[1])

    roleWinrateText = "Role Winrate"
    name_bbox = title_font.getbbox(roleWinrateText)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width - 550) // 4
    draw_text(draw, roleWinrateText, (name_x, y), title_font, colors['gold'])
        
    # Draw gold lines
    line_height = 2  
    draw.line([(x + 20, y + 30), (name_x - 20, y + 30)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, y + 30), (name_x + name_width + 250, y + 30)], fill=colors['gold'], width=line_height)

    y_offset = 70
    role_icon_size = 50  
    champ_icon_size = 35  
    spacing = 5  
    column_width = 160  
    role_spacing = 15  

    # Define the order of roles
    role_order = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']

    # Draw all roles as separate columns
    for index, position_name in enumerate(role_order):
        role_x = x + 50 + column_width * index
        role_y = y + y_offset
        
        role_image = Image.open(f"static/assets/role/{position_name}.png").resize((role_icon_size, role_icon_size))
        background.paste(role_image, (role_x, role_y), role_image.convert('RGBA'))
        
        text_y = role_y + role_icon_size + spacing
        
        if position_name in mapped_results:
            data = mapped_results[position_name]
            games_played = data['games_played']
            wins = data['wins']
            losses = data['losses']
            
            # Draw wins and losses
            wins_text = f"{wins}W"
            losses_text = f"{losses}L"
            wins_bbox = subtext_font.getbbox(wins_text)
            losses_bbox = subtext_font.getbbox(losses_text)
            total_width = wins_bbox[2] + losses_bbox[2] + spacing
            wins_x = role_x + (role_icon_size - total_width) // 2
            losses_x = wins_x + wins_bbox[2] + spacing
            draw_text(draw, wins_text, (wins_x, text_y), subtext_font, (0, 255, 0))  # Green for wins
            draw_text(draw, losses_text, (losses_x, text_y), subtext_font, (255, 0, 0))  # Red for losses
            
            # Calculate and draw win rate
            win_rate = (wins / games_played) * 100 if games_played > 0 else 0
            winrate_text = f"({win_rate:.0f}%)"
            winrate_bbox = subtext_font.getbbox(winrate_text)
            winrate_x = role_x + (role_icon_size - winrate_bbox[2]) // 2
            draw_text(draw, winrate_text, (winrate_x, text_y + 25), subtext_font, colors['gold'])

            champ_y_offset = text_y + 80 + role_spacing
        
            # Draw champion stats for each role
            for champ_index, champ in enumerate(sorted(data['champions'], key=lambda x: x['games_played'], reverse=True)[:5]):  # Display top 5 champions per role
                champ_image = Image.open(f"static/assets/champion/{champ['name']}.png").resize((champ_icon_size, champ_icon_size))
                
                # Calculate the width of the champion stats text
                champ_win_rate = (champ['wins'] / champ['games_played']) * 100
                stats_text = f"{champ['wins']}W/{champ['losses']}L ({champ_win_rate:.0f}%)"
                kda_text = f"{champ['kda']}"
                stats_bbox = footer_font.getbbox(stats_text)
                kda_bbox = footer_font.getbbox(kda_text)
                stats_width = max(stats_bbox[2], kda_bbox[2])
                
                # Calculate the total width of the champion block (icon + stats)
                total_block_width = champ_icon_size + spacing + stats_width
                
                # Calculate the x position to center the block with the role icon
                if champ_index == 0:
                    champ_block_x = role_x + (role_icon_size - total_block_width) // 2
                
                # Draw champion icon
                champ_x = champ_block_x
                champ_y = champ_y_offset
                background.paste(champ_image, (champ_x, champ_y), champ_image.convert('RGBA'))
                
                # Draw champion stats
                text_x = champ_x + champ_icon_size + spacing
                wins_text = f"{champ['wins']}W"
                losses_text = f"{champ['losses']}L"
                winrate_text = f"({champ_win_rate:.0f}%)"
                draw_text(draw, wins_text, (text_x, champ_y), footer_font, (0, 255, 0))  # Green for wins
                draw_text(draw, losses_text, (text_x + footer_font.getbbox(wins_text)[2] + spacing, champ_y), footer_font, (255, 0, 0))  # Red for losses
                draw_text(draw, winrate_text, (text_x + footer_font.getbbox(wins_text + losses_text)[2] + spacing * 2, champ_y), footer_font, colors['white'])
                draw_text(draw, kda_text, (text_x, champ_y + 15), footer_font, colors['gold'])
                
                champ_y_offset += champ_icon_size + spacing * 3  
        else:
            draw_text(draw, "", (role_x, text_y), subtext_font, colors['white'])


def draw_last_20_games(draw, background, cursor, playerName, position, colors):
    x, y = position
    icon_size = 60  
    spacing = 15  # Spacing between icons
    total_width = 1920  # Using full width of the image

    # Fetch last 20 games
    cursor.execute("""
    SELECT championName, win
    FROM stats
    WHERE player = ?
    ORDER BY matchId DESC
    LIMIT 20
    """, (playerName,))
    
    games = cursor.fetchall()

    # Calculate the starting x position to center the icons
    total_icons_width = (icon_size + spacing) * len(games) - spacing
    start_x = x + (total_width - total_icons_width) // 2


    # Call the function
    icons_y = draw_centered_title_with_lines(draw, background, "Last 20 Games", y, colors, title_font)


    for i, (champion, win) in enumerate(games):
        icon_x = start_x + i * (icon_size + spacing)
        
        # Load and resize champion icon
        champ_icon = Image.open(f"static/assets/champion/{champion}.png").resize((icon_size, icon_size))
        
        # Create a new image for the border
        bordered_icon = Image.new('RGBA', (icon_size + 4, icon_size + 4), (0, 0, 0, 0))
        
        # Choose border color based on win/loss
        border_color = (0, 255, 0, 255) if win else (255, 0, 0, 255)
        
        # Draw the border
        border_draw = ImageDraw.Draw(bordered_icon)
        border_draw.rectangle([0, 0, icon_size + 3, icon_size + 3], outline=border_color, width=2)
        
        # Paste the champion icon onto the bordered image
        bordered_icon.paste(champ_icon, (2, 2), champ_icon.convert('RGBA'))
        
        # Paste the bordered icon onto the background
        background.paste(bordered_icon, (icon_x, icons_y), bordered_icon)



def get_winner(cursor):
    cursor.execute("""
    SELECT alias
    FROM players
    ORDER BY calculatedRankValue DESC
    LIMIT 1
    """)
    winner = cursor.fetchone()
    return winner[0] if winner else None

def count_games_on_september_24(cursor, playerName):
    cursor.execute("""
    SELECT COUNT(*)
    FROM stats 
    WHERE player = ? 
    AND time >= 1727128800000 
    """, (playerName,))
    count = cursor.fetchone()[0]
    return count

def get_24h_performance(cursor, playerName):

    cursor.execute("""SELECT DISTINCT time FROM soloqchallenge WHERE player = ? ORDER by time desc """, (playerName,))
    result = cursor.fetchall()
    previous_time = result[50][0]
    current_time = result[0][0]
    previous_values = {}
    current_values = {}
    delta_values = {}

    cursor.execute("""
        SELECT player, tier, rank, league_points, wins, losses
        FROM soloqchallenge
        WHERE time = ? AND player = ?
    """, (previous_time, playerName,))
    previous_data = cursor.fetchall()

    for player, tier, rank, lp, wins, losses in previous_data:
        rank_value = tierRankValues[tier][rank] + lp
        winrate = round(wins/(wins+losses)*100)
        previous_values[player] = rank_value, wins, losses, winrate

    cursor.execute("""
        SELECT player, tier, rank, league_points, wins, losses
        FROM soloqchallenge
        WHERE time = ? AND player = ?
    """, (current_time, playerName))
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
    lp_won = max(delta_values.items(), key=lambda x: x[1][0])
    if lp_won[1][0]>0:
        lp_won = f'+{lp_won[1][0]} LP 📈'
    else:
        lp_won = f'{lp_won[1][0]} LP 📉'

    # Player with highest winrate
    winrate = max(delta_values.items(), key=lambda x: x[1][3])

    text = f'{winrate[1][1]}W / {winrate[1][2]}L ({winrate[1][3]}%), {lp_won} '
    conn.close()
    return text


conn = sqlite3.connect('soloqchallenge.db')
cursor = conn.cursor()
playerName = get_winner(cursor)
generate_stats_image(playerName)
games_count = count_games_on_september_24(cursor, playerName)
summary=get_24h_performance(cursor, playerName)
print(f"Félicitations à {twitterHandles.get(playerName)} qui remporte le Soloq Challenge 🥳 \nIl a joué {games_count} games pendant le rush des dernières 24h \n{summary}")


#----------------------------------------------------------------------------------------------------------------------------------------------------

def generate_top_stats_image():
    background = Image.open("static/assets/finalBackground.png").resize((1920, 1080))
    draw = ImageDraw.Draw(background)
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()
    conn.create_function("calculate_rank_value", 3, calculate_rank_value)
    draw_top_all_roles(draw, background, cursor, playerName, (0,0), colors)

    draw_text(draw, "Made with love by KevcooT",(0, background.height-20), footer_font, colors['gold_light'])
    background.save(f"endResults/lastDay/topPlayersStats.png")

    
def get_winner_role(cursor, winner):
    cursor.execute("""
    SELECT individualPosition
    FROM stats
    WHERE player = ?
    GROUP BY individualPosition
    ORDER BY COUNT(*) DESC 
    LIMIT 1
    """, (winner,))
    winnerRole = cursor.fetchone()
    return winnerRole[0] if winnerRole else None

def get_top_players_by_role(cursor, winner):
    roles = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
    top_players = {}

    for role in roles:
        cursor.execute("""
        WITH player_roles AS (
            SELECT player, individualPosition, COUNT(*) as role_count,
                   ROW_NUMBER() OVER (PARTITION BY player ORDER BY COUNT(*) DESC) as rn
            FROM stats
            GROUP BY player, individualPosition
        ),
        ranked_players AS (
            SELECT p.alias, p.calculatedRankValue, pr.individualPosition
            FROM players p
            JOIN player_roles pr ON p.alias = pr.player
            WHERE pr.rn = 1
        )
        SELECT alias, calculatedRankValue, individualPosition
        FROM ranked_players
        WHERE individualPosition = ?
        ORDER BY calculatedRankValue DESC
        LIMIT 2
        """, (role,))
        
        results = cursor.fetchall()
        
        if results:
            if results[0][0] == winner:
                top_players[role] = results[1] if len(results) > 1 else None
            else:
                top_players[role] = results[0]
        else:
            top_players[role] = None

    return top_players

def get_top_players_stats(cursor, top_players):
    top_players_stats = {}

    for role, player in top_players.items():
        if player:
            cursor.execute("""
            SELECT 
                player,
                SUM(kills) as total_kills,
                SUM(deaths) as total_deaths,
                SUM(assists) as total_assists,
                SUM(win) as total_wins,
                SUM(loss) as total_losses,
                AVG(csPerMinute) as avg_cs_per_minute,
                AVG(totalDamageDealtToChampions) as avg_damage_dealt,
                COUNT(*) as games_played
            FROM stats
            WHERE player = ? AND individualPosition = ?
            GROUP BY player
            """, (player[0], role))
            
            stats = cursor.fetchone()
            if stats:
                top_players_stats[role] = {
                    'player': stats[0],
                    'total_kills': stats[1],
                    'total_deaths': stats[2],
                    'total_assists': stats[3],
                    'total_wins': stats[4],
                    'total_losses': stats[5],
                    'avg_cs_per_minute': stats[6],
                    'avg_damage_dealt': stats[7],
                    'games_played': stats[8]
                }
            else:
                top_players_stats[role] = None
        else:
            top_players_stats[role] = None

    return top_players_stats

def get_top_5_champions(cursor, player, role):
    cursor.execute("""
    SELECT championName, COUNT(*) as games_played
    FROM stats
    WHERE player = ? AND individualPosition = ?
    GROUP BY championName
    ORDER BY games_played DESC
    LIMIT 5
    """, (player, role))
    return cursor.fetchall()

def draw_top_all_roles(draw, background, cursor, playerName, position, colors):
    # Start from top of the image
    x, y = 0, 0

    # Draw title
    titlePageText = "Top par Role"
    name_bbox = title_font.getbbox(titlePageText)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (background.width - name_width) // 2
    draw_text(draw, titlePageText, (name_x, y + 25), title_font, colors['gold'])
        
    # Draw gold lines
    line_height = 2
    draw.line([(x + 120, y + 60), (name_x - 20, y + 60)], fill=colors['gold'], width=line_height)
    draw.line([(name_x + name_width + 20, y + 60), (background.width - 20, y + 60)], fill=colors['gold'], width=line_height)

    # Draw SoloQ Challenge icon
    icon = Image.open("static/assets/soloqchallenge.png").resize((100, 100))
    background.paste(icon, (0,0), icon.convert('RGBA'))

    # Get data
    winner = get_winner(cursor)
    top_players = get_top_players_by_role(cursor, winner)
    top_players_stats = get_top_players_stats(cursor, top_players)

    roles = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
    stats = ['KDA']

    # Calculate layout
    role_width = background.width // len(roles)
    role_y = y + 90
    stats_y_start = role_y + 80
    stats_height = 80  
    champion_y_start = stats_y_start + len(stats) * stats_height + 200  

    # Draw roles and player stats
    for i, role in enumerate(roles):
        role_x = i * role_width + (role_width // 2)

        # Draw role icon
        roleIcon = position_mapping.get(role, role)
        role_icon = Image.open(f"static/assets/role/{roleIcon.lower()}.png").resize((60, 60))
        icon_x = role_x - (role_icon.width // 2)
        background.paste(role_icon, (icon_x, role_y), role_icon.convert('RGBA'))

        if top_players_stats[role]:
            player = top_players_stats[role]['player']
            
            # Draw player icon with gold border
            player_icon = Image.open(f"static/assets/{player}.png").resize((120, 120))
            gold_border = Image.new('RGBA', (124, 124), colors['gold'])
            icon_x = role_x - (player_icon.width // 2)
            background.paste(gold_border, (icon_x - 2, stats_y_start - 2))
            background.paste(player_icon, (icon_x, stats_y_start), player_icon.convert('RGBA'))

            # Get player's rank data
            cursor.execute("""
            SELECT tier, rank, wins, losses, league_points
            FROM soloqchallenge
            WHERE player = ?
            ORDER BY time desc
            """, (player,))
            rank_data = cursor.fetchone()
            
            if rank_data:
                tier, rank, wins, losses, leaguePoints = rank_data
                
                # Draw rank icon
                rank_icon = Image.open(f"static/assets/{tier.lower()}.png").resize((30, 30))
                rank_icon_x = role_x - (rank_icon.width // 2)
                background.paste(rank_icon, (rank_icon_x, stats_y_start + 130), rank_icon.convert('RGBA'))
                
                # Draw LP
                lp_text = f"{leaguePoints} LP"
                draw_centered_text(draw, lp_text, (role_x, stats_y_start + 170), subtext_font, colors['white'])
                
                # Draw wins, losses, and winrate
                wins_text = f"{wins}W"
                losses_text = f"{losses}L"
                winrate = wins / (wins + losses) if (wins + losses) > 0 else 0
                winrate_text = f"({winrate:.0%})"
                wins_bbox = subtext_font.getbbox(wins_text)
                losses_bbox = subtext_font.getbbox(losses_text)
                winrate_bbox = subtext_font.getbbox(winrate_text)
                total_width = wins_bbox[2] + losses_bbox[2] + winrate_bbox[2] + 20  # 20 pixels spacing
                wins_x = role_x - (total_width // 2)
                losses_x = wins_x + wins_bbox[2] + 10
                winrate_x = losses_x + losses_bbox[2] + 10
                draw_text(draw, wins_text, (wins_x, stats_y_start + 200), subtext_font, (0, 255, 0))  # Green color
                draw_text(draw, losses_text, (losses_x, stats_y_start + 200), subtext_font, (255, 0, 0))  # Red color
                draw_text(draw, winrate_text, (winrate_x, stats_y_start + 200), subtext_font, colors['white'])  # White color

            # Draw KDA
            kda_y = stats_y_start + 240
            draw_centered_text(draw, "KDA", (role_x, kda_y), text_font, colors['gold'])  # KDA headline in gold
            
            kills = top_players_stats[role]['total_kills']
            deaths = top_players_stats[role]['total_deaths']
            assists = top_players_stats[role]['total_assists']
            kda_value = f"{kills}/{deaths}/{assists}"
            draw_centered_text(draw, kda_value, (role_x, kda_y + 35), subtext_font, colors['white'])

            # Draw "Champion Stats" title
            champ_stats_title_y = kda_y + 70
            draw_centered_text(draw, "Champion Stats", (role_x, champ_stats_title_y), text_font, colors['gold'])

            # Draw top 5 champions
            top_champions = get_top_5_champions(cursor, player, role)
            for k, (champ, games) in enumerate(top_champions):
                champ_icon = Image.open(f"static/assets/champion/{champ}.png").resize((40, 40))
                champ_x = role_x - (champ_icon.width // 2)  # Center the champion icon
                champ_y = champ_stats_title_y + 40 + k * 100  # Vertical spacing
                background.paste(champ_icon, (champ_x, champ_y), champ_icon.convert('RGBA'))
                
                # Calculate champion-specific stats
                cursor.execute("""
                SELECT SUM(win) as wins, SUM(loss) as losses, AVG(kills) as avg_kills, AVG(deaths) as avg_deaths, AVG(assists) as avg_assists
                FROM stats
                WHERE player = ? AND individualPosition = ? AND championName = ?
                """, (player, role, champ))
                champ_stats = cursor.fetchone()
                if champ_stats:
                    champ_wins, champ_losses, champ_avg_kills, champ_avg_deaths, champ_avg_assists = champ_stats
                    champ_winrate = champ_wins / (champ_wins + champ_losses) if (champ_wins + champ_losses) > 0 else 0
                    
                    # Draw wins/losses and winrate
                    wins_text = f"{champ_wins}W"
                    losses_text = f"{champ_losses}L"
                    winrate_text = f"({champ_winrate:.0%})"
                    wins_bbox = subtext_font.getbbox(wins_text)
                    losses_bbox = subtext_font.getbbox(losses_text)
                    winrate_bbox = subtext_font.getbbox(winrate_text)
                    total_width = wins_bbox[2] + losses_bbox[2] + winrate_bbox[2] + 20  # 20 pixels spacing
                    wins_x = role_x - (total_width // 2)
                    losses_x = wins_x + wins_bbox[2] + 10
                    winrate_x = losses_x + losses_bbox[2] + 10
                    draw_text(draw, wins_text, (wins_x, champ_y + 45), subtext_font, (0, 255, 0))  # Green color
                    draw_text(draw, losses_text, (losses_x, champ_y + 45), subtext_font, (255, 0, 0))  # Red color
                    draw_text(draw, winrate_text, (winrate_x, champ_y + 45), subtext_font, colors['white'])  # White color
                    
                    kda_text = f"{champ_avg_kills:.1f}/{champ_avg_deaths:.1f}/{champ_avg_assists:.1f}"
                   
                    # Align texts vertically
                    draw_centered_text(draw, kda_text, (role_x, champ_y + 75), subtext_font, colors['gold'])


        else:
            draw_centered_text(draw, "No data", (role_x, stats_y_start + stats_height), text_font, colors['white'])

        # Draw vertical gold line to separate roles (except for the last role)
        if i < len(roles) - 1:
            line_x = (i + 1) * role_width
            draw.line([(line_x, role_y), (line_x, background.height - 20)], fill=colors['gold'], width=2)

def draw_centered_text(draw, text, position, font, color):
    x, y = position
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text((x - text_width // 2, y - text_height // 2), text, font=font, fill=color, align='center')










generate_top_stats_image()
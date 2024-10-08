from datetime import datetime, timezone, timedelta
import sqlite3

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

import pandas as pd
from matplotlib import dates as mdates


position_mapping = {
    'TOP': 'Top',
    'JUNGLE': 'Jungle',
    'MIDDLE': 'Mid',
    'BOTTOM': 'Bot',
    'UTILITY': 'Support'
}

def generate_stats_image():
    background = Image.open("static/assets/bgtest.png")
    draw = ImageDraw.Draw(background)
    
    # Load Riot Games' theme fonts
    title_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 100)
    header_font = ImageFont.truetype("fonts/BeaufortForLOL-Bold.ttf", 48)
    text_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 36)
    
    # Define Riot Games' gold color palette
    colors = {
        'gold': '#C8AA6E',
        'gold_light': '#F0E6D2',
        'gold_dark': '#785A28',
        'gold_muted': '#C8AA6E80',  # 50% opacity
        'green': '#1E8449',
        'red': '#C0392B'
    }
  
    conn = sqlite3.connect('soloqchallenge.db')
    cursor = conn.cursor()

    # Get top 10 players based on calculatedRankValue
    cursor.execute("""
        SELECT alias, team, calculatedRankValue
        FROM players
        ORDER BY calculatedRankValue DESC
        LIMIT 10
    """)
    current_top_players = cursor.fetchall()

    # Get player rankings from 1 hour ago
    cursor.execute("SELECT DISTINCT time FROM soloqchallenge ORDER by time desc")
    result = cursor.fetchall()
    previous_time = result[12][0]
    print(result[0][0])

    challenge_start_date = datetime(2023, 9, 3)  # September 3rd as day 1
    current_time = datetime.fromisoformat(result[0][0])
    current_time = current_time + timedelta(hours=2)
    day_number = -(365 - (current_time.date() - challenge_start_date.date()).days + 1)
    hour = current_time.hour
    formatted_time = f"Day {day_number}, {hour}:00"

    cursor.execute("""
        SELECT player, tier, rank, league_points
        FROM soloqchallenge
        WHERE time = ?
    """, (previous_time,))
    previous_data = cursor.fetchall()

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

    # Calculate rank value and create previous rankings
    previous_rankings = {}
    previous_lps = {}
    for player, tier, rank, lp in previous_data:
        rank_value = tierRankValues.get(tier, {}).get(rank, 0) + lp
        previous_rankings[player] = rank_value
        previous_lps[player] = lp
    # Sort players by rank value and assign ranks
    sorted_players = sorted(previous_rankings.items(), key=lambda x: x[1], reverse=True)
    previous_rankings = {player: rank for rank, (player, _) in enumerate(sorted_players, 1)}


    # Draw title
    title_text = f"TOP 10 - {formatted_time}"
    draw.text((background.width // 2, 50), title_text, font=title_font, fill=colors['gold'], anchor="mt")

    # Draw icon
    logo = Image.open("static/assets/soloqchallenge.png")
    logo = logo.resize((150, 150))
    background.paste(logo, (background.width-150,0), logo.convert('RGBA'))

    # Draw player stats
    y_offset = 200  
    for i, (player, team, rank_value) in enumerate(current_top_players, 1):
        # Get player stats
        cursor.execute("""
            SELECT championName, individualPosition, 
                    SUM(kills) as total_kills, 
                    SUM(assists) as total_assists, 
                    SUM(deaths) as total_deaths,
                    COUNT(*) as games_played,
                    SUM(win) as wins,
                    AVG(csPerMinute) as avg_cs_per_minute
            FROM stats
            WHERE player = ?
            ORDER BY games_played DESC
            LIMIT 1
        """, (player,))
        stats = cursor.fetchone()
        
        # Get current tier, rank and league points
        cursor.execute("""
            SELECT tier, rank, league_points
            FROM soloqchallenge
            WHERE player = ?
            ORDER BY time DESC
            LIMIT 1
        """, (player,))
        current_rank_data = cursor.fetchone()
        
        if stats and current_rank_data:
            champion, position, kills, assists, deaths, games_played, wins, avg_cs = stats
            current_tier, current_rank, current_lp = current_rank_data
            position = position_mapping.get(position, position)
            win_rate = (wins / games_played) * 100 if games_played > 0 else 0
            
            player_icon = Image.open(f"static/assets/{player}.png").resize((120, 120))
            
            # Create a gold frame
            frame_size = 5  
            framed_icon = Image.new('RGBA', (player_icon.width + 2*frame_size, player_icon.height + 2*frame_size), colors['gold']) 
            framed_icon.paste(player_icon, (frame_size, frame_size))
            
            # Paste the framed icon onto the background
            background.paste(framed_icon, (50 - frame_size, y_offset - frame_size))
            
            # Draw position icon
            position_icon = Image.open(f"static/assets/role/{position.lower()}.png").resize((60, 60))
            background.paste(position_icon, (180, y_offset), position_icon)
            
            # Draw team icon
            try:
                team_icon = Image.open(f"static/assets/{team}.png").convert("RGBA").resize((60, 60))
                background.paste(team_icon, (180, y_offset + 60), team_icon)
            except ValueError:
                # If there's an issue with transparency, paste without mask
                background.paste(team_icon, (180, y_offset + 100))
            
            # Draw rank comparison icon and text
            previous_rank = previous_rankings.get(player)
            previous_lp = previous_lps.get(player)
            lp_change = current_lp - previous_lp
            if previous_rank is None or previous_rank > 10:
                rank_change_icon = Image.open("static/assets/arrow_up.png").resize((30, 30))
                rank_change_text = " *"
                rank_change_color = colors['gold']
            else:
                rank_change = previous_rank - i
                if rank_change > 0:
                    rank_change_icon = Image.open("static/assets/arrow_up.png").resize((30, 30))
                    rank_change_text = f"+{rank_change}"
                    rank_change_color = colors['green']
                elif rank_change < 0:
                    rank_change_icon = Image.open("static/assets/arrow_down.png").resize((30, 30))
                    rank_change_text = f"{rank_change}"
                    rank_change_color = colors['red']
                else:
                    rank_change_icon = Image.open("static/assets/equal.png").resize((30, 30))
                    rank_change_text = ""
                    rank_change_color = colors['gold_light']
            if lp_change > 0:
                lp_change_text = f"+{lp_change}"
                lp_change_color = colors['green']
            elif lp_change < 0:
                lp_change_text = f"{lp_change}"
                lp_change_color = colors['red']
            else:
                lp_change_text = "="
                lp_change_color = colors['gold_light']
            # Calculate the vertical center of the player's name
            player_name_center = y_offset + 10
            
            # Align the middle of the rank change icon with the middle of the player's name
            rank_icon_y = player_name_center   # 15 is half the height of the rank change icon
            background.paste(rank_change_icon, (250, rank_icon_y + 40), rank_change_icon)
            draw.text((250, rank_icon_y), rank_change_text, font=text_font, fill=rank_change_color)
            
            # Draw player info
            player_text = f"{player}"
            draw.text((300, y_offset), player_text, font=header_font, fill=colors['gold'])
            
            # Add bone.png for Trayton and adjust x_offset for rank info
            x_offset = int(300 + draw.textlength(player_text, font=header_font) + 10)
            if player == "Trayton":
                bone_icon = Image.open("static/assets/bone.png").resize((30, 30))
                background.paste(bone_icon, (x_offset, y_offset+20), bone_icon)
                x_offset += 40  # Add width of bone icon plus a small gap
            
            player_wr = f" {current_tier} - {current_lp} LP "
            draw.text((x_offset, y_offset+12), player_wr, font=text_font, fill=colors['gold_light'])
            draw.text((int(x_offset + draw.textlength(player_wr, font=text_font)), y_offset+12), f"({lp_change_text})", font=text_font, fill=lp_change_color)
     
            # Draw current tier, rank and league points
            win_text = f"{wins}W"
            loss_text = f"{games_played - wins}L"
            win_rate_text = f"({round(win_rate)}%)"
            draw.text((300, y_offset + 60), win_text, font=text_font, fill=colors['green'])
            draw.text((300 + draw.textlength(win_text, font=text_font), y_offset + 60), " / ", font=text_font, fill=colors['gold_light'])
            draw.text((300 + draw.textlength(win_text + " / ", font=text_font), y_offset + 60), loss_text, font=text_font, fill=colors['red'])
            draw.text((300 + draw.textlength(win_text + " / " + loss_text, font=text_font), y_offset + 60), f" {win_rate_text}", font=text_font, fill=colors['gold_light'])
            
            # Draw KDA and other stats
            kda = (kills + assists) / deaths if deaths > 0 else kills + assists
            kda_text = f"KDA: {kills}/{deaths}/{assists} ({kda:.2f})"
            draw.text((300, y_offset + 100), kda_text, font=text_font, fill=colors['gold_light'])
            """
            stats_text = f"Win Rate: {win_rate:.1f}% | CS/min: {avg_cs:.1f}"
            draw.text((300, y_offset + 140), stats_text, font=text_font, fill=colors['gold_light'])
            """
            # Get and draw most played champions
            cursor.execute("""
                SELECT championName, COUNT(*) as games_played
                FROM stats
                WHERE player = ?
                GROUP BY championName
                ORDER BY games_played DESC
                LIMIT 5
            """, (player,))
            top_champions = cursor.fetchall()
            
            champ_x_offset = 850
            for champ, _ in top_champions:
                champ_icon = Image.open(f"static/assets/champion/{champ}.png").resize((60, 60))
                background.paste(champ_icon, (champ_x_offset, y_offset + 70))
                champ_x_offset += 80
            
            y_offset += 200  # Move to next line
            
            # Draw separation line
            draw.line((50, y_offset, background.width - 50, y_offset), fill=colors['gold'], width=2)
            
            y_offset += 40  # Add more space after the line
    # Draw footer
    footer_text = "Made with love by KevcooT"
    update_timer_text = "Updates every 6 hours"
    footer_font = ImageFont.truetype("fonts/BeaufortForLOL-Regular.ttf", 24)
    draw.text((background.width // 2, background.height - 200), update_timer_text, font=footer_font, fill=colors['gold_muted'], anchor="ms")
    draw.text((background.width // 2, background.height - 100), footer_text, font=footer_font, fill=colors['gold_muted'], anchor="ms")

    conn.close()
    # Save the image
    background.save("endResults/hourlyUpdate/soloq_challenge_leaderboard.png")


generate_stats_image()
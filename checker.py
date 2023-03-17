import requests
import json
import time
from datetime import datetime, time, timedelta
import time as tm
from discord_webhook import DiscordWebhook, DiscordEmbed

now = datetime.now()
current_time = now.strftime("%H:%M")

class FitnessPoint:
    def __init__(self):
        self.webhook_url = "INPUT_DISCORD_WEBHOOK_HERE"
        self.studio_number = "XBT$1"
    
    def run(self):
        while True:
            print('Status-Poll: Checking FitnessPoint Frequentation at ' + current_time +'...')
            self.check_frequentation()
            tm.sleep(1800)  # Sleep for one hour (3600 seconds)

    def check_frequentation(self):
        headers = {
            'authority': 'www.fitnesspoints.de',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'referer': 'https://www.fitnesspoints.de/fitnesspoint-regensburg',
            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        
        response = requests.get('https://www.fitnesspoints.de/api/checkinCount', headers=headers)
        studios = json.loads(response.text)

        frequentation = None
        for studio in studios:
            if studio["studioNumber"] == self.studio_number:
                frequentation = studio["frequentation"]
                break

        if frequentation is not None:
            frequentation_percentage = frequentation * 100
            
            if frequentation_percentage < 50:
                self.occupancy_status = "Frei :green_square:"
            elif frequentation_percentage < 80:
                self.occupancy_status = "Teilweise belegt :yellow_square:"
            else:
                self.occupancy_status = "Voll belegt :red_square:"
            
            print("Status-Poll: Aktuelle Auslastung von FitnessPoint: {:.1f}%".format(frequentation_percentage))
            self.send_webhook(frequentation_percentage)
            print('Status-Update: User got notified via Discord.')
        else:
            print("Status-Poll: Auslastung nicht verfügbar! - Retrying...")

    def send_webhook(self, frequentation_percentage):
        TITLE = 'FitnessPoint Regensburg'

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        opening_time = time(6, 0) if now.weekday() < 5 else time(8, 0)
        closing_time = time(0, 0) if now.weekday() < 5 else time(22, 0)
        status = ''
        
        if now.time() < opening_time:
            status = 'Geschlossen :no_entry:'
        elif now.time() > closing_time:
            status = 'Geschlossen :no_entry:'
        else:
            status = 'Geöffnet :white_check_mark: '
        embed = DiscordEmbed(title=TITLE, color='FF0000')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1073359084843192381/1086078049910538260/fitnesspoint.png')
        embed.set_footer(text="FitnessPoint GmbH", icon_url="https://cdn.discordapp.com/attachments/1073359084843192381/1086078049910538260/fitnesspoint.png")
        embed.set_timestamp()
        embed.add_embed_field(name='Auslastung', value="{:.1f}%".format(frequentation_percentage))
        embed.add_embed_field(name='Status', value=self.occupancy_status)
        embed.add_embed_field(name='Verfügbarkeit', value=status)
        embed.add_embed_field(name='Aktuelle Zeit', value=current_time)
        embed.add_embed_field(name='Öffnungzeiten',  value='Mo-Fr: 06:00 - 0:00 \nSa-So: 08:00 - 22:00')
 
        webhook = DiscordWebhook(url=self.webhook_url, rate_limit_retry=True)
        webhook.add_embed(embed)
        webhook.execute()

if __name__ == '__main__':
    fp = FitnessPoint()
    fp.run()

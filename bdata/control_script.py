import json
import time
import os
from threading import Thread
from datetime import datetime
from pushnotifier import PushNotifier as pn


def read_json_file():
    with open(os.path.abspath("bdata/data.json"),'r') as f:
        data = json.load(f)
    return data

with open(os.path.abspath("bdata/pc_name"),'r') as f:
    pc_name = f.read()

json_data = read_json_file()
bot_type = json_data['XXXINFO'][pc_name]['bot_type']
pdevices = json_data['pushnotifierinfo']['deviceid']
pn = pn.PushNotifier(json_data['pushnotifierinfo']['username'],json_data['pushnotifierinfo']['password'],json_data['pushnotifierinfo']['packagename'],json_data['pushnotifierinfo']['papikey'])

def main():
    while True:
        time.sleep(60)
        json_data = read_json_file()
        bot_type = json_data['XXXINFO'][pc_name]['bot_type']
        if not bot_type in ['type_christ','type_normal','type_switch']:
            break
        last_time = datetime.strptime(read_json_file()['time_check'], "%m/%d/%Y, %H:%M")
        time_diff = int((datetime.now()-last_time).seconds / 60)
        if time_diff > 60:
            pn.send_text('{} {}, {} dakikadır ses yok'.format(datetime.now().strftime('%H:%M'),json_data['XXXINFO'][pc_name]['username'],time_diff),
                silent=False, devices=[pdevices])
        time.sleep(1200)
        
if bot_type in ['type_christ','type_normal','type_switch']:
    x = Thread(target=main)
    x.start()
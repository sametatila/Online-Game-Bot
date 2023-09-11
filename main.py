import pyautogui as pau
import pydirectinput as pd
import time
import win32gui
import os
import sys
import psutil
from pushnotifier import PushNotifier as pn
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import *
from azcaptchaapi import AZCaptchaApi
from PIL import Image
from pytesseract import pytesseract
from datetime import datetime
import cv2
import numpy as np
import win32ui
from ctypes import windll
import json
import keyboard
import serial
import mouse
import threading
import socket
import struct
import win32api


def read_json_file():
    with open('./bdata/data.json','r') as f:
        data = json.load(f)
    return data

def write_json_file(data):
    with open('./bdata/data.json','w') as f:
        json.dump(data, f, indent=4)
    return data

def update_json(new_data):
    with open('./bdata/data.json','r') as f:
        data = json.load(f)
    data.update(new_data)
    with open('./bdata/data.json','w') as f:
        json.dump(data, f, indent=4)
    return data

def update_json_partial(new_data,*args):
    with open('./bdata/data.json','r') as f:
        data = json.load(f)
    if len(args) == 1:
        data[args[0]] = new_data
    elif len(args) == 2:
        data[args[0]][args[1]] = new_data
    elif len(args) == 3:
        data[args[0]][args[1]][args[2]] = new_data
    with open('./bdata/data.json','w') as f:
        json.dump(data, f, indent=4)
    return data

json_data = read_json_file()

with open('./bdata/pc_name','r') as f:
    pc_name = f.read()

try:
    pc_data = json_data['pc_variables'][pc_name]
except:
    pc_data = json_data['pc_variables']['monster_1']

com = pc_data['serial_port']

azapi = AZCaptchaApi('XXX')

gamefolder = 'XXX'
otcfolder = 'XXX'

items = ['clothes','other_clothes']
servers = ['XXX']
server_numbers = ['XXX']

pdevices = json_data['pushnotifierinfo']['deviceid']
pn = pn.PushNotifier(json_data['pushnotifierinfo']['username'],json_data['pushnotifierinfo']['password'],json_data['pushnotifierinfo']['packagename'],json_data['pushnotifierinfo']['papikey'])

clothes_inven = ['fc','fp','fcap','fglo','fsho']
clothes_armor = ['fcf','fpf','fcapf','fglof','fshof']
other_clothes_inven = ['mlu1','mlu2','mlu3','mlu4','mlu5']
other_clothes_armor = ['ml1','ml2','ml3','ml4','ml5']
clothes_merchant = ['fcm','fpm','fcapm','fglom','fshom']
item_dict = {'f':(clothes_inven,clothes_armor,clothes_merchant),'m':(other_clothes_inven,other_clothes_armor)}

w_size, h_size = pd.size()
if w_size == 1920:
    w_sizen, h_sizen = w_size-554, h_size-312
else:
    w_sizen, h_sizen = w_size, h_size

class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainUi, self).__init__()
        uic.loadUi('./bdata/XXX.ui', self)
        self.setWindowTitle("XXX")
        self.kullaniciadi.setText(json_data['XXXINFO'][pc_name]['username'])
        self.kullanicisifre.setText(json_data['XXXINFO'][pc_name]['password'])
        self.itemsec.addItems(items)
        self.itemsec.setCurrentText(json_data['XXXINFO'][pc_name]['item'])
        self.sunucusec.addItems(servers)
        self.sunucusec.setCurrentText(json_data['XXXINFO'][pc_name]['sunucu'])
        if self.sunucusec.currentText() == 'XXX':
            self.sunucunosec.clear()
            self.sunucunosec.addItems(server_numbers[:5])
            self.sunucunosec.addItems(server_numbers[12:])
        self.sunucunosec.setCurrentText(json_data['XXXINFO'][pc_name]['sunucuno'])
        self.sunucusec.currentTextChanged.connect(self.sunucusec_changed)
        self.fiyat.setText(json_data['XXXINFO'][pc_name]['fiyat'])
        if json_data['XXXINFO'][pc_name]['bot_type'] == 'type_normal':
            self.type_normal_r.setChecked(True)
        elif json_data['XXXINFO'][pc_name]['bot_type'] == 'type_christ':
            self.type_christ_r.setChecked(True)
        elif json_data['XXXINFO'][pc_name]['bot_type'] == 'type_switch':
            self.type_switch_r.setChecked(True)
        elif json_data['XXXINFO'][pc_name]['bot_type'] == 'type_merchant':
            self.type_merchant_r.setChecked(True)
        elif json_data['XXXINFO'][pc_name]['bot_type'] == 'type_login':
            self.type_login_r.setChecked(True)
        if json_data['XXXINFO'][pc_name]['vip_key'] == 'True':
            self.vip_key_c.setChecked(True)
        elif json_data['XXXINFO'][pc_name]['vip_key'] == 'False':
            self.vip_key_c.setChecked(False)
        self.kokaydet.clicked.connect(self.koinfokaydet)
        self.baslat.clicked.connect(self.threading_main_func)
        self.durdur.clicked.connect(self.thread_stop)
        self.inv_to_inn_btn.clicked.connect(self.invtoinn_thread)
        self.inn_to_inv_btn.clicked.connect(self.inntoinv_thread)
        self.vip_to_inv_btn.clicked.connect(self.viptoinv_thread)
        self.inv_to_vip_btn.clicked.connect(self.invtovip_thread)
        self.sendinput_start.clicked.connect(self.sendinput_thread)
        self.sendinput_stop.clicked.connect(self.sendinput_thread_stop)
        self.durdur.setEnabled(False)
        self.sendinput_stop.setEnabled(False)

        self.notuser.setText(json_data['pushnotifierinfo']['username'])
        self.notcass.setText(json_data['pushnotifierinfo']['password'])
        self.notcackage.setText(json_data['pushnotifierinfo']['packagename'])
        self.notapi.setText(json_data['pushnotifierinfo']['papikey'])
        self.notdevice.setText(json_data['pushnotifierinfo']['deviceid'])
        self.notuser.setEnabled(False)
        self.notcass.setEnabled(False)
        self.notcackage.setEnabled(False)
        self.notapi.setEnabled(False)
        self.notdevice.setEnabled(False)

        total_item_count = json_data['loop_info']['total_item_count']
        if type(total_item_count) == str:
            self.total_item_label.setText(str(total_item_count))
        else:
            self.total_item_label.setText('0')
        loop_count = json_data['loop_info']['loop_count']
        if type(loop_count) == str:
            self.loop_label.setText(str(loop_count))
        else:
            self.loop_label.setText('0')

        self.reset_button.clicked.connect(self.reset_count)
        self.show()
        
    def sunucusec_changed(self):
        if self.sunucusec.currentText() == 'Zero':
            self.sunucunosec.clear()
            self.sunucunosec.addItems(server_numbers[:5])

    def koinfokaydet(self):
        user_name = self.kullaniciadi.text()
        user_pass = self.kullanicisifre.text()
        item_kind = self.itemsec.currentText()
        server = self.sunucusec.currentText()
        server_number = self.sunucunosec.currentText()
        sell_price = self.fiyat.text()
        type_normal = self.type_normal_r.isChecked()
        type_christ = self.type_christ_r.isChecked()
        type_switch = self.type_switch_r.isChecked()
        type_merchant = self.type_merchant_r.isChecked()
        type_login = self.type_login_r.isChecked()
        vip_key = self.vip_key_c.isChecked()
        if type_normal:
            bot_type = 'type_normal'
        elif type_christ:
            bot_type = 'type_christ'
        elif type_switch:
            bot_type = 'type_switch'
        elif type_merchant:
            bot_type = 'type_merchant'
        elif type_login:
            bot_type = 'type_login'

        ko_user_info = {
            "username": str(user_name),
            "password": str(user_pass),
            "item": str(item_kind),
            "sunucu": str(server),
            "sunucuno": str(server_number),
            "fiyat": str(sell_price),
            "bot_type": str(bot_type),
            "vip_key": str(vip_key)
        }
        update_json_partial(ko_user_info,'XXXINFO',pc_name)
        kill_exe('XXX.exe')
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    def reset_count(self):
        loop_info = {
            "loop_info": {
                'loop_count': "0",
                'total_item_count': "0"
            },
            "no_scroll": "False"
        }
        update_json(loop_info)
        self.total_item_label.setText('0')
        self.loop_label.setText('0')

    def disable_durdur(self, val):
        if val:
            self.baslat.setEnabled(True)
            self.durdur.setEnabled(False)

    def threading_main_func(self):
        self.kullaniciadi.setEnabled(False)
        self.kullanicisifre.setEnabled(False)
        self.itemsec.setEnabled(False)
        self.sunucusec.setEnabled(False)
        self.sunucunosec.setEnabled(False)
        self.fiyat.setEnabled(False)
        try:
            update_json({"time_check": datetime.now().strftime("%m/%d/%Y, %H:%M")})
        except:
            pass
        kill_exe('XXX.exe')
        control_exe = os.path.abspath("bdata/XXX.exe")
        os.startfile(control_exe)
        if self.type_normal_r.isChecked() or self.type_christ_r.isChecked():
            self.control_thread()
        self.thread_1 = ThreadClass(parent=None,index=0)
        self.thread_1.user_name = self.kullaniciadi.text()
        self.thread_1.user_pass = self.kullanicisifre.text()
        if self.itemsec.currentText() == 'clothes':
            self.thread_1.item_lists = item_dict['f']
        elif self.itemsec.currentText() == 'other_clothes':
            self.thread_1.item_lists = item_dict['m']
        self.thread_1.server = str(self.sunucusec.currentText()).lower()
        for server_num in server_numbers:
            if self.sunucunosec.currentText() == server_num:
                server_num = server_num.replace(' ','_').lower()
                self.thread_1.server_number = server_num
        self.thread_1.total_item_count = self.total_item_label.text()
        self.thread_1.loop_count = self.loop_label.text()
        self.thread_1.price = self.fiyat.text()
        self.thread_1.type_normal = self.type_normal_r.isChecked()
        self.thread_1.type_christ = self.type_christ_r.isChecked()
        self.thread_1.type_switch = self.type_switch_r.isChecked()
        self.thread_1.type_merchant = self.type_merchant_r.isChecked()
        self.thread_1.type_login = self.type_login_r.isChecked()
        self.thread_1.vip_key = self.vip_key_c.isChecked()

        self.thread_1.start()
        self.thread_1.total_item_signal.connect(self.total_item_label.setText)
        self.thread_1.loop_count_signal.connect(self.loop_label.setText)
        self.thread_1.disable_durdur_signal.connect(self.disable_durdur)
        self.baslat.setEnabled(False)
        self.durdur.setEnabled(True)
        self.sendinput_start.setEnabled(False)
        self.sendinput_stop.setEnabled(False)
        
    def minute_control(self, val):
        if val:
            self.baslat.setEnabled(True)
            self.durdur.setEnabled(False)
            self.thread_1.stop()
            self.baslat.setEnabled(False)
            self.durdur.setEnabled(True)
            self.threading_main_func()

    def control_thread(self):
        if self.type_normal_r.isChecked() or self.type_christ_r.isChecked():
            self.thread_2 = ControlThreadClass(parent=None,index=0)
            self.thread_2.type_normal = self.type_normal_r.isChecked()
            self.thread_2.type_christ = self.type_christ_r.isChecked()
            self.thread_2.type_switch = self.type_switch_r.isChecked()
            self.thread_2.type_merchant = self.type_merchant_r.isChecked()
            self.thread_2.type_login = self.type_login_r.isChecked()
            self.thread_2.user_name = self.kullaniciadi.text()
            self.thread_2.start()
            self.thread_2.control_signal.connect(self.minute_control)

    def thread_stop(self):
        kill_exe('XXX.exe')
        self.kullaniciadi.setEnabled(True)
        self.kullanicisifre.setEnabled(True)
        self.itemsec.setEnabled(True)
        self.sunucusec.setEnabled(True)
        self.sunucunosec.setEnabled(True)
        self.fiyat.setEnabled(True)
        print('main bitti')
        self.baslat.setEnabled(True)
        self.durdur.setEnabled(False)
        self.sendinput_start.setEnabled(True)
        self.sendinput_stop.setEnabled(False)
        if self.type_normal_r.isChecked() or self.type_christ_r.isChecked():
            self.thread_2.stop()
        self.thread_1.stop()

    def inntoinv_thread(self):
        self.thread = InntoInvThreadClass(parent=None,index=0)
        if self.itemsec.currentText() == 'clothes':
            self.thread.item_lists = item_dict['f']
        elif self.itemsec.currentText() == 'other_clothes':
            self.thread.item_lists = item_dict['m']
        self.thread.start()

    def viptoinv_thread(self):
        self.thread = ViptoInvThreadClass(parent=None,index=0)
        if self.itemsec.currentText() == 'clothes':
            self.thread.item_lists = item_dict['f']
        elif self.itemsec.currentText() == 'other_clothes':
            self.thread.item_lists = item_dict['m']
        self.thread.start()

    def invtovip_thread(self):
        self.thread = InvtoVipThreadClass(parent=None,index=0)
        if self.itemsec.currentText() == 'clothes':
            self.thread.item_lists = item_dict['f']
        elif self.itemsec.currentText() == 'other_clothes':
            self.thread.item_lists = item_dict['m']
        self.thread.start()

    def invtoinn_thread(self):
        self.thread = InvtoInnThreadClass(parent=None,index=0)
        if self.itemsec.currentText() == 'clothes':
            self.thread.item_lists = item_dict['f']
        elif self.itemsec.currentText() == 'other_clothes':
            self.thread.item_lists = item_dict['m']
        self.thread.start()

    def sendinput_thread(self):
        self.thread_3 = SendInputThreadClass(parent=None,index=0)
        self.thread_3.info = False
        self.sendinput_start.setEnabled(False)
        self.sendinput_stop.setEnabled(True)
        self.thread_3.start()

    def sendinput_thread_stop(self):
        self.sendinput_start.setEnabled(True)
        self.sendinput_stop.setEnabled(False)
        pd.keyDown('ctrl')
        pd.keyUp('ctrl')
        time.sleep(0.5)
        self.thread_3.stop()
       
class ThreadClass(QtCore.QThread):
    total_item_signal = QtCore.pyqtSignal(str)
    loop_count_signal = QtCore.pyqtSignal(str)
    disable_durdur_signal = QtCore.pyqtSignal(bool)
    def __init__(self, parent: None,index=0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        
    def run(self):
        if self.type_merchant:
            try:
                time.sleep(5)
                merchant_check(self.item_lists, self.price, self.user_name,self.vip_key)
            except Exception as e:
                print(e)
                pass
        else:
            if self.total_item_count != 'item': 
                total_item_count = int(self.total_item_count)
            else:
                total_item_count = 0
            if self.loop_count != 'item': 
                loop_count = int(self.loop_count)
            else:
                loop_count = 0
            big_condition = True
            while big_condition:
                try:
                    condition = True
                    while condition:
                        try:
                            update_time()
                        except:
                            pass
                        if self.type_login:
                            kill_game()
                            condition = start_game()
                            condition = otc_running_check()
                            condition = check_and_click('xxx_pic',0.98,file_name_2='xxx_pic_2',s2=0.5)
                            key_press('+enter')
                            condition = login_screen(self.user_name,self.user_pass)
                            condition = otc_screen()
                            condition = check_and_click('startconfirm',0.9)
                            condition = select_server_screen(self.server,self.server_number)
                            condition = check_captcha()
                            condition = character_screen()
                            pn.send_text('{} {}, giriş yapıldı.'.format(datetime.now().strftime('%H:%M'),self.user_name),
                                    silent=False, devices=[pdevices])
                            big_condition = False
                            condition = False
                        else:
                            if self.type_switch == True and locate_png('menuler',0.7) != None:
                                time.sleep(2)
                                click(60,60,s1=1,s3=1)
                                upgrade_place_x, upgrade_place_y = open_upgrade_place_switch(self.user_name)
                                upgrade_item, no_item, new_turn, condition = start_upgrade(upgrade_place_x, upgrade_place_y, self.item_lists, self.type_switch, self.user_name)
                                big_condition = big_condition
                                if new_turn:
                                    condition = kill_game()
                                    definite_kill()
                                elif no_item:
                                    condition = go_hostess()
                                    condition = go_merchant()
                                    condition = buy_items(self.item_lists,1)
                                    condition = go_upgrade_place_switch()
                                    condition = kill_game()
                                    definite_kill()
                                elif upgrade_item:
                                    condition = go_hostess()
                                    condition, total_item_count, loop_count = open_inhostess(self.item_lists,self.user_name,total_item_count,loop_count)
                                    new_loop_info = {
                                        "loop_info": {
                                            "loop_count": str(loop_count),
                                            "total_item_count": str(total_item_count)
                                        }
                                    }
                                    update_json(new_loop_info)
                                    self.total_item_signal.emit(str(total_item_count))
                                    self.loop_count_signal.emit(str(loop_count))
                                    condition = go_merchant()
                                    condition = buy_items(self.item_lists,1)
                                    condition = go_upgrade_place_switch()
                                    condition = kill_game()
                                    definite_kill()
                                else:
                                    condition = kill_game()
                                    definite_kill()
                            kill_game()
                            condition = start_game()
                            condition = otc_running_check()
                            condition = check_and_click('xxx_pic',0.98,file_name_2='xxx_pic_2',s2=0.5)
                            key_press('+enter')
                            condition = login_screen(self.user_name,self.user_pass)
                            condition = otc_screen()
                            condition = check_and_click('startconfirm',0.9)
                            condition = select_server_screen(self.server,self.server_number)
                            condition = check_captcha()
                            condition = character_screen()
                            no_scroll_check = read_json_file()['no_scroll']
                            if self.type_switch == "True":
                                upgrade_place_x, upgrade_place_y = open_upgrade_place_switch(self.user_name)
                                upgrade_item, no_item, new_turn, condition = start_upgrade(upgrade_place_x, upgrade_place_y, self.item_lists, self.type_switch, self.user_name)
                                big_condition = big_condition
                                if new_turn:
                                    condition = kill_game()
                                    definite_kill()
                                elif no_item:
                                    condition = go_hostess()
                                    condition = go_merchant()
                                    condition = buy_items(self.item_lists,1)
                                    condition = go_upgrade_place_switch()
                                    condition = kill_game()
                                    definite_kill()
                                elif upgrade_item:
                                    condition = go_hostess()
                                    condition, total_item_count, loop_count = open_inhostess(self.item_lists,self.user_name,total_item_count,loop_count)
                                    new_loop_info = {
                                        "loop_info": {
                                            "loop_count": str(loop_count),
                                            "total_item_count": str(total_item_count)
                                        }
                                    }
                                    update_json(new_loop_info)
                                    self.total_item_signal.emit(str(total_item_count))
                                    self.loop_count_signal.emit(str(loop_count))
                                    condition = go_merchant()
                                    condition = buy_items(self.item_lists,1)
                                    condition = go_upgrade_place_switch()
                                    condition = kill_game()
                                    definite_kill()
                                else:
                                    condition = kill_game()
                                    definite_kill()
                            else:
                                condition = go_upgrade_place(self.user_name)
                                if self.type_normal == True:
                                    if no_scroll_check == 'True':
                                        condition = go_hostess()
                                        condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key,no_scroll_c=no_scroll_check)
                                        update_json({"no_scroll": "Ready"})
                                        condition = kill_game()
                                        definite_kill()
                                    if no_scroll_check == 'Ready':
                                        condition = go_merchant_ready(self.vip_key)
                                        update_json({"no_scroll": "False"})
                                        pn.send_text('{} {}, pazar kurmaya hazır!!!.'.format(datetime.now().strftime('%H:%M'), self.user_name),
                                            silent=False, devices=[pdevices])
                                        self.disable_durdur_signal.emit(True)
                                        self.is_running = False
                                        self.terminate()
                                        big_condition = False
                                        condition = False
                                    upgrade_place_x, upgrade_place_y = open_upgrade_place()
                                    upgrade_item, no_item, new_turn, condition = start_upgrade(upgrade_place_x, upgrade_place_y, self.item_lists, False, self.user_name)
                                    if new_turn:
                                        condition = kill_game()
                                        definite_kill()
                                    elif no_item:
                                        if self.vip_key:
                                            condition = go_merchant_ready(self.vip_key)
                                            condition = buy_items(self.item_lists,2)
                                        else:
                                            condition = go_hostess()
                                            condition = go_merchant()
                                            condition = buy_items(self.item_lists,1)
                                        condition = kill_game()
                                        definite_kill()
                                    elif upgrade_item:
                                        if self.vip_key:
                                            condition, total_item_count, loop_count, total_vip_key = open_vip_key(self.item_lists,self.user_name,total_item_count,loop_count)
                                            if total_vip_key == 48:
                                                condition = go_hostess()
                                                condition = vip_to_inv(self.item_lists)
                                                condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key)
                                                condition = vip_to_inv(self.item_lists)
                                                condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key, inn_x, inn_y)
                                            elif total_vip_key < 48:
                                                condition = go_merchant_ready(self.vip_key)
                                                condition = buy_items(self.item_lists,2)
                                        else:
                                            condition = go_hostess()
                                            condition, total_item_count, loop_count = open_inhostess(self.item_lists,self.user_name,total_item_count,loop_count,no_scroll_c=no_scroll_check)
                                            condition = go_merchant()
                                            condition = buy_items(self.item_lists,1)

                                        new_loop_info = {
                                            "loop_info": {
                                                "loop_count": str(loop_count),
                                                "total_item_count": str(total_item_count)
                                            }
                                        }
                                        update_json(new_loop_info)
                                        self.total_item_signal.emit(str(total_item_count))
                                        self.loop_count_signal.emit(str(loop_count))
                                        condition = kill_game()
                                        definite_kill()
                                    else:
                                        print('Bi bok var')
                                        condition = kill_game()
                                        definite_kill()

                                elif self.type_christ == True:
                                    if no_scroll_check == 'True':
                                        condition = go_inhostess_christ(self.server_number)
                                        condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess_christ(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key,no_scroll_c=no_scroll_check)
                                        update_json({"no_scroll": "Ready"})
                                        condition = kill_game()
                                        definite_kill()
                                    if no_scroll_check == 'Ready':
                                        condition = go_merchant_ready(self.vip_key)
                                        update_json({"no_scroll": "False"})
                                        pn.send_text('{} {}, pazar kurmaya hazır!!!.'.format(datetime.now().strftime('%H:%M'), self.user_name),
                                            silent=False, devices=[pdevices])
                                        self.disable_durdur_signal.emit(True)
                                        self.is_running = False
                                        self.terminate()
                                        big_condition = False
                                        condition = False
                                    upgrade_place_x, upgrade_place_y = open_upgrade_place()
                                    upgrade_item, no_item, new_turn, condition = start_upgrade(upgrade_place_x, upgrade_place_y, self.item_lists, False, self.user_name)
                                    print(upgrade_item, no_item, new_turn, condition)
                                    if new_turn:
                                        condition = kill_game()
                                        definite_kill()
                                    elif no_item:
                                        if self.vip_key:
                                            condition, total_item_count, loop_count, total_vip_key = open_vip_key(self.item_lists,self.user_name,total_item_count,loop_count)
                                            print(total_vip_key,'no_item')
                                            if total_vip_key == 48:
                                                condition = go_inhostess_christ(self.server_number)
                                                condition = vip_to_inv(self.item_lists)
                                                condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess_christ(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key)
                                                condition = vip_to_inv(self.item_lists)
                                                condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess_christ(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key, inn_x, inn_y)
                                            elif total_vip_key < 48:
                                                condition = go_merchant_ready(self.vip_key)
                                                condition = buy_items(self.item_lists,2)
                                        else:
                                            condition = go_inhostess_christ(self.server_number)
                                            condition = go_merchant_christ()
                                            condition = buy_items(self.item_lists,0)
                                        condition = kill_game()
                                        definite_kill()
                                    elif upgrade_item:
                                        if self.vip_key:
                                            condition, total_item_count, loop_count, total_vip_key = open_vip_key(self.item_lists,self.user_name,total_item_count,loop_count)
                                            print(total_vip_key,'upgrade_item')
                                            if total_vip_key == 48:
                                                condition = go_inhostess_christ(self.server_number)
                                                condition = vip_to_inv(self.item_lists)
                                                condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess_christ(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key)
                                                condition = vip_to_inv(self.item_lists)
                                                condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess_christ(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key, inn_x, inn_y)
                                            elif total_vip_key < 48:
                                                condition = go_merchant_ready(self.vip_key)
                                                condition = buy_items(self.item_lists,2)
                                        else:
                                            condition = go_inhostess_christ(self.server_number)
                                            condition, total_item_count, loop_count, inn_x, inn_y = open_inhostess_christ(self.item_lists,self.user_name,total_item_count,loop_count,self.vip_key)
                                            condition = go_merchant_christ()
                                            condition = buy_items(self.item_lists,0)
                                        new_loop_info = {
                                            "loop_info": {
                                                "loop_count": str(loop_count),
                                                "total_item_count": str(total_item_count)
                                            }
                                        }
                                        update_json(new_loop_info)
                                        self.total_item_signal.emit(str(total_item_count))
                                        self.loop_count_signal.emit(str(loop_count))
                                        condition = kill_game()
                                        definite_kill()
                                    else:
                                        print('Bi bok var')
                                        condition = kill_game()
                                        definite_kill()
                except Exception as e:
                    print(e)
                    pass
            
    def stop(self):
        self.is_running = False
        self.terminate()

class ControlThreadClass(QtCore.QThread):
    control_signal = QtCore.pyqtSignal(bool)
    def __init__(self, parent: None,index=0):
        super(ControlThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.control_check = False

    def run(self):
        if self.type_normal or self.type_christ:
            counter = 0
            while True:
                try:
                    self.control_check = False
                    time.sleep(30)
                    last_time = datetime.strptime(read_json_file()['time_check'], "%m/%d/%Y, %H:%M")
                    if (datetime.now()-last_time).seconds / 60 > 50:
                        print('yeniden başladı')
                        counter+=1
                        if counter > 2:
                            pn.send_text('{} {}, {} kere baştan başladı sorun var!'.format(datetime.now().strftime('%H:%M'),self.user_name,counter),
                                        silent=False, devices=[pdevices])
                        self.control_check = True
                        self.control_signal.emit(self.control_check)
                    else:
                        self.control_check = False
                        self.control_signal.emit(self.control_check)
                except Exception as e:
                    print(e)
                    pass

    def stop(self):
        self.is_running = False
        self.terminate()

class InntoInvThreadClass(QtCore.QThread):
    def __init__(self, parent: None,index=0):
        super(InntoInvThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True

    def run(self):
        inn_to_inv(self.item_lists)

    def stop(self):
        self.is_running = False
        self.terminate()

class ViptoInvThreadClass(QtCore.QThread):
    def __init__(self, parent: None,index=0):
        super(ViptoInvThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True

    def run(self):
        vip_to_inv(self.item_lists)

    def stop(self):
        self.is_running = False
        self.terminate()

class InvtoVipThreadClass(QtCore.QThread):
    def __init__(self, parent: None,index=0):
        super(InvtoVipThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True

    def run(self):
        inv_to_vip(self.item_lists)

    def stop(self):
        self.is_running = False
        self.terminate()

class InvtoInnThreadClass(QtCore.QThread):
    def __init__(self, parent: None,index=0):
        super(InvtoInnThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True

    def run(self):
        inv_to_inn(self.item_lists)

    def stop(self):
        self.is_running = False
        self.terminate()

class SendInputThreadClass(QtCore.QThread):
    def __init__(self, parent: None,index=0):
        super(SendInputThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True

    def run(self):
        def keyboard_listener():
            global stop_threads
            stop_threads = False
            time.sleep(1)
            while True:
                if stop_threads:
                    break
                key = keyboard.read_key()
                print('Normal ', key)
                if key == 'ctrl':
                    stop_threads = True
                    break
                if len(key) == 1:
                    s = serial_open()
                    s.write("-{}\n".format(keyboard.read_key()).encode())
                    print('Fake ', key)
                    time.sleep(0.2)
                    serial_close(s)
                else:
                    s = serial_open()
                    s.write("+{}\n".format(keyboard.read_key()).encode())
                    print('Fake ', key)
                    time.sleep(0.2)
                    serial_close(s)
                time.sleep(0.05)
                

        def mouse_listener():
            global stop_threads
            stop_threads = False
            time.sleep(1)
            while True:
                if stop_threads:
                    break
                while mouse.is_pressed("left"):
                    print('clicked left')
                    s = serial_open()
                    time.sleep(0.05)
                    s.write(b"ld1\n")
                    time.sleep(0.05)
                    s.write(b"ld2\n")
                    time.sleep(0.05)
                    serial_close(s)
                while mouse.is_pressed("right"):
                    print('clicked right')
                    s = serial_open()
                    time.sleep(0.05)
                    s.write(b"rd1\n")
                    time.sleep(0.05)
                    s.write(b"rd2\n")
                    time.sleep(0.05)
                    serial_close(s)
                time.sleep(0.05)
                
        try:
            hwnd = win32gui.FindWindow(None, "Game Client")
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass
        print(self.info)
        stop_threads = False
        t1 = threading.Thread(target=mouse_listener)
        t2 = threading.Thread(target=keyboard_listener)
        t1.start()
        t2.start()
        time.sleep(1)
        print(self.info)
        stop_threads = stop_threads
        t1.join()
        t2.join()

    def stop(self):
        self.is_running = False
        self.terminate()

def serial_open():
    global ser
    try:
        ser = serial.Serial(com, 115200)
        ser.isOpen()
        print ("port is opened!")
    except IOError:
        ser.close()
        ser.open()
        print ("port was already open, was closed and opened again!")
    return ser

def serial_close(ser):
    ser.close()

def key_press(word):
    s = serial_open()
    s.write("{}\n".format(word).encode())
    time.sleep(0.4)
    serial_close(s)

def click(x, y, click_button=0, s1=0, s2=0.2, s3=0.1):
    s = serial_open()
    if click_button == 0:
        time.sleep(0.2)
        pd.moveTo(int(x), int(y))
        s.write(b"ld1\n")
        time.sleep(0.1)
        s.write(b"ld2\n")
        time.sleep(s3+0.5)
    else:
        time.sleep(0.2)
        pd.moveTo(int(x), int(y))
        s.write(b"rd1\n")
        time.sleep(0.1)
        s.write(b"rd2\n")
        time.sleep(s3+0.5)
    serial_close(s)
    
def drag_to(x, y, s1, button):
    s = serial_open()
    if button == 'left':
        time.sleep(0.2)
        s.write(b"ld1\n")
        time.sleep(0.2)
        pd.moveTo(x, y)
        time.sleep(0.2)
        s.write(b"ld2\n")
    else:
        time.sleep(0.2)
        s.write(b"rd1\n")
        time.sleep(0.2)
        pd.moveTo(x, y)
        time.sleep(0.2)
        s.write(b"rd2\n")
    time.sleep(0.2)
    serial_close(s)
    

def locate_png(file_name,con):
    if file_name != None:
        file ='./bdata/'+file_name+'.png'
        locate = pau.locateOnScreen(file, confidence = con)
        if locate != None:
            x, y, w, h = locate
            return x+int(w/2), y+int(h/2)
        else:
            return None
    else:
        return None

def if_click(file_name,con,click_button=0,s1=0, s2=0.2, s3=0.1):
    locate = locate_png(file_name,con)
    if locate != None:
        x, y = locate
        if w_sizen-300 > x > 500:
            click(x,y,click_button,s1,s2,s3)

def check_and_click(file_name,con,file_name_2 = None,click_button=0,s1=0, s2=0.2, s3=0.1):
    condition = True
    counter = 0
    while True:
        locate = locate_png(file_name,con)
        if locate != None:
            x, y = locate
            click(x,y,click_button,s1,s2,s3)
            break
        locate = locate_png(file_name_2,con)
        if locate != None:
            x, y = locate
            click(x,y,click_button,s1,s2,s3)
            break
        time.sleep(0.05)
        print(counter,file_name,file_name_2)
        counter+=1
        if counter > 91:
            condition = False
            break
    return x, y, condition
    
def check_and_click_other(file_name, con, x, y, file_name_2 = None, click_button=0, s1=0, s2=0.2, s3=0.1):
    condition = True
    counter = 0
    while True:
        locate = locate_png(file_name,con)
        if locate != None:
            click(x,y,click_button,s1,s2,s3)
            break
        locate = locate_png(file_name_2,con)
        if locate != None:
            click(x,y,click_button,s1,s2,s3)
            break
        time.sleep(0.05)
        print(counter,file_name,file_name_2)
        counter+=1
        if counter > 91:
            condition = False
            break
    return condition

def get_items(location, item_list):
    if location == 0:
        new_item_list = item_list[0]
        con = 0.98
    elif location == 1:
        new_item_list = item_list[1]
        con = 0.98
    elif location == 2:
        new_item_list = item_list[2]
        con = 0.98
    elif location == 3:
        new_item_list = item_list[0]
        con = 0.98
    elif location == 4:
        new_item_list = item_list[0]
        con = 0.98
    item_cor_list = []
    for item_name in new_item_list:
        sep_item_cor_list = []
        for item in pau.locateAllOnScreen('./bdata/'+item_name+'.png',confidence=con):
            x, y, w, h = item
            if location == 0:
                if x > 970 and y > 386:
                    item_cor_list.append((x+int(w/2), y+int(h/2)))
            elif location == 1:
                if y < 339:
                    item_cor_list.append((x+int(w/2), y+int(h/2)))
            elif location == 2:
                if y > 320:
                    sep_item_cor_list.append((x+int(w/2), y+int(h/2)))
            elif location == 3:
                if x > 970 and y < 386:
                    item_cor_list.append((x+int(w/2), y+int(h/2)))
            elif location == 4:
                if 600 < x < 970:
                    item_cor_list.append((x+int(w/2), y+int(h/2)))
        if location == 2:
            item_cor_list.append(sep_item_cor_list)

    return item_cor_list

def otc_time_tesseract():
    while True:
        try:
            otc_seconds = pau.screenshot(region=(998, 615, 1019-998, 629-615))
            path_to_image = 'C:/tesseract.png'
            otc_seconds.save(path_to_image)
            path_to_tesseract = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
            img = Image.open(path_to_image)
            pytesseract.tesseract_cmd = path_to_tesseract
            text = pytesseract.image_to_string(img,lang='eng', config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')
            text = int(text[:-1])
            break
        except:
            pass
    return text

def control_dc_cancel():
    condition = True
    if check_dc():
        condition = False
    if_click('block_user',0.8)
    if_click('cancel',0.8)
    return condition

def otc_running_check():
    condition = True
    counter = 0
    while True:
        otc_running_check = [True for proc in psutil.process_iter() if proc.name() == "onetimecode.exe"]
        if otc_running_check == [True]:
            break
        else:
            os.startfile(otcfolder)
        time.sleep(0.1)
        print(counter,'otc running check')
        counter+=1
        if counter > 91:
            condition = False
            break
    return condition

def kill_game():
    global condition
    condition = False
    for proc in psutil.process_iter():
        if proc.name() == "game.exe":
            proc.kill()
        if proc.name() == "Launcher.exe":
            proc.kill()
        if proc.name() == "onetimecode.exe":
            proc.kill()
        if proc.name() == "msedge.exe":
            proc.kill()
    time.sleep(1)
    return condition

def definite_kill():
    x = int('error')

def kill_exe(exe_name):
    for proc in psutil.process_iter():
        if proc.name() == exe_name:
            proc.kill()

def get_captcha():
    ilkcaptcha = pau.screenshot(region=(550, 390, 240, 62))
    ilkcaptcha.save("./bdata/Capture.png")
    with open('./bdata/Capture.png', 'rb') as captcha_file:
        captcha2 = azapi.solve(captcha_file)
    captcha1 = str(captcha2.await_result()).lower()
    return captcha1

def check_dc():
    for i in range(5):
        if locate_png('dc'+str(i),0.8) != None:
            return True
    return False

def start_game():
    os.startfile(gamefolder)
    condition = True
    counter = 0
    while True:
        locate = locate_png('update_completed',0.95)
        if locate != None:
            time.sleep(0.5)
            click(w_size/2,h_size/2+200,s2=0.3)
            small_con = True
            while small_con:
                locate = locate_png('update_completed',0.95)
                if locate == None:
                    time.sleep(0.5)
                    small_con = False
                else:
                    click(w_size/2,h_size/2+200,s2=0.3)
                time.sleep(1)
            break
        locate = locate_png('patch_data_check',0.95)
        if locate != None:
            time.sleep(0.1)
            x, y = locate_png('patch_data_ok',0.95)
            click(x, y)
            time.sleep(0.1)
            os.startfile(gamefolder)
            while True:
                locate = locate_png('patch_data',0.95)
                if locate != None:
                    x, y = locate_png('launcher_close',0.95)
                    click(x, y, s2=0.2,s3=0.5)
                    locate = locate_png('code_error_check',0.95)
                    if locate != None:
                        x, y = locate('code_error_ok',0.95)
                        click(x, y, s2=0.2)
                    kill_game()
                    definite_kill()
                    break
                counter+=1
                if counter > 91:
                    condition = False
                    break
            kill_game()
            definite_kill()
            break
        time.sleep(0.01)
        print(counter,'Start ko')
        counter+=1
        if counter > 91:
            condition = False
            break
    return condition

def login_screen(user_name,user_pass):
    condition = True
    counter = 0
    while True:
        if locate_png('login',0.95) != None:
            key_press('-{}'.format(user_name))
            time.sleep(1.5)
            key_press('+tab')
            time.sleep(0.1)
            key_press('-{}'.format(user_pass))
            time.sleep(1.5)
            hwnd = win32gui.FindWindow(None, "Anyotc")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            locate = locate_png('otcpassword',0.8)
            if locate_png('otcpassword',0.8) != None:
                x, y = locate
                pd.mouseUp(x, y)
                pd.mouseUp(x, y, button='right')
                pd.mouseUp(x, y)
                pd.mouseUp(x, y, button='right')
                for key in '343834':
                    x, y = locate_png(key,0.95)
                    click(x,y,s2=0.2)
                check_and_click('otcconfirm',0.9)
                if locate_png('otcpasserror',0.8) != None:
                    check_and_click('otcpassok',0.8)
                    check_and_click('otcpassreset',0.8)
                else:
                    if otc_time_tesseract() < 11:
                        time.sleep(12)
                    check_and_click('otccopy',0.9,file_name_2='otccopy_2')
                    kill_exe('onetimecode.exe')
            x, y = locate_png('login',0.95)
            click(x, y, s3=0.01)
            key_press('+enter')
            time.sleep(0.5)
            if locate_png('invalid_pass',0.8) != None:
                key_press('+enter')
                time.sleep(0.5)
                key_press('+enter')
                time.sleep(0.5)
            break
        if check_dc():
            kill_game()
            definite_kill()
        time.sleep(0.01)
        counter+=1
        if counter > 121:
            kill_game()
            definite_kill()
            condition = False
            break
    return condition

def otc_screen():
    condition = True
    counter = 0
    while True:
        if locate_png('otcok',0.7) != None:
            time.sleep(0.1)
            pau.hotkey('ctrl','v')
            x, y = locate_png('otcok',0.9)
            click(x, y)
            time.sleep(0.3)
            if locate_png('otcerror',0.8) != None:
                kill_game()
                definite_kill()
            else:
                break
        if locate_png('invalid_pass',0.8) != None:
            key_press('+enter')
            time.sleep(0.5)
            key_press('+enter')
            time.sleep(0.5)
        if check_dc():
            kill_game()
            definite_kill()
            condition = False
            break
        time.sleep(0.01)
        print(counter,'otc screen')
        counter+=1
        if counter > 91:
            kill_game()
            definite_kill()
            condition = False
            break
    return condition

def select_server_screen(server,server_number):
    condition = True
    counter = 0
    while True:
        if locate_png('selectserver',0.9) != None:
            try:
                x, y = locate_png('minark',0.8)
                click(x,y,s2=0.2)
            except:
                x, y = locate_png('destan',0.8)
                click(x,y,s2=0.2)
            finally:
                x, y = locate_png(server,0.8)
                click(x,y,s2=0.2)
            check_and_click(server_number,0.98)
            key_press('+enter')
            time.sleep(0.5)
            break
        if check_dc():
            kill_game()
            definite_kill()
        time.sleep(0.01)
        print(counter,'Select server screen')
        counter+=1
        if counter > 91:
            kill_game()
            definite_kill()
            condition = False
            break
    return condition

def check_captcha():
    condition = True
    counter = 0
    while True:
        if locate_png('retrycaptcha',0.8) != None:
            capt = get_captcha()
            print(capt)
            check_and_click('ilkcaptchainput',0.8,s2=0.2)
            pd.write(capt)
            check_and_click('captcha_confirm',0.9,s3=1)
            key_press('+enter')
            time.sleep(1)
            if locate_png('captchaerror',0.6) != None:
                check_and_click('captchaerror_confirm',0.9,s3=1)
                check_and_click('retrycaptcha',0.8,s2=0.2,s3=1)
            if locate_png('retrycaptcha',0.8) == None:
                break
        if locate_png('retrycaptcha',0.8) == None and locate_png('selectserver',0.9) == None:
            break
        if locate_png('server_full',0.8) == None and locate_png('selectserver',0.9) == None and locate_png('retrycaptcha',0.8) == None:
            break
        if check_dc():
            kill_game()
            definite_kill()
        time.sleep(0.01)
        print(counter,'Sıra bekliyor!')
        counter+=1
    return condition

def character_screen():
    if locate_png('server_full',0.8) == None and locate_png('selectserver',0.9) == None:
        key_press('+enter')
        time.sleep(0.5)
        key_press('+enter')
        time.sleep(0.5)
        if locate_png('selectcharacter',0.7):
            key_press('+enter')
            time.sleep(0.5)
            key_press('+enter')
    condition = True
    while True:
        if locate_png('menuler',0.7) != None:
            break
        if check_dc():
            kill_game()
            definite_kill()
            condition = False
            break
        time.sleep(1)
    return condition

def go_upgrade_place(user_name):
    condition = True
    counter = 0
    while True:
        if locate_png('menuler',0.7) != None:
            click(60,60)
            key_press('-m')
            time.sleep(0.5)
            if locate_png('inmap',0.8) != None:
                map_loc = 'inmap'
                print(map_loc)
                key_press('+esc')
                key_press('-o')
                key_press('+F10')
                check_and_click('option',0.95)
                check_and_click('rewishper',0.95)
                check_and_click('reparty',0.95)
                if_click('savesettings',0.95,s3=0.01)
                key_press('+esc')
                click(int(w_sizen/2)+pc_data['inmap_px_1'],65)
                time.sleep(pc_data['inmap_sleep_1'])
                condition = control_dc_cancel()
                key_press('+esc')
                click(int(w_sizen/2)+pc_data['inmap_px_2'],65)
                time.sleep(pc_data['inmap_sleep_2'])
                break

            elif locate_png('outmap',0.8) != None:
                map_loc = 'outmap'
                print(map_loc)
                key_press('+esc')
                key_press('-o')
                condition = control_dc_cancel()
                key_press('+F10')
                check_and_click('option',0.95)
                check_and_click('rewishper',0.95)
                check_and_click('reparty',0.95)
                if_click('savesettings',0.95,s3=0.01)
                key_press('+esc')
                click(int(w_sizen/2)+pc_data['outmap_px_1'],int(h_sizen/2-337))
                time.sleep(pc_data['outmap_sleep_1'])
                key_press('+esc')
                click(int(w_sizen/2)+pc_data['outmap_px_2'],65)
                time.sleep(pc_data['outmap_sleep_2'])
                break
        time.sleep(0.01)
        print(counter,'Go upgrade_place')
        counter+=1
        if counter > 121:
            kill_game()
            definite_kill()
            condition = False
            break
    return condition
            
def go_upgrade_place_switch():
    condition = True
    key_press('+esc')
    time.sleep(0.5)
    key_press('-x')
    time.sleep(0.5)
    key_press('-d')
    time.sleep(0.5)
    key_press('-s')
    time.sleep(0.5)
    dondur = 110
    pau.moveTo(int(w_sizen/2), 60)
    counter = 0
    g_counter = 0
    mini_condition = True
    while mini_condition:
        dondur+=3
        counter+=1
        if counter < 40:
            drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
            time.sleep(0.1)
            for i in range(5):
                locate = locate_png('anv_'+str(i),0.6)
                if locate != None:
                    x, y = locate
                    click(x+15, y)
                    mini_condition = False
                    break
            if locate != None:
                break
            if counter == 39:
                kill_game()
                definite_kill()
                condition = False
                break
        time.sleep(0.01)
        g_counter+=1
        if g_counter > 120:
            kill_game()
            definite_kill()
            condition = False
            break
    time.sleep(12)
    return condition

def open_upgrade_place():
    key_press('+esc')
    time.sleep(0.1)
    key_press('-x')
    time.sleep(0.1)
    condition = control_dc_cancel()
    key_press('-b')
    time.sleep(0.1)
    counter = 0
    m_con = True
    while m_con:
        for i in range(4):
            locate = locate_png('upgrade_place_'+str(i),0.8)
            if locate != None:
                upgrade_place_x, upgrade_place_y = locate
                print(upgrade_place_x, upgrade_place_y)
                click(upgrade_place_x, upgrade_place_y, click_button=1, s2=0.3)
                time.sleep(0.3)
                m_con = False
                break
        print(counter,'Open upgrade_place')
        counter+=1
        if counter > 90:
            kill_game()
            definite_kill()
            condition = False
            break
                
    check_and_click('upgrade1',0.9)
    time.sleep(0.1)
    return upgrade_place_x, upgrade_place_y

def open_upgrade_place_switch(user_name):
    condition = True
    counter = 0
    while True:
        if locate_png('menuler',0.7) != None:
            key_press('+esc')
            time.sleep(0.5)
            condition = control_dc_cancel()
            key_press('-o')
            time.sleep(0.5)
            key_press('-b')
            time.sleep(0.5)
            key_press('-e')
            time.sleep(0.5)
            upgrade_place_x, upgrade_place_y, condition = check_and_click('upgrade_place',0.8,click_button=1)
            check_and_click('upgrade1',0.9)
            break
        time.sleep(0.01)
        print(counter,'Open upgrade_place')
        counter+=1
        if counter > 121:
            pn.send_text('{} {}, upgrade_place acilmadi.'.format(datetime.now().strftime('%H:%M'), user_name),
                            silent=False, devices=[pdevices])
            condition = False
            break
    return upgrade_place_x, upgrade_place_y

def start_upgrade(upgrade_place_x, upgrade_place_y, item_list, bot_type, user_name):
    condition = True
    new_turn = False
    time.sleep(2)
    counter = 31
    g_counter = 0
    l_condition = True
    if locate_png('uscroll',0.8) != None:
        u_x, u_y = locate_png('uscroll',0.8)
        if u_x > 1265 and u_y > 565:
            pass
        else:
            u_x, u_y = relocate_scroll(user_name)
            if bot_type:
                open_upgrade_place_switch()
                time.sleep(2)
            else:
                open_upgrade_place()
                time.sleep(2)
        try:
            update_json({'no_scroll':'False'})
        except:
            pass
    else:
        print('Kağıt bitti')
        pn.send_text('{} {} kağıt bitti. Pazar hazırlığı yapılıyor.'.format(datetime.now().strftime('%H:%M'), user_name),
                                silent=False, devices=[pdevices])
        try:
            update_json({'no_scroll':'True'})
        except:
            pass
        kill_game()
        definite_kill()
    while l_condition:
        if locate_png('confirm1', 0.6) != None:
            g_counter = 0
            upgraded_list = []
            item_cord_list = get_items(0,item_list)
            if len(item_cord_list) == 0:
                no_item = True
                l_condition = False
            else:
                no_item = False
            for item_cord in item_cord_list:
                if_click('block_user',0.8)
                x, y = item_cord
                click(x, y)
                time.sleep(0.1)
                if locate_png('item+7',0.95) == None:
                    if_click('block_user',0.8)
                    click(x, y, click_button=1)
                    click(u_x, u_y, click_button=1)
                    x, y = locate_png('confirm1', 0.6)
                    click(x, y)
                    while True:
                        if_click('block_user',0.8)
                        locate = locate_png('confirm2', 0.6)
                        if locate != None:
                            x, y = locate
                            if x > 900:
                                click(x, y)
                                break
                        time.sleep(0.01)
                        g_counter+=1
                        if g_counter > 60:
                            upgrade_comp = False
                            condition = False
                            kill_game()
                            definite_kill()
                            l_condition = False
                            break
                    if_click('block_user',0.8)
                    click(upgrade_place_x, upgrade_place_y, click_button=1)
                    check_and_click('upgrade1', 0.9)
                    counter-=1
                else:
                    upgraded_list.append([x, y])    
                
                if counter == 0:
                    new_turn = True
                    l_condition = False
                    break
            if bot_type:
                if len(item_cord_list) == len(upgraded_list):
                    upgrade_comp = True
                    condition = False
                    l_condition = False
                else:
                    upgrade_comp = False
            else:
                if len(item_cord_list) == len(upgraded_list):
                    upgrade_comp = True
                    l_condition = False
                else:
                    upgrade_comp = False

        time.sleep(0.01)
        g_counter+=1
        if g_counter > 60:
            kill_game()
            definite_kill()
            condition = False
            break
    return upgrade_comp, no_item, new_turn, condition

def go_hostess():
    condition = True
    key_press('+esc')
    time.sleep(0.3)
    key_press('-x')
    time.sleep(0.3)
    dondur = 15
    pau.moveTo(int(w_sizen/2), 60)
    time.sleep(0.1)
    for i in range(2):
        drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
        time.sleep(0.1)
        dondur+=15
    dondur = 1
    time.sleep(0.3)
    counter = 0
    g_counter = 0
    while True:
        print(dondur,'normal_innhostess')
        dondur+=1
        counter+=1
        if counter < 30:
            drag_to(int(w_sizen/2)-dondur, 60,0.1, button='right')
            time.sleep(0.1)
            for i in range(1,5):
                locate = locate_png('min'+str(i),0.6)
                if locate != None:
                    x, y = locate
                    click(x+3, 35)
                    break
            if locate != None:
                break
            if counter == 29:
                pau.moveTo(int(w_sizen/2), 60)
                dondur = 0
        elif 50 >= counter >= 30:
            drag_to(int(w_sizen/2)+dondur, 60,0.3, button='right')
            time.sleep(0.1)
            for i in range(1,5):
                locate = locate_png('min'+str(i),0.6)
                if locate != None:
                    x, y = locate
                    click(x+3, 35)
                    break
            if locate != None:
                break
            if counter > 50:
                kill_game()
                definite_kill()
                condition = False
                break
        time.sleep(0.01)
        g_counter+=1
        if g_counter > 60:
            kill_game()
            definite_kill()
            condition = False
            break
    time.sleep(12)
    return condition

def open_inhostess(item_list, user_name, total_item_count, loop_count, vip_key, inn_x = 0, inn_y = 0, no_scroll_c = 'False'):
    loop_count = int(loop_count)
    total_item_count = int(total_item_count)
    condition = True
    condition = control_dc_cancel()
    key_press('+esc')
    key_press('-b')
    counter = 0
    while True:
        if inn_x == 0:
            locate = locate_png('inhostess',0.65)
            if locate != None:
                x, y = locate
                inn_x, inn_y = x, y+110
                click(inn_x, inn_y,click_button=1,s3=1)
                time.sleep(0.5)
                if locate_png('usestorage',0.8) == None:
                    click(x, y+160,click_button=1)
                    time.sleep(0.45)
                check_and_click('usestorage',0.8)
                time.sleep(0.3)
                pau.moveTo(int(w_sizen/2), 35)
                time.sleep(0.1)
                break
        else:
            click(inn_x, inn_y,click_button=1,s3=1)
            time.sleep(0.5)
            if locate_png('usestorage',0.8) == None:
                click(inn_x, inn_y+50,click_button=1)
                time.sleep(0.45)
            check_and_click('usestorage',0.8)
            time.sleep(0.3)
            pau.moveTo(int(w_sizen/2), 35)
            break
        time.sleep(0.01)
        print(counter,'Open inhostes')
        counter+=1
        if counter > 91:
            kill_game()
            definite_kill()
            condition = False
            break
    if no_scroll_c == 'False':
        counter = 0
        while True:
            if locate_png('incheck',0.9) != None:
                time.sleep(1)
                item_cord_list = get_items(0,item_list)
                if len(item_cord_list) == 0:
                    time.sleep(1)
                    break
                else:
                    for item_cord in item_cord_list:
                        x, y = item_cord
                        click(x, y, click_button=1, s2=0.2)
                        time.sleep(0.45)
                if vip_key == False:
                    total_item_count+=len(item_cord_list)
                    loop_count+=1
                    pn.send_text('{} Tur: {}, {}, toplam {} item bastı.'.format(datetime.now().strftime('%H:%M'), loop_count, user_name, total_item_count),
                                    silent=False, devices=[pdevices])
                else:
                    pn.send_text('{} {}, vip\'ten depoya.'.format(datetime.now().strftime('%H:%M'), user_name),
                                    silent=False, devices=[pdevices])
            time.sleep(0.01)
            print(counter,'Incheck')
            counter+=1
            if counter > 91:
                kill_game()
                definite_kill()
                condition = False
                break
    else:
        counter = 0
        while True:
            if locate_png('incheck',0.9) != None:
                time.sleep(1)
                item_cord_list = get_items(0,item_list)
                if len(item_cord_list) == 0:
                    time.sleep(1)
                    for i in range(7):
                        empty_total = []
                        for item in pau.locateAllOnScreen('./bdata/inv_empty_box.png',confidence=0.9):
                            x, y, w, h = item
                            if x > 970 and y > 386:
                                empty_total.append(item)
                        empty_total_count = len(empty_total)
                        item_cord_list = get_items(3,item_list)
                        print(empty_total_count)
                        if empty_total_count > 0:
                            for item_cord in item_cord_list[:empty_total_count]:
                                x, y = item_cord
                                click(x, y, click_button=1)
                                time.sleep(0.45)
                                empty_total_count-=1
                            pd.moveTo(60,60)
                            time.sleep(0.1)
                            x, y = locate_png('inn_next',0.9)
                            click(x, y, s2=0.2,s3=0.5)
                            time.sleep(0.3)
                            if i == 0:
                                pn.send_text('{} {} depo boş sıkıntı var!'.format(datetime.now().strftime('%H:%M'), user_name),
                                    silent=False, devices=[pdevices])
                                break
                        else:
                            print('bitti')
                            break
                else:
                    while True:
                        empty_total = []
                        for item in pau.locateAllOnScreen('./bdata/inn_empty_box.png',confidence=0.9):
                            x, y, w, h = item
                            if x > 970 and y < 386:
                                empty_total.append((x+int(w/2), y+int(h/2)))
                        empty_total_count = len(empty_total)
                        print(empty_total_count)
                        if empty_total_count == 24:
                            break
                        else:
                            x, y = locate_png('inn_next',0.9)
                            click(x, y, s2=0.2)
                            time.sleep(0.3)
                    
                    if len(item_cord_list) <=24:
                        for item_cord in item_cord_list[:empty_total_count]:
                            x, y = item_cord
                            click(x, y, click_button=1, s2=0.2)
                            time.sleep(0.45)

                    else:
                        for item_cord in item_cord_list[:empty_total_count]:
                            x, y = item_cord
                            click(x, y, click_button=1, s2=0.2)
                            time.sleep(0.45)
                        x, y = locate_png('inn_next',0.9)
                        click(x, y, s2=0.2,s3=0.5)
                        for item_cord in item_cord_list[empty_total_count:]:
                            x, y = item_cord
                            click(x, y, click_button=1, s2=0.2)
                            time.sleep(0.45)
                    x, y = locate_png('inn_back',0.9)
                    for i in range(8):
                        click(x, y, s2=0.2,s3=0.5)
                        time.sleep(0.5)
                    while True:
                        empty_total = []
                        for item in pau.locateAllOnScreen('./bdata/inv_empty_box.png',confidence=0.9):
                            x, y, w, h = item
                            print(item)
                            if x > 970 and y > 386:
                                empty_total.append(item)
                        empty_total_count = len(empty_total)
                        item_cord_list = get_items(3,item_list)
                        print(empty_total_count)
                        if empty_total_count > 0:
                            for item_cord in item_cord_list[:empty_total_count]:
                                x, y = item_cord
                                click(x, y, click_button=1)
                                time.sleep(0.45)
                                empty_total_count-=1
                            pd.moveTo(60,60)
                            time.sleep(0.1)
                            x, y = locate_png('inn_next',0.9)
                            click(x, y, s2=0.2,s3=0.5)
                            time.sleep(0.5)
                        else:
                            print('bitti')
                            break
                break
            time.sleep(0.01)
            print(counter,'Prepare for merchant')
            counter+=1
            if counter > 91:
                kill_game()
                definite_kill()
                condition = False
                break
    return condition, total_item_count, loop_count, inn_x, inn_y
        
def go_merchant():
    print('go merchant started')
    condition = True
    key_press('+esc')
    key_press('-x')
    dondur = 50
    pau.moveTo(int(w_sizen/2), 60)
    counter = 0
    g_counter = 0
    mini_condition = True
    while mini_condition:
        dondur+=3
        counter+=1
        if counter < 60:
            drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
            time.sleep(0.1)
            for i in range(1,5):
                locate = locate_png('fab'+str(i),0.6)
                if locate != None:
                    x, y = locate
                    click(x-30, 35)
                    mini_condition = False
                    break
            if locate != None:
                break
            if counter == 59:
                pau.moveTo(int(w_sizen/2), 60)
                dondur = 0
        elif 120 >= counter >= 60:
            drag_to(int(w_sizen/2)+dondur, 60,0.3, button='right')
            time.sleep(0.1)
            for i in range(1,5):
                locate = locate_png('fab'+str(i),0.6)
                if locate != None:
                    x, y = locate
                    click(x-30, 35)
                    mini_condition = False
                    break
            if locate != None:
                break
            if counter > 120:
                kill_game()
                definite_kill()
                condition = False
                break
        time.sleep(0.01)
        g_counter+=1
        if g_counter > 120:
            kill_game()
            definite_kill()
            condition = False
            break
    time.sleep(8)
    return condition

def go_inhostess_christ(server_num):
    condition = True
    key_press('+esc')
    time.sleep(0.3)
    key_press('-x')
    time.sleep(0.3)
    click(60,60)
    time.sleep(0.3)
    dondur = pc_data['christ_go_inn_dondur_1']
    pau.moveTo(int(w_sizen/2), 60)
    for i in range(pc_data['christ_go_inn_for_1']):
        drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
        dondur+=pc_data['christ_go_inn_dondur_1']
    dondur = pc_data['christ_go_inn_dondur_2']
    pau.moveTo(int(w_sizen/2), 60)
    counter = 0
    while True:
        if counter < 200:
            drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
            for i in range(2):
                locate = locate_png('inn_'+str(i),0.7)
                if locate != None:
                    x, y = locate
                    click(x+pc_data['christ_go_inn_x_1'], y+40)
                    break
            if locate != None:
                break
            if counter == 199:
                kill_game()
                definite_kill()
                condition = False
                break
        dondur+=pc_data['christ_go_inn_dondur_2']
        counter+=1
    time.sleep(1)
    dondur = pc_data['christ_go_inn_dondur_3']
    pau.moveTo(int(w_sizen/2), 60)
    for i in range(pc_data['christ_go_inn_for_2']):
        drag_to(int(w_sizen/2)+dondur, 60,0.3, button='right')
        dondur+=pc_data['christ_go_inn_dondur_3']
    dondur = pc_data['christ_go_inn_dondur_4']
    counter = 0
    while True:
        if counter < 200:
            drag_to(int(w_sizen/2)+dondur, 60,0.3, button='right')
            for i in range(3):
                locate = locate_png('inn_1_'+str(i),0.7)
                if locate != None:
                    x, y = locate
                    print(server_num)
                    if server_num == 'zero_5':
                        click(x+33, y+20)
                    else:
                        click(x+pc_data['christ_go_inn_x_2'], y+20)
                    break
            if locate != None:
                break
            if counter == 199:
                kill_game()
                definite_kill()
                condition = False
                break
        dondur+=pc_data['christ_go_inn_dondur_4']
        counter+=1
    time.sleep(10)
    return condition

def open_inhostess_christ(item_list, user_name, total_item_count, loop_count, vip_key, inn_x = 0, inn_y = 0, no_scroll_c = 'False'):
    loop_count = int(loop_count)
    total_item_count = int(total_item_count)
    condition = True
    condition = control_dc_cancel()
    key_press('+esc')
    key_press('-b')
    counter = 0
    while True:
        if inn_x == 0:
            locate = locate_png('inhostess_christ',0.65)
            if locate != None:
                x, y = locate
                inn_x, inn_y = x+20, y+100
                click(inn_x, inn_y,click_button=1,s3=1)
                if locate_png('usestorage',0.8) == None:
                    click(inn_x, inn_y+50,click_button=1)
                check_and_click('usestorage',0.8)
                pau.moveTo(int(w_sizen/2), 35)
                break
        else:
            click(inn_x, inn_y,click_button=1,s3=1)
            if locate_png('usestorage',0.8) == None:
                click(inn_x, inn_y+50,click_button=1)
            check_and_click('usestorage',0.8)
            pau.moveTo(int(w_sizen/2), 35)
            break
        time.sleep(0.01)
        print(counter,'Open inhostes')
        counter+=1
        if counter > 121:
            kill_game()
            definite_kill()
            condition = False
            break
    if no_scroll_c == 'False':
        counter = 0
        while True:
            if locate_png('incheck',0.9) != None:
                item_cord_list = get_items(0,item_list)
                if len(item_cord_list) == 0:
                    break
                else:
                    for item_cord in item_cord_list:
                        x, y = item_cord
                        click(x, y, click_button=1)
                if vip_key == False:
                    total_item_count+=len(item_cord_list)
                    loop_count+=1
                    pn.send_text('{} Tur: {}, {}, toplam {} item bastı.'.format(datetime.now().strftime('%H:%M'), loop_count, user_name, total_item_count),
                                    silent=False, devices=[pdevices])
                else:
                    pn.send_text('{} {}, vip\'ten depoya.'.format(datetime.now().strftime('%H:%M'), user_name),
                                    silent=False, devices=[pdevices])
            time.sleep(0.01)
            print(counter,'Incheck')
            counter+=1
            if counter > 91:
                kill_game()
                definite_kill()
                condition = False
                break
    else:
        counter = 0
        while True:
            if locate_png('incheck',0.9) != None:
                time.sleep(1)
                item_cord_list = get_items(0,item_list)
                if len(item_cord_list) == 0:
                    time.sleep(1)
                    for i in range(7):
                        empty_total = []
                        for item in pau.locateAllOnScreen('./bdata/inv_empty_box.png',confidence=0.9):
                            x, y, w, h = item
                            if x > 970 and y > 386:
                                empty_total.append(item)
                        empty_total_count = len(empty_total)
                        item_cord_list = get_items(3,item_list)
                        print(empty_total_count)
                        if empty_total_count > 0:
                            for item_cord in item_cord_list[:empty_total_count]:
                                x, y = item_cord
                                click(x, y, click_button=1)
                                empty_total_count-=1
                            pd.moveTo(60,60)
                            time.sleep(0.1)
                            x, y = locate_png('inn_next',0.9)
                            click(x, y, s2=0.2,s3=0.5)
                            if i == 0:
                                pn.send_text('{} {} depo boş sıkıntı var!'.format(datetime.now().strftime('%H:%M'), user_name),
                                    silent=False, devices=[pdevices])
                                break
                        else:
                            print('bitti')
                            break
                else:
                    while True:
                        empty_total = []
                        for item in pau.locateAllOnScreen('./bdata/inn_empty_box.png',confidence=0.9):
                            x, y, w, h = item
                            if x > 970 and y < 386:
                                empty_total.append((x+int(w/2), y+int(h/2)))
                        empty_total_count = len(empty_total)
                        print(empty_total_count)
                        if empty_total_count == 24:
                            break
                        else:
                            x, y = locate_png('inn_next',0.9)
                            click(x, y, s2=0.2,s3=0.5)
                    
                    if len(item_cord_list) <=24:
                        for item_cord in item_cord_list[:empty_total_count]:
                            x, y = item_cord
                            click(x, y, click_button=1, s2=0.2, s3=0.3)
                    else:
                        for item_cord in item_cord_list[:empty_total_count]:
                            x, y = item_cord
                            click(x, y, click_button=1, s2=0.2, s3=0.3)
                        x, y = locate_png('inn_next',0.9)
                        click(x, y, s2=0.2,s3=0.5)
                        for item_cord in item_cord_list[empty_total_count:]:
                            x, y = item_cord
                            click(x, y, click_button=1, s2=0.2, s3=0.3)
                    x, y = locate_png('inn_back',0.9)
                    for i in range(8):
                        click(x, y, s2=0.2,s3=0.5)
                    while True:
                        empty_total = []
                        for item in pau.locateAllOnScreen('./bdata/inv_empty_box.png',confidence=0.9):
                            x, y, w, h = item
                            print(item)
                            if x > 970 and y > 386:
                                empty_total.append(item)
                        empty_total_count = len(empty_total)
                        item_cord_list = get_items(3,item_list)
                        print(empty_total_count)
                        if empty_total_count > 0:
                            for item_cord in item_cord_list[:empty_total_count]:
                                x, y = item_cord
                                click(x, y, click_button=1)
                                empty_total_count-=1
                            pd.moveTo(60,60)
                            time.sleep(0.1)
                            x, y = locate_png('inn_next',0.9)
                            click(x, y, s2=0.2,s3=0.5)
                        else:
                            print('bitti')
                            break
                break
            time.sleep(0.01)
            print(counter,'Prepare for merchant')
            counter+=1
            if counter > 91:
                kill_game()
                definite_kill()
                condition = False
                break
    return condition, total_item_count, loop_count, inn_x, inn_y
        
def go_merchant_christ():
    print('go merchant christ started')
    condition = True
    key_press('+esc')
    key_press('-x')
    for _ in range(2):
        dondur = pc_data['christ_go_merc_dondur_1']
        pau.moveTo(int(w_sizen/2), 60)
        for i in range(pc_data['christ_go_merc_for_1']):
            drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
            dondur+=pc_data['christ_go_merc_dondur_1']
    dondur = pc_data['christ_go_merc_dondur_2']
    pau.moveTo(int(w_sizen/2), 60)
    counter = 0
    mini_condition = True
    while mini_condition:
        if counter < 200:
            drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
            for i in range(3):
                locate = locate_png('fab_'+str(i),0.8)
                if locate != None:
                    x, y = locate
                    click(x+pc_data['christ_go_merc_x_1'], y+60)
                    mini_condition = False
                    break
            if locate != None:
                break
            if counter == 199:
                kill_game()
                definite_kill()
                condition = False
                break
        dondur+=pc_data['christ_go_merc_dondur_2']
        counter+=1

    time.sleep(9)
    return condition

def buy_items(item_list,bot_type_int):
    if bot_type_int == 0:
        armor_png = 'clothesci_christ'
    elif bot_type_int == 1:
        armor_png = 'clothesci'
    elif bot_type_int == 2:
        armor_png = 'clothesci_vip'
    condition = True
    condition = control_dc_cancel()
    if bot_type_int != 2:
        key_press('-b')
    counter = 0
    while True:
        locate = locate_png(armor_png,0.65)
        if locate != None:
            x, y = locate
            if bot_type_int != 2:
                click(x+40, y+140)
                click(x+40, y+140,click_button=1)
                time.sleep(0.3)
            elif bot_type_int == 2:
                click(x-10, y+140)
                click(x-10, y+140,click_button=1)
                time.sleep(0.3)
            check_and_click('clothestrade',0.8)
            pau.moveTo(int(w_sizen/2), 35)
            time.sleep(1)
            break
        time.sleep(0.01)
        print(counter,'Find clothes merchant')
        counter+=1
        if counter > 91:
            kill_game()
            definite_kill()
            condition = False
            break
    counter = 0
    while True:
        if locate_png('purchase',0.8) != None:
            item_cord_list = get_items(1,item_list)
            print(item_cord_list)
            if len(item_cord_list) == 5:
                break
            else:
                kill_game()
                definite_kill()
                condition = False
                break
        time.sleep(0.01)
        print(counter,'Find clothes purchase')
        counter+=1
        if counter > 91:
            kill_game()
            definite_kill()
            condition = False
            break
    counter = 0
    while True:
        for item_cord in item_cord_list[:3]:
            x, y = item_cord
            click(x, y)
            for _ in range(5):
                click(x, y, click_button=1, s2=0.2)
                time.sleep(0.3)
        check_and_click('purchase',0.8)
        if_click('block_user',0.7)
        check_and_click('ftconfirm',0.8)
        item_cord = item_cord_list[2]
        x, y = item_cord
        click(x, y, click_button=1, s2=0.2)
        time.sleep(0.3)
        for item_cord in item_cord_list[3:]:
            x, y = item_cord
            for _ in range(5):
                click(x, y, click_button=1, s2=0.2)
                time.sleep(0.3)
        check_and_click('purchase',0.8)
        if_click('block_user',0.7)
        check_and_click('ftconfirm',0.8)
        
        print(counter,'Buy items')
        counter+=1
        if counter > 91:
            kill_game()
            definite_kill()
            condition = False
            break
        break
    try:
        update_json({"time_check": datetime.now().strftime("%m/%d/%Y, %H:%M")})
    except:
        pass
    return condition

def go_merchant_ready(vip_key):
    print('go merchant ready starded')
    condition = True
    key_press('+esc')
    time.sleep(0.1)
    key_press('-x')
    time.sleep(0.1)
    click(60,60)
    time.sleep(0.1)
    dondur = pc_data['merch_ready_dondur_1']
    pau.moveTo(int(w_sizen/2), 60)
    time.sleep(0.1)
    for i in range(pc_data['merch_ready_for_1']):
        drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
        time.sleep(0.1)
        dondur+=pc_data['merch_ready_dondur_1']
    dondur = pc_data['merch_ready_dondur_2']
    counter = 0
    while True:
        if counter < 200:
            pau.moveTo(int(w_sizen/2), 60)
            time.sleep(0.1)
            drag_to(int(w_sizen/2)-dondur, 60,0.3, button='right')
            time.sleep(0.1)
            for i in range(2):
                locate = locate_png('inn_'+str(i),0.7)
                if locate != None:
                    x, y = locate
                    click(x+pc_data['merch_ready_x_1'], y+40)
                    time.sleep(0.3)
                    if vip_key:
                        time.sleep(13)
                    else:
                        time.sleep(5)
                        key_press('-s')
                    break
            if locate != None:
                break
            if counter == 199:
                kill_game()
                definite_kill()
                condition = False
                break
        counter+=1
    return condition

def open_vip_key(item_list, user_name, total_item_count, loop_count):
    loop_count = int(loop_count)
    total_item_count = int(total_item_count)
    print(loop_count,total_item_count,'opened vip key')
    condition = True
    condition = control_dc_cancel()
    key_press('+esc')
    time.sleep(0.1)
    key_press('-x')
    time.sleep(0.1)
    pd.moveTo(60,60)
    time.sleep(0.1)
    while True:
        locate = locate_png('inventory',0.8)
        if locate != None:
            break
        else:
            key_press('-i')
    pd.moveTo(60,60)
    x, y = locate_png('vip_key',0.8)
    click(x, y)
    pd.moveTo(60,60)
    time.sleep(1)
    item_cord_list = get_items(0,item_list)
    print(len(item_cord_list),'Inven item')
    if len(item_cord_list) > 0:
        for item_cord in item_cord_list:
            x, y = item_cord
            click(x, y, click_button=1)
            time.sleep(0.2)
        total_item_count+=len(item_cord_list)
        loop_count+=1
        pn.send_text('{} Tur: {}, {}, toplam {} item bastı.'.format(datetime.now().strftime('%H:%M'), loop_count, user_name, total_item_count),
                        silent=False, devices=[pdevices])
    pd.moveTo(60,60)
    time.sleep(0.2)
    vip_item_cord_list = get_items(4,item_list)
    print(len(vip_item_cord_list),'Vip item')
    return condition, total_item_count, loop_count, len(vip_item_cord_list)

def vip_to_inv(item_list):
    try:
        hwnd = win32gui.FindWindow(None, "Game Client")
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass
    time.sleep(0.3)
    condition = control_dc_cancel()
    key_press('+esc')
    key_press('-x')
    click(60,60)
    time.sleep(0.2)
    while True:
        locate = locate_png('inventory',0.8)
        if locate != None:
            break
        else:
            key_press('-i')
            time.sleep(1)
        time.sleep(0.5)
    pd.moveTo(60,60)
    time.sleep(0.2)
    x, y = locate_png('vip_key',0.8)
    click(x, y, s2=0.2)
    time.sleep(0.3)
    pd.moveTo(60,60)
    time.sleep(1)
    vip_item_cord_list = get_items(4,item_list)
    if len(vip_item_cord_list) > 0:
        for item_cord in vip_item_cord_list[:28]:
            x, y = item_cord
            click(x, y, click_button=1, s2=0.2)
            time.sleep(0.3)
    return condition

def inv_to_vip(item_list):
    try:
        hwnd = win32gui.FindWindow(None, "Game Client")
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass
    time.sleep(0.3)
    condition = control_dc_cancel()
    key_press('+esc')
    key_press('-x')
    click(60,60)
    time.sleep(0.2)
    while True:
        locate = locate_png('inventory',0.8)
        if locate != None:
            break
        else:
            key_press('-i')
            time.sleep(1)
        time.sleep(0.5)
    pd.moveTo(60,60)
    x, y = locate_png('vip_key',0.8)
    click(x, y, s2=0.2)
    time.sleep(0.3)
    pd.moveTo(60,60)
    time.sleep(1)
    item_cord_list = get_items(0,item_list)
    if len(item_cord_list) > 0:
        for item_cord in item_cord_list:
            x, y = item_cord
            click(x, y, click_button=1)
            time.sleep(0.2)
    return condition

def sell_item(item_x, item_y, box_list, counter, price):
    while True:
        click(item_x, item_y)
        x, y = box_list[counter]
        print(x, y)
        drag_to(x, y, 0.1, button='left')
        time.sleep(1)
        locate = locate_png('pazarconfirm',0.9)
        if locate != None:
            key_press('-{}'.format(price))
            time.sleep(2)
            key_press('+space')
            time.sleep(0.5)
            x, y = locate
            click(x, y, s2=0.2)
            time.sleep(0.5)
            pd.moveTo(60,60)
            time.sleep(0.5)
            x, y = locate_png('pazar2confirm',0.9)
            click(x, y, s2=0.2, s3=0.5)
            pd.moveTo(60,60)
            time.sleep(0.5)
            break

def merchant_stop():
    hwnd = win32gui.FindWindow(None, "Game Client")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    click(60,60)
    time.sleep(0.2)
    while True:
        locate = locate_png('inventory',0.8)
        if locate != None:
            break
        else:
            key_press('-i')
            time.sleep(0.5)
    x, y = locate_png('re_arrange',0.8)
    click(x, y, s2=0.2)
    time.sleep(1)
    x, y = locate_png('re_arrange_confirm',0.8)
    click(x, y, s2=0.2)
    time.sleep(0.1)

def merchant_set(item_list,price,user_name,vip_key):
    merchant_stop()
    if vip_key:
        merchant_inv_check_vip(item_list)
    key_press('-h')
    time.sleep(0.5)
    try:
        x, y = locate_png('klan',0.9)
        click(x, y)
        time.sleep(0.5)
        print('clicked')
    except:
        x, y = locate_png('knights',0.9)
        click(x, y)
        time.sleep(0.5)
        print('clicked')
    finally:
        x, y = locate_png('trade1',0.9)
        click(x, y)
        time.sleep(0.5)
        x, y = locate_png('merchant',0.9)
        click(x, y)
        click(x, y)
        click(x, y)
        time.sleep(0.2)
        key_press('+enter')
        time.sleep(0.3)
    while True:
        locate = locate_png('sellm',0.9)
        if locate != None:
            x, y = locate
            click(x, y, s2=0.2,s3=5)
            if locate_png('tsp',0.9) != None:
                break
            else:
                pd.moveTo(60,60)
    time.sleep(2)
    item_cor_lists = get_items(2,item_list)
    item_lenght = sum([len(i) for i in item_cor_lists])
    box_list = []
    for item in pau.locateAllOnScreen('./bdata/boskutu.png',confidence=0.9):
        x, y, w, h = item
        box_list.append((x+int(w/2), y))

    if item_lenght >= 12:
        counter = 0
        for i in range(12):
            temp_item_cor_lists = []
            for item_cor_list in item_cor_lists:
                if counter == 12:
                    break
                if len(item_cor_list) > 0:
                    x, y = item_cor_list[0]
                    sell_item(x, y, box_list, counter, price)
                    item_cor_list.pop(0)
                    temp_item_cor_lists.append(item_cor_list)
                    print(counter)
                    counter+=1
            item_cor_lists = temp_item_cor_lists
        x, y = locate_png('sellconfirm',0.9)
        click(x, y)
    elif 12 > item_lenght > 0:
        counter = 0
        for i in range(item_lenght):
            temp_item_cor_lists = []
            for item_cor_list in item_cor_lists:
                if counter == item_lenght+1:
                    break
                if len(item_cor_list) > 0:
                    x, y = item_cor_list[0]
                    sell_item(x, y, box_list, counter, price)
                    item_cor_list.pop(0)
                    temp_item_cor_lists.append(item_cor_list)
                    print(counter)
                    counter+=1
            item_cor_lists = temp_item_cor_lists
        x, y = locate_png('sellconfirm',0.9)
        click(x, y)
    key_press('-i')
    time.sleep(1)
    if locate_png('inventory',0.9) == None:
        key_press('-i')
    time.sleep(2)
    pn.send_text('{} {}, pazar kuruldu.'.format(datetime.now().strftime('%H:%M'),user_name),
                            silent=False, devices=[pdevices])
    return item_lenght

def save_screenshot():
    window_name = "Game Client"
    hwnd = win32gui.FindWindow(None, window_name)
    
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        im.save("C:/merchant_check_ss.png")

def locate_iother_clothes_on_iother_clothes(img, confidence):
    save_screenshot()
    img_rgb = cv2.imread("C:/merchant_check_ss.png")
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('./bdata/'+img+'.png',0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    loc = np.where( res >= confidence)
    cor_list = []
    for pt in zip(*loc[::-1]):
        cor_list.append(pt)
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
    cv2.imwrite('C:/res.png',img_rgb)
    return cor_list

def merchant_inv_check_vip(item_list):
    control_dc_cancel()
    key_press('+esc')
    key_press('-x')
    pd.moveTo(60,60)
    while True:
        locate = locate_png('inventory',0.8)
        if locate != None:
            break
        else:
            key_press('-i')
            time.sleep(0.5)
    pd.moveTo(60,60)
    item_cord_list = get_items(0,item_list)
    if len(item_cord_list) < 12:
        x, y = locate_png('vip_key',0.8)
        click(x, y, s2=0.2)
        pd.moveTo(60,60)
        time.sleep(1)
        vip_item_cord_list = get_items(4,item_list)
        if len(vip_item_cord_list) > 0:
            for item_cord in vip_item_cord_list[:28]:
                x, y = item_cord
                click(x, y, click_button=1, s2=0.2)
    key_press('+esc')
    time.sleep(0.2)

def merchant_check(item_list, price, user_name,vip_key):
    counter = 1
    main_merchant_con = True
    while main_merchant_con:
        total_item_count = merchant_set(item_list, price, user_name,vip_key)
        no_item = True
        merchant_con = True
        while merchant_con:
            time.sleep(20)
            try:
                item_lenght = len([i for item in item_list[0] for i in locate_iother_clothes_on_iother_clothes(item, 0.99)])
                if item_lenght > 12:
                    item_diff = total_item_count - item_lenght
                    print(total_item_count,item_lenght,item_diff)
                    if item_diff >= 9:
                        pn.send_text('{} {}, {}.parti bitti.'.format(datetime.now().strftime('%H:%M'),user_name,counter),
                                        silent=False, devices=[pdevices])
                        time.sleep(60)
                        merchant_con = False
                elif 12 >= item_lenght > 0:
                    item_diff = total_item_count - item_lenght
                    print(total_item_count,item_lenght,item_diff)
                    if item_diff >= 9:
                        pn.send_text('{} {}, {}.parti bitti.'.format(datetime.now().strftime('%H:%M'),user_name,counter),
                                        silent=False, devices=[pdevices])
                        time.sleep(60)
                        merchant_con = False
                elif item_lenght == 0:
                    pn.send_text('{} {}, pazar item kalmadı.'.format(datetime.now().strftime('%H:%M'),user_name),
                                    silent=False, devices=[pdevices])
                    main_merchant_con = False
                    merchant_con = False
                    no_item = False
            except Exception as e:
                print(e)
                pass
        counter+=1
        if not no_item:
            break
            
def inn_to_inv(item_list):
    time.sleep(2)
    hwnd = win32gui.FindWindow(None, "Game Client")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    click(60,60)
    
    if locate_png('incheck',0.9) != None:
        for i in range(8):
            empty_total = []
            for item in pau.locateAllOnScreen('./bdata/inv_empty_box.png',confidence=0.9):
                x, y, w, h = item
                print(item)
                if x > 970 and y > 386:
                    empty_total.append(item)
            empty_total_count = len(empty_total)
            item_cord_list = get_items(3,item_list)
            print(empty_total_count)
            if empty_total_count > 0:
                for item_cord in item_cord_list[:empty_total_count]:
                    x, y = item_cord
                    click(x, y, click_button=1)
                    time.sleep(0.3)
                    empty_total_count-=1
                pd.moveTo(60,60)
                time.sleep(0.1)
                x, y = locate_png('inn_next',0.9)
                click(x, y, s2=0.2,s3=0.5)
            else:
                print('bitti')
                break

def inv_to_inn(item_list):
    time.sleep(2)
    hwnd = win32gui.FindWindow(None, "Game Client")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    click(60,60)

    if locate_png('incheck',0.9) != None:
        time.sleep(1)
        item_cord_list = get_items(0,item_list)
        if len(item_cord_list) == 0:
            time.sleep(1)
            while True:
                empty_total = []
                for item in pau.locateAllOnScreen('./bdata/inv_empty_box.png',confidence=0.9):
                    x, y, w, h = item
                    print(item)
                    if x > 970 and y > 386:
                        empty_total.append(item)
                empty_total_count = len(empty_total)
                item_cord_list = get_items(3,item_list)
                print(empty_total_count)
                if empty_total_count > 0:
                    for item_cord in item_cord_list[:empty_total_count]:
                        x, y = item_cord
                        click(x, y, click_button=1)
                        time.sleep(0.3)
                        empty_total_count-=1
                    pd.moveTo(60,60)
                    time.sleep(0.1)
                    x, y = locate_png('inn_next',0.9)
                    click(x, y, s2=0.2,s3=0.5)
                else:
                    print('bitti')
                    break
        else:
            while True:
                empty_total = []
                for item in pau.locateAllOnScreen('./bdata/inn_empty_box.png',confidence=0.9):
                    x, y, w, h = item
                    if x > 970 and y < 386:
                        empty_total.append((x+int(w/2), y+int(h/2)))
                empty_total_count = len(empty_total)
                if empty_total_count == 24:
                    break
                else:
                    x, y = locate_png('inn_next',0.9)
                    click(x, y, s2=0.2,s3=0.5)
            
            if len(item_cord_list) <=24:
                for item_cord in item_cord_list[:empty_total_count]:
                    x, y = item_cord
                    click(x, y, click_button=1, s2=0.2, s3=0.3)
            else:
                for item_cord in item_cord_list[empty_total_count:]:
                    x, y = item_cord
                    click(x, y, click_button=1, s2=0.2, s3=0.3)
                x, y = locate_png('inn_next',0.9)
                click(x, y, s2=0.2,s3=0.5)

def relocate_scroll(user_name):
    key_press('+esc')
    key_press('-x')
    key_press('-i')
    time.sleep(0.5)
    counter = 0
    while True:
        locate = locate_png('uscroll',0.8)
        if locate != None:
            x, y = locate
            if x > 1265 and y > 565:
                u_x = x
                u_y = y
                break
            else:
                pd.moveTo(x, y)
                time.sleep(0.1)
                drag_to(1310, 610, 0.8, button='left')
                pd.moveTo(60,60)
                u_x , u_y = locate_png('uscroll',0.8)
                break
        counter+=1
        time.sleep(0.01)
        if counter > 60:
            pn.send_text('{} {}, scroll yerine koyulamadı!'.format(datetime.now().strftime('%H:%M'),user_name),
                                        silent=False, devices=[pdevices])
            kill_game()
            definite_kill()
            break
    return u_x, u_y

def update_time():
    server_list = ['time.nist.gov', 'time.windows.com', 'pool.ntp.org']

    def gettime_ntp(addr='time.nist.gov'):
        TIME1970 = 2208988800
        client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        data = bytes('\x1b' + 47 * '\0','utf-8')
        try:
            client.settimeout(5.0)
            client.sendto( data, (addr, 123))
            data, address = client.recvfrom( 1024 )
            if data:
                epoch_time = struct.unpack( '!12I', data )[10]
                epoch_time -= TIME1970
                return epoch_time
        except socket.timeout:
            return None
        
    for server in server_list:
        epoch_time = gettime_ntp(server)
        if epoch_time is not None:
            utcTime = datetime.utcfromtimestamp(epoch_time)
            win32api.SetSystemTime(utcTime.year, utcTime.month, utcTime.weekday(), utcTime.day, utcTime.hour, utcTime.minute, utcTime.second, 0)
            localTime = datetime.fromtimestamp(epoch_time)
            print("Time updated to: " + localTime.strftime("%Y-%m-%d %H:%M") + " from " + server)
            break
        else:
            print("Could not find time from " + server)
                    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainUi()
    if pd.size() == (1920,1080):
        window.move(1568, 0)
    sys.exit(app.exec_())


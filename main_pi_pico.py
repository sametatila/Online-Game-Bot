import sys
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse


keyboard_dict = {
    '0': Keycode.ZERO, '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE, '4': Keycode.FOUR, 
    '5': Keycode.FIVE, '6': Keycode.SIX, '7': Keycode.SEVEN, '8': Keycode.EIGHT, '9': Keycode.NINE, 
    'a': Keycode.A, 'b': Keycode.B, 'c': Keycode.C, 'd': Keycode.D, 'e': Keycode.E, 
    'f': Keycode.F, 'g': Keycode.G, 'h': Keycode.H, 'i': Keycode.I, 'j': Keycode.J, 'k': Keycode.K, 'l': Keycode.L, 
    'm': Keycode.M, 'n': Keycode.N, 'o': Keycode.O, 'p': Keycode.P, 'q': Keycode.Q, 'r': Keycode.R, 's': Keycode.S, 
    't': Keycode.T, 'u': Keycode.U, 'v': Keycode.V, 'w': Keycode.W, 'x': Keycode.X, 'y': Keycode.Y, 'z': Keycode.Z
    }

keyboard_dict_special = {
    'tab': Keycode.TAB,
    'space': Keycode.SPACE, 
    'enter': Keycode.ENTER, 
    'esc': Keycode.ESCAPE, 
    'delete': Keycode.DELETE, 
    'backspace': Keycode.BACKSPACE, 
    'home': Keycode.HOME, 
    'end': Keycode.END, 
    'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3, 'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 
    'F7': Keycode.F7, 'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11, 'F12': Keycode.F12
    }



keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

def key_press(word):
    try:
        for i in word:
            keyboard.press(keyboard_dict[i])
            time.sleep(0.1)
            keyboard.release(keyboard_dict[i])
    except:
        pass

def key_press_special(word):
    try:
        keyboard.press(keyboard_dict_special[word])
        time.sleep(0.1)
        keyboard.release(keyboard_dict_special[word])
    except:
        pass

def key_press_desk(key):
    keyboard.press(keyboard_dict[key])

def key_realese_desk(key):
    keyboard.release(keyboard_dict[key])

def click_left(ts):
    ts = ts.split(',')
    s1, s2, s3 = ts
    time.sleep(float(s1))
    mouse.press(Mouse.LEFT_BUTTON)	
    time.sleep(float(s2))
    mouse.release(Mouse.LEFT_BUTTON)
    time.sleep(float(s3))

def click_right(ts):
    ts = ts.split(',')
    s1, s2, s3 = ts
    time.sleep(float(s1))
    mouse.press(Mouse.RIGHT_BUTTON)	
    time.sleep(float(s2))
    mouse.release(Mouse.RIGHT_BUTTON)
    time.sleep(float(s3))

def left_drag_to_press():
    mouse.press(Mouse.LEFT_BUTTON)
    
def left_drag_to_release():
    mouse.release(Mouse.LEFT_BUTTON)

def right_drag_to_press():
    mouse.press(Mouse.RIGHT_BUTTON)
    
def right_drag_to_release():
    mouse.release(Mouse.RIGHT_BUTTON)
        

    
while True:
    v = sys.stdin.readline().strip()
    if v.startswith('+'):
        key_press_special(v[1:])
    elif v.startswith('-'):
        key_press(v[1:])
    elif v.startswith("lc"):
        click_left(v[2:])
    elif v.startswith("rc"):
        click_right(v[2:])
    elif v == 'ld1':
        left_drag_to_press()
    elif v == 'ld2':
        left_drag_to_release()
    elif v == 'rd1':
        right_drag_to_press()
    elif v == 'rd2':
        right_drag_to_release()
    elif v.startswith('?'):
        key_press_desk(v[1:])
    elif v.startswith('*'):
        key_realese_desk(v[1:])
    time.sleep(0.5)
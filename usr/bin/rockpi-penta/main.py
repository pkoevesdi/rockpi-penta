#!/usr/bin/env python3
import sys
import fan
import misc
try:
    import oled
    top_board = 1
except Exception as ex:
    top_board = 0

import multiprocessing as mp

q = mp.Queue()
lock = mp.Lock()

action = {
    'none': lambda: 'nothing',
    'slider': lambda: oled.slider(lock),
    'switch': lambda: misc.fan_switch(),
    'reboot': lambda: misc.check_call('reboot'),
    'poweroff': lambda: misc.check_call('poweroff'),
}


def receive_key(q):
    while True:
        func = misc.get_func(q.get())
        action[func]()


def main():
    if sys.argv[-1] == 'on':
        if '4c+' in misc.check_output('cat /proc/device-tree/model').lower():
            misc.check_call('echo host > /sys/devices/platform/usb0/dwc3_mode')
        if top_board:
            oled.welcome()
        misc.disk_turn_on()
    elif sys.argv[-1] == 'off':
        if top_board:
            fan.turn_off()
            oled.goodbye()
        misc.disk_turn_off()
        exit(0)


if __name__ == '__main__':
    main()

    if top_board:
        p0 = mp.Process(target=receive_key, args=(q,))
        p1 = mp.Process(target=misc.watch_key, args=(q,))
        p2 = mp.Process(target=oled.auto_slider, args=(lock,))
        p3 = mp.Process(target=fan.running)

        p0.start()
        p1.start()
        p2.start()
        p3.start()
        p3.join()
    else:
        p3 = mp.Process(target=fan.running)
        p3.start()
        p3.join()

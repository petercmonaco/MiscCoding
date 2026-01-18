# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from driving import driving_stop, handle_driving_cmd, loop_driving, loop_replan, upover_to_xy
from imu import current_heading, is_parked_flat
from lidar import loop_read_lidar, get_distances
from asyncio import create_task, gather, run
from asyncio import sleep as async_sleep
from display import display_cmd, display_battery, display_distances, display_heading, display_xy
from servos import loop_point_lidar, handle_servo_cmd
import board
import alarm
import adafruit_max1704x
from wifi_and_comms import set_command_handler, handle_http_requests, handle_websocket_requests, send_message, wlog

# Battery monitor
bm = adafruit_max1704x.MAX17048(board.I2C())


def execute_cmd(cmd):
    display_cmd(cmd)
    if cmd == 'sleep':
        driving_stop()
        alarm.exit_and_deep_sleep_until_alarms(alarm.pin.PinAlarm(pin=board.D0, value=False))
    elif cmd == 'ping':
        send_message("Pong")
    elif cmd == 'status':
        send_message(f"Battery: {bm.cell_percent:.1f}%")
    elif cmd == 'pos':
        resp = "Parked flat. " if is_parked_flat() else f"Hdg: {current_heading():.1f}. "
        [d1, d2] = get_distances()
        resp += f" {d1}mm up, {d2}mm over"
        send_message(resp)
    elif cmd == 'collect_lidar':
        pass
        #(dvals1, dvals2) = collect_timings()
        #send_message(f"Up: Collected {len(dvals1)} distance readings")
        #send_message(",".join([str(d) for d in dvals1]))
        #send_message(f"Over: Collected {len(dvals2)} distance readings")
        #send_message(",".join([str(d) for d in dvals2]))
    else:
        for cmd_handler in [handle_driving_cmd, handle_servo_cmd]:
            (is_for_me, msg) = cmd_handler(cmd)
            if is_for_me:
                if msg:
                    send_message(msg)
                return
        send_message("Unknown command: " + cmd)

set_command_handler(execute_cmd)

async def loop_update_display():
    while True:
        await async_sleep(1)
        display_battery(f"{bm.cell_percent:.1f}")
        display_heading(f"{current_heading():.1f}")
        d = get_distances()
        display_distances(d)
        xy = upover_to_xy(d[0], d[1])
        display_xy(xy)
        wlog("hello")

async def main():
    await gather(
        create_task(handle_http_requests()),
        create_task(handle_websocket_requests()),
        create_task(loop_update_display()), # 1x
        create_task(loop_driving()), # 100x
        create_task(loop_point_lidar()), # 10x
        create_task(loop_read_lidar()), # 50x, but new data 10x
        create_task(loop_replan()) # 1x
    )


run(main())

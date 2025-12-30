import time
import board
import adafruit_vl53l1x
import digitalio
from asyncio import sleep as async_sleep

#i2c = board.I2C()  # uses board.SCL and board.SDA
i2c_stemma = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

xshut = [
    digitalio.DigitalInOut(board.D6),
    digitalio.DigitalInOut(board.D5),
]

for shutdown_pin in xshut:
    # Set the shutdown pins to output, and pull them low, shutting down the sensor.
    shutdown_pin.switch_to_output(value=False)
# All VL53L1X sensors are now off.


sensors = []
# Change the address of the additional VL53L1X sensors.
for pin_number, shutdown_pin in enumerate(xshut):
    # Turn on one VL53L1X sensor
    shutdown_pin.value = True
    # Instantiate the VL53L1X I2C object and insert it into the list.
    # This also performs VL53L1X hardware check.
    sensor = adafruit_vl53l1x.VL53L1X(i2c_stemma)
    sensors.append(sensor)
    # This ensures no address change on one sensor board, specifically the last one in the series.
    if pin_number < len(xshut) - 1:
        # The default address is 0x29. Update it to an address that is not already in use.
        sensor.set_address(pin_number + 0x30)

# Print the various sensor I2C addresses to the serial console.
#if i2c_stemma.try_lock():
#    print("Sensor I2C addresses:", [hex(x) for x in i2c_stemma.scan()])
#    i2c_stemma.unlock()

for s in sensors:
    s.distance_mode = 2 # 1: SHORT, 2: LONG
    s.timing_budget = 100 # in ms
    s.start_ranging()
    # Optional: Retrieve the sensor's model ID, module type, and mask revision
    #model_id, module_type, mask_rev = s.model_info

last_dist = [None] * len(sensors)

"""def collect_timings():
    global sensors
    dvals1 = []
    dvals2 = []
    start_time = time.monotonic()
    while True:
        if sensors[0].data_ready :
            dvals1.append(sensors[0].distance)
            sensors[0].clear_interrupt()
        if sensors[1].data_ready :
            dvals2.append(sensors[1].distance)
            sensors[1].clear_interrupt()
        time.sleep(0.001)
        if time.monotonic() - start_time > 5.0:
            break

    return (dvals1, dvals2)"""

async def loop_read_lidar():
    global sensors, last_dist
    while True:
        for i, s in enumerate(sensors): 
            if s.data_ready :
                reading = s.distance
                d = reading if reading is not None else 555.5 # If the distance is too great, sensor returns None
                last_dist[i] = int(d * 10)  # convert to mm
                s.clear_interrupt()
        await async_sleep(0.02) # 20 ms between readings


def get_distances():
    global last_dist
    return last_dist

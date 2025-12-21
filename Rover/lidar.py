import board
import adafruit_vl53l1x

#i2c = board.I2C()  # uses board.SCL and board.SDA
i2c_stemma = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
vl53 = adafruit_vl53l1x.VL53L1X(i2c_stemma)

# OPTIONAL: can set non-default values
vl53.distance_mode = 2 # 1: SHORT, 2: LONG
vl53.timing_budget = 100 # in ms

# Retrieve the sensor's model ID, module type, and mask revision
#model_id, module_type, mask_rev = vl53.model_info

vl53.start_ranging()

latest_distance = None

def get_distance():
    if vl53.data_ready:
        latest_distance = (vl53.distance or 0) * 10 # Convert cm to mm
        vl53.clear_interrupt()
    
    return latest_distance

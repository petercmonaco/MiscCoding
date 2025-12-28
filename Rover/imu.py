import math
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL

i2c = board.I2C()  # uses board.SCL and board.SDA
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

def print_all_imu():
    acceleration = accel_gyro.acceleration
    gyro = accel_gyro.gyro
    magnetic = mag.magnetic
    print("Acceleration: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2".format(*acceleration))
    print("Gyro          X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} rad/s".format(*gyro))
    print("Magnetic      X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} uT".format(*magnetic))

def current_heading():
    x, y, _ = accel_gyro.acceleration
    hdg = math.degrees(math.atan2(-x,-y))
    if hdg < 0:
        hdg += 360
    return hdg

def is_parked_flat():
    x, y, z = accel_gyro.acceleration
    return abs(z) > abs(x) and abs(z) > abs(y)

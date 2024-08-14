import machine
import struct
import time
import dht
from umqtt.robust import MQTTClient
from umqtt.simple import MQTTClient
import keys

# Initialize DHT22 sensor on GPIO 14 (Pin 19)
dht_sensor = dht.DHT22(machine.Pin(14))

# I2C setup (SCL: GP9, SDA: GP8)
i2c = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8), freq=10000)

# MCU-81 I2C address and registers (keep these as before)
ccs811_address = 0x5A
status_register = 0x00
data_register = 0x02
env_data_register = 0x05
error_id_register = 0xE0

# Adafruit IO MQTT setup
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_CLIENT_ID = "pico"
AIO_FEED_TEMP = keys.AIO_USER + "/feeds/dht22.temperature"
AIO_FEED_HUM = keys.AIO_USER + "/feeds/dht22.humidity"

# Connect to Adafruit IO using MQTT
def connect_mqtt():
    client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, port=AIO_PORT, user=keys.AIO_USER, password=keys.AIO_KEY)
    try:
        client.connect()
        print("Connected to Adafruit IO!")
    except Exception as e:
        print(f"Failed to connect to Adafruit IO: {e}")
        return None
    return client

# Functions for MCU-81 (keep these as they are)

def reset_sensor():
    try:
        reset_sequence = bytes([0x11, 0xE5, 0x72, 0x8A])
        i2c.writeto_mem(ccs811_address, 0xFF, reset_sequence)
        print("Sensor reset")
    except Exception as e:
        print(f"Failed to reset sensor: {e}")

def set_measurement_mode(mode):
    try:
        i2c.writeto_mem(ccs811_address, 0x01, bytes([mode]))
        print(f"Measurement mode set to {mode}")
    except Exception as e:
        print(f"Failed to set measurement mode: {e}")

def write_env_data_to_mcu81(temperature, humidity):
    try:
        temp = int((temperature + 25) * 512)  # Temperature in 1/512 degrees Celsius
        hum = int(humidity * 512)             # Humidity in 1/512 percent

        env_data = struct.pack('>HH', hum, temp)

        i2c.writeto_mem(ccs811_address, env_data_register, env_data)
        print(f"Updated ENV_DATA with Temp: {temperature}°C, Humidity: {humidity}%")
    except Exception as e:
        print(f"Failed to write environmental data to MCU-81: {e}")

def read_air_quality_from_mcu81():
    try:
        if not data_available():
            print("No new data available.")
            return None, None

        i2c_data = i2c.readfrom_mem(ccs811_address, data_register, 4)
        print(f"Raw I2C data: {i2c_data}")

        eCO2 = struct.unpack('>H', i2c_data[0:2])[0]
        eTVOC = struct.unpack('>H', i2c_data[2:4])[0]

        print(f"MCU-81 eCO2: {eCO2} ppm")
        print(f"MCU-81 eTVOC: {eTVOC} ppb")

        return eCO2, eTVOC
    except Exception as e:
        print(f"Failed to read air quality data from MCU-81: {e}")
        return None, None

def data_available():
    try:
        status = i2c.readfrom_mem(ccs811_address, status_register, 1)[0]
        return status & 0x08
    except Exception as e:
        print(f"Failed to check data availability: {e}")
        return False

def check_sensor_status():
    try:
        status = i2c.readfrom_mem(ccs811_address, status_register, 1)[0]
        error_id = i2c.readfrom_mem(ccs811_address, error_id_register, 1)[0]
        print(f"STATUS: {bin(status)}")
        print(f"ERROR_ID: 0x{error_id:X}")
    except Exception as e:
        print(f"Failed to read STATUS or ERROR_ID: {e}")

# Main function to read DHT22 and publish to Adafruit IO
def main():
    client = connect_mqtt()
    if client is None:
        return  # Exit if the connection failed
    
    # Initialize the sensor (reset and set measurement mode)
    reset_sensor()
    time.sleep(2)
    set_measurement_mode(0x10)

    start_time = time.time()

    # Main loop to read DHT22 and calibrate MCU-81 over time
    while True:
        try:
            dht_sensor.measure()
            temperature = dht_sensor.temperature()  # In Celsius
            humidity = dht_sensor.humidity()        # In Percentage

            print(f"DHT22 Temperature: {temperature}°C")
            print(f"DHT22 Humidity: {humidity}%")

            # Publish to Adafruit IO
            client.publish(AIO_FEED_TEMP, str(temperature))
            client.publish(AIO_FEED_HUM, str(humidity))

            # Write environmental data to MCU-81 (for calibration)
            write_env_data_to_mcu81(temperature, humidity)

            # Read air quality data from MCU-81
            eCO2, eTVOC = read_air_quality_from_mcu81()

            # Check sensor status
            check_sensor_status()

            # Delay for stabilization
            time.sleep(10)

            # Check if 20 minutes have passed
            elapsed_time = time.time() - start_time
            if elapsed_time > 86400:  # 24h in seconds
                print("Conditioning period complete, checking for stable readings.")
                break

        except OSError as e:
            print("OSError: Failed to read sensor:", e)
        except Exception as e:
            print("Exception: An unexpected error occurred:", e)

        time.sleep(2)

if __name__ == "__main__":
    main()

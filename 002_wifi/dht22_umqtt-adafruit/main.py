import machine
from time import sleep
import dht
from umqtt.simple import MQTTClient  # Make sure this is correctly imported
import keys

# Initialize DHT22 sensor on GPIO 14 (Pin 19)
dht_sensor = dht.DHT22(machine.Pin(14))

# Adafruit IO MQTT setup
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_CLIENT_ID = "pico"

# Define MQTT feeds
AIO_FEED_TEMP = keys.AIO_USER + "/feeds/dht22.temperature"
AIO_FEED_HUM = keys.AIO_USER + "/feeds/dht22.humidity"

# Function to connect to Adafruit IO via MQTT
def connect_mqtt():
    client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, port=AIO_PORT, user=keys.AIO_USER, password=keys.AIO_KEY)
    try:
        client.connect()
        print("Connected to Adafruit IO!")
    except Exception as e:
        print("Failed to connect to Adafruit IO:", e)
        return None
    return client

# Function to publish sensor data to Adafruit IO
def publish_sensor_data(client, temperature, humidity):
    try:
        client.publish(AIO_FEED_TEMP, str(temperature))
        client.publish(AIO_FEED_HUM, str(humidity))
        print("Published to Adafruit IO")
    except Exception as e:
        print("Failed to publish to Adafruit IO:", e)

# Main function
def main():
    client = connect_mqtt()  # Connect to MQTT
    if client is None:
        return  # Exit if the connection failed
    
    while True:
        try:
            # Trigger a measurement
            dht_sensor.measure()
            
            # Read temperature and humidity
            temperature = dht_sensor.temperature()  # In Celsius
            humidity = dht_sensor.humidity()        # In Percentage
            
            # Print the readings
            print("Temperature: {}°C".format(temperature))
            print("Humidity: {}%".format(humidity))
            
            # Publish the sensor data to Adafruit IO
            publish_sensor_data(client, temperature, humidity)
            
        except OSError as e:
            print("Failed to read sensor:", e)
        
        # Wait for 10 seconds before next reading
        sleep(10)

if __name__ == "__main__":
    main()

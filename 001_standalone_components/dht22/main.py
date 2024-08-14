import machine
from time import sleep
import dht

# Initialize DHT11 sensor on GPIO 14 (Pin 19)
dht_sensor = dht.DHT22(machine.Pin(14))

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
        
    except OSError as e:
        print("Failed to read sensor:", e)
    
    # Wait for 2 seconds before next reading
    sleep(1)

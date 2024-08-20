import machine
import dht
import time

# Initialize DHT22 sensor on GPIO 14 (Pin 19)
dht_sensor = dht.DHT22(machine.Pin(14))

def test_dht22():
    try:
        # Measure temperature and humidity
        dht_sensor.measure()
        temperature = dht_sensor.temperature()  # In Celsius
        humidity = dht_sensor.humidity()        # In Percentage

        # Print the values
        print(f"DHT22 Temperature: {temperature}°C")
        print(f"DHT22 Humidity: {humidity}%")
    except Exception as e:
        print(f"Failed to read from DHT22 sensor: {e}")

def main():
    while True:
        test_dht22()  # Read and print DHT22 data
        time.sleep(10)  # Delay between readings

if __name__ == "__main__":
    main()

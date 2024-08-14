import sys
sys.path.append('lib')  # Lägg till lib-mappen i sys.path

try:
    import keys
    print("keys module loaded successfully")
except ImportError as e:
    print("Failed to load keys module:", e)

import keys  # Importera keys från lib-mappen
import network
from time import sleep

def connect():
    wlan = network.WLAN(network.STA_IF)  # Put modem on Station mode
    if not wlan.isconnected():           # Check if already connected
        print('connecting to network...')
        wlan.active(True)                # Activate network interface
        # set power mode to get WiFi power-saving off (if needed)
        wlan.config(pm=0xa11140)
        wlan.connect(keys.WIFI_SSID, keys.WIFI_PASS)  # Your WiFi Credential
        print('Waiting for connection...', end='')
        # Check if it is connected otherwise wait
        while not wlan.isconnected():
            print('.', end='')
            sleep(1)
    # Print the IP assigned by router
    ip = wlan.ifconfig()[0]
    print('\nConnected on {}'.format(ip))
    return ip

def http_get(url='http://detectportal.firefox.com/'):
    import socket
    import time
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.settimeout(10)  # Set a timeout for the connection
    try:
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
        time.sleep(1)
        rec_bytes = s.recv(10000)
        print(rec_bytes.decode('utf-8'))  # Decode bytes to string
    except Exception as e:
        print("Error during HTTP GET:", e)
    finally:
        s.close()

# WiFi Connection
try:
    ip = connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# HTTP request
try:
    http_get()
except Exception as err:
    print("No Internet", err)

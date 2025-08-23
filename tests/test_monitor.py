from monitor_ws2000 import WS2000Monitor

def test_monitor():
    ws2000 = WS2000Monitor()
    wind_data = ws2000.get_latest_reading()
    print(wind_data)

if __name__ == "__main__":
    test_monitor()

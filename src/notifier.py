# -*- coding: utf-8 -*-
"""Send notifications to a webhook in MicroPython.

Send a POST request to a webhook URL endpoint. Intended for use with an IFTTT
webhook, but reasonably could be used for any webhook.
"""

import network
import sys
import urequests
import json
import time
import machine

led = machine.Pin("LED", machine.Pin.OUT)


class Notifier:
    client = None

    def __init__(self):
        with open("data.json", "r") as df:
            self.data = json.load(df)

    @property
    def ssid(self):
        return self.data["SSID"]

    @property
    def password(self):
        return self.data["PASSWORD"]

    @property
    def url(self):
        return self.data["URL"]

    def connect(self):
        print("Connecting to", self.ssid)
        self.client = network.WLAN(network.STA_IF)
        self.client.active(True)
        self.client.connect(self.ssid, self.password)

        for _ in range(10):
            led.toggle()
            if self.client.isconnected():
                print("Connected to Wi-Fi")
                print("IP Address:", self.client.ifconfig()[0])
                led.off()
                break
            time.sleep(1)
        else:
            print("Failed to connect to Wi-Fi")
            sys.exit(1)

    def disconnect(self):
        self.client.disconnect()
        self.client.active(False)
        print("Disconnected Wi-Fi")

    def blink_forever(self, rate=1):
        while True:
            led.toggle()
            time.sleep(1 / rate)

    def post_data(self, data):
        json_data = json.dumps(data)
        try:
            response = urequests.post(
                self.url, data=json_data, headers={"Content-Type": "application/json"}
            )
            print("Response:", response.text)
            print("Return Code:", response.status_code)
            if response.status_code != 200:
                self.blink_forever(5)
            response.close()
        except Exception as e:
            print("Failed to send POST request:", e)

    @classmethod
    def send(cls, data):
        notifier = cls()
        notifier.connect()
        notifier.post_data(data=data)
        notifier.disconnect()


if __name__ == "__main__":
    data = {"value1": "started"}
    Notifier.send(data=data)


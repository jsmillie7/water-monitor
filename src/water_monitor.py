# -*- coding: utf-8 -*-
"""Monitor running water in a pipe using micropython

Get a rolling RMS value from an analog microphone to
determine acoustically if water is running through a
nearby pipe.
"""

import machine
from collections import deque

from notifier import Notifier

led = machine.Pin("LED", machine.Pin.OUT)
adc = machine.ADC(28)

MID_POINT = 32768

notifier = Notifier()
notifier.connect()


class Monitor:
    def __init__(self, samples=100, threshold=5000, post_data=False) -> None:
        """Acoustically monitor an environment by determining when the
        root-mean-square of the amplitude exceeds a threshold.

        :param samples: The size of the RMS history
        :param threshold: The minimum RMS value that triggers an event
        :param post_data: Send data to webhook on event
        """
        led.off()
        self.history = deque([], samples)
        self.size = samples
        self.threshold = threshold
        self.offset = 0

        self.water_running = False
        self.post_data = post_data

    def __del__(self):
        notifier.disconnect()

    def rolling_rms(self):
        """Calculate a new the new RMS"""
        self.history.append((adc.read_u16() - MID_POINT) ** 2)
        return (sum(self.history) / self.size) ** 0.5

    def calculate_offset(self):
        """Run at startup, ideally when there is no other noise, to calculate
        and offset microphone noise.
        """
        self.offset = (sum(self.history) / self.size) ** 0.5
        print("Calculated Offset = ", self.offset)

    def send(self, value):
        """Conditionally send an update via HTTP post requst"""
        if self.post_data:
            notifier.post_data({"value1": value})

    def run_forever(self):
        """Preload the history then run the monitor until interrupted."""
        i = 0
        # Preloading the rolling rms data allows the rms values to level
        # out prior to starting the monitor.
        print("Starting preload")
        while i < 3 * self.size:
            self.rolling_rms()
            i += 1
        print("Calibrating...")
        self.calculate_offset()
        self.water_running = False
        led.off()

        while True:
            # While we are updating the rolling RMS continually, we don't need
            # every single data point, so only calculate every 100th point
            if i % 100 == 0:
                x = self.rolling_rms() - self.offset
                if x > self.threshold and not self.water_running:
                    led.on()
                    print("[ON]", x)
                    self.water_running = True
                    self.send("started")
                elif x < self.threshold * 0.5 and self.water_running:
                    led.off()
                    print("[OFF]", x)
                    self.water_running = False
                    self.send("finished")
            else:
                self.rolling_rms()
            i += 1


if __name__ == "__main__":
    monitor = Monitor(samples=250, threshold=800)
    monitor.run_forever()

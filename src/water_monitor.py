# -*- coding: utf-8 -*-
"""Monitor running water in a pipe using micropython

Get a rolling RMS value from an analog microphone to
determine acoustically if water is running through a
nearby pipe.
"""
import utime
import math
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

        Args:
            samples (int): The size of the RMS history
            threshold (int): The minimum RMS value that triggers an event
            post_data (bool): Send data to webhook on event
        """
        led.off()
        self.history = deque([], samples)
        self.size = samples
        self.threshold = threshold
        self.rms_offset = 0
        self.delay_offset = 20
        self.calibrated = False

        self.water_running = False
        self.post_data = post_data

    def __del__(self):
        notifier.disconnect()

    def rms(self):
        """sample the audio for 1s and return the rms value of it"""
        delay = int(1e6 // self.size) - self.delay_offset
        start = utime.ticks_ms()

        for _ in range(self.size):
            self.history.append(adc.read_u16())
            utime.sleep_us(delay)

        if self.calibrated:
            return self.calc_rms()

        # while calibrating, change the delay offset to change
        # the total duration of sample collection to get within
        # 1% of 1 second
        dur = utime.ticks_ms() - start
        if dur > 1010:
            self.delay_offset += 1
        elif dur < 990:
            self.delay_offset -= 1
        else:
            self.calibrated = True
            print("Took", dur, "| Calibrated delay offset:", self.delay_offset)
            return

        print("Took", dur, "| New delay offset:", self.delay_offset)

    def calc_rms(self):
        """Calculate the RMS of the history deque"""
        total_square = sum((x - 32768) ** 2 for x in self.history)
        rms = math.sqrt(total_square / self.size)
        return rms

    def send(self, value):
        """Conditionally send an update via HTTP post requst"""
        if self.post_data:
            notifier.post_data({"value1": value})

    def run_forever(self):
        """Preload the history then run the monitor until interrupted."""
        print("Ensure environment is silent...")
        print("Calibrating delay offset...")
        while not self.calibrated:
            led.toggle()
            self.rms()
        self.rms_offset = self.calc_rms()
        print("Offset =", self.rms_offset)
        self.water_running = False
        led.off()

        while True:
            x = self.rms() - self.rms_offset
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
                print(x)

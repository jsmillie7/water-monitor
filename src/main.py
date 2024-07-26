# -*- coding: utf-8 -*-
"""Water Monitor main

Main script for running the water monitor by default
on a micropython board.
"""
from water_monitor import Monitor


def main():
    monitor = Monitor(samples=250, threshold=800, post_data=True)
    monitor.run_forever()


if __name__ == "__main__":
    main()

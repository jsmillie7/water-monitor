# -*- coding: utf-8 -*-
"""Water Monitor main

Main script for running the water monitor by default
on a micropython board.
"""
from water_monitor import Monitor


def main():
    monitor = Monitor(samples=10000, threshold=50, post_data=True)
    monitor.run_forever()


if __name__ == "__main__":
    main()

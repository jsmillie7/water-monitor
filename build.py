#!/usr/bin/env python3
"""Upload the files to the board"""
import json
import subprocess
from pathlib import Path

import serial.tools.list_ports as ports

JSON_DATA_FILE = Path(__file__).parent / "data.json"


def create_data_json():
    """Generate the data file used by micropython"""
    print("Creating the board data.json file.")
    ssid = input("Network SSID: ").strip()
    pw = input("Network Password: ").strip()

    all_coms = [x.device for x in ports.comports()]
    for idx, com in enumerate(all_coms):
        print(f"[{idx}] {com}")
    com_int = input("Select index of COM port: ").strip()
    com = all_coms[int(com_int)]

    url = input("Endpoint URL: ").strip()

    data = {"SSID": ssid, "PASSWORD": pw, "COM": com, "URL": url}
    JSON_DATA_FILE.write_text(json.dumps(data, indent=4))
    print(f"Wrote {JSON_DATA_FILE}")


def ampy_cmd(subcommand, cwd=None):
    """Run an ampy from the command line"""
    com_port = json.loads(JSON_DATA_FILE.read_text())["COM"]
    cmd = ["ampy", "--port", com_port, *subcommand]
    subprocess.run(cmd, cwd=cwd)


def put_file_cmd(file: Path):
    """Put a file on the micropython board"""
    subcmd = ["put", file.name]
    ampy_cmd(subcmd, cwd=file.parent)
    print(f"PUT {file}")


def reset_cmd():
    """Send soft reset command to ampy"""
    ampy_cmd(["reset"])


def main():
    print("Loading project to micropython board")
    if not JSON_DATA_FILE.exists():
        create_data_json()

    src = Path(__file__).parent / "src"
    files = [JSON_DATA_FILE, *src.glob("*.py")]

    for file in files:
        put_file_cmd(file)

    reset_cmd()
    print("Finished Uploading...")


if __name__ == "__main__":
    main()

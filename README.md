# Wi-Fi Password Extractor (Windows)

A Python script that recovers the plaintext passwords of Wi-Fi networks
saved on a Windows machine and appends them to `Wi-Fi-Password.txt` on the
current user's Desktop. It can also be packaged into a single executable
with PyInstaller.

## Overview

The script:

1. Runs `netsh wlan show profiles` to list every Wi-Fi network the machine
   has previously connected to.
2. For each profile, runs `netsh wlan show profile name="<SSID>" key=clear`
   to reveal the stored key.
3. Appends the network name and password to `Wi-Fi-Password.txt` on the
   user's Desktop.

Each run is timestamped, and duplicate (network, password) pairs already
present in the file are skipped by default.

## Disclaimer

This tool is intended for recovering passwords on machines you own or have
explicit written permission to access. Reading Wi-Fi credentials from a
device without authorization is illegal in most jurisdictions. The authors
assume no liability for misuse.

## Requirements

- Windows 10 or Windows 11
- Python 3.8 or newer
- Administrator privileges (recommended; required on some systems to
  reveal the `Key Content` field)

Python packages (only needed for building the executable or develope this version for your self)

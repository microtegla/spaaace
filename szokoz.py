#!/usr/bin/env python3
""

import asyncio
import shutil
import subprocess
import sys
from pathlib import Path

from evdev import InputDevice, ecodes, list_devices
# spacebar sound, must be palceholder.waw / Szőközhang, placeholder.wav-nak kell hogy legyen
WAV = Path(__file__).resolve().with_name("placeholder.wav")

# players of audio / Hanglejátszók
PLAYERS = ["pw-play", "paplay", "aplay"]


def find_player():
    for name in PLAYERS:
        path = shutil.which(name)
        if path:
            return path
    sys.exit("Pájpvájör hol?")


PLAYER = find_player()


def play():
    subprocess.Popen(
        [PLAYER, str(WAV)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def find_keyboards():
    keyboards = []
    for path in list_devices():
        try:
            dev = InputDevice(path)
        except OSError:
            continue
        keys = dev.capabilities().get(ecodes.EV_KEY, [])
        if ecodes.KEY_SPACE in keys:
            keyboards.append(dev)
    return keyboards


async def watch(dev):
    try:
        async for event in dev.async_read_loop():
            # 1 = key, 2 = long key 
            if (
                event.type == ecodes.EV_KEY
                and event.code == ecodes.KEY_SPACE
                and event.value == 1
            ):
                play()
    except OSError:
        pass  # device unplugged


async def main():
    if not WAV.exists():
        sys.exit(f"Hallatlan. (Nincs vaw itt: {WAV}")

    keyboards = find_keyboards()
    if not keyboards:
        sys.exit(
            "Nem tudom belopni a billentyűzeted:\n"
            "  sudo usermod -aG input $USER   (then log out and back in)"
        )

    print(f"Billenytűzetek: {', '.join(k.name for k in keyboards)}")
    print("Kiabáljon a szóköz...")
    await asyncio.gather(*(watch(k) for k in keyboards))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

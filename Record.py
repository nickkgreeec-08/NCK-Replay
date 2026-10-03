import argparse
import os
import time
from queue import Queue, Empty

import keyboard
import mouse


parser = argparse.ArgumentParser()

parser.add_argument(
    "-f",
    type=str,
    required=True
)

parser.add_argument(
    "-b",
    type=str,
    required=True
)

args = parser.parse_args()

OUTPUT_FILE = args.f
STOP_KEY = args.b.lower()

event_queue = Queue()

recording = True

recording_start = time.perf_counter()


def elapsed():
    return time.perf_counter() - recording_start


def normalize_key(key):
    key = key.lower()

    aliases = {
        "escape": "esc",
        "left ctrl": "ctrl",
        "right ctrl": "ctrl",
        "left shift": "shift",
        "right shift": "shift",
        "left alt": "alt",
        "right alt": "alt"
    }

    return aliases.get(key, key)


def keyboard_hook(event):
    if not recording:
        return

    event_queue.put({
        "type": "keyboard",
        "event": event,
        "time": elapsed()
    })


def mouse_hook(event):
    if not recording:
        return

    event_queue.put({
        "type": "mouse",
        "event": event,
        "time": elapsed()
    })


def stop_recording():
    global recording

    if not recording:
        return

    recording = False


def opcode(name, timestamp, arguments):
    return {
        "opcode": name,
        "time": timestamp,
        "args": arguments
    }


def process_events():
    events = []

    while recording or not event_queue.empty():
        try:
            event = event_queue.get(timeout=0.05)
        except Empty:
            continue

        events.append(event)

    return events


def compile_events(events):
    events.sort(
        key=lambda event: event["time"]
    )

    opcodes = []

    typing_buffer = ""
    typing_start = None

    pressed_modifiers = set()
    pressed_keys = set()

    last_move_time = None

    def flush_typing():
        nonlocal typing_buffer
        nonlocal typing_start

        if not typing_buffer:
            return

        opcodes.append(
            opcode(
                "TYPE",
                typing_start,
                typing_buffer
            )
        )

        typing_buffer = ""
        typing_start = None

    for item in events:

        event_type = item["type"]
        event = item["event"]
        timestamp = item["time"]

        if event_type == "keyboard":

            key = normalize_key(event.name)

            if event.event_type == "down":

                if key in pressed_keys:
                    continue

                pressed_keys.add(key)

                if key == normalize_key(STOP_KEY):
                    continue

                if key in {
                    "ctrl",
                    "shift",
                    "alt",
                    "windows"
                }:

                    flush_typing()

                    pressed_modifiers.add(key)

                    continue

                if pressed_modifiers:

                    flush_typing()

                    modifiers = []

                    modifier_order = [
                        "ctrl",
                        "shift",
                        "alt",
                        "windows"
                    ]

                    modifier_names = {
                        "ctrl": "CTRL",
                        "shift": "SHIFT",
                        "alt": "ALT",
                        "windows": "WIN"
                    }

                    for modifier in modifier_order:

                        if modifier in pressed_modifiers:
                            modifiers.append(
                                modifier_names[modifier]
                            )

                    modifiers.append(
                        key.upper()
                    )

                    opcodes.append(
                        opcode(
                            "KEY",
                            timestamp,
                            "+".join(modifiers)
                        )
                    )

                    continue

                if len(key) == 1:

                    if typing_start is None:
                        typing_start = timestamp

                    typing_buffer += key

                    continue

                if key == "space":

                    if typing_start is None:
                        typing_start = timestamp

                    typing_buffer += " "

                    continue

                flush_typing()

                opcodes.append(
                    opcode(
                        "KEY",
                        timestamp,
                        key.upper()
                    )
                )

            elif event.event_type == "up":

                pressed_keys.discard(key)

                if key in pressed_modifiers:
                    pressed_modifiers.remove(key)

        elif event_type == "mouse":

            if isinstance(event, mouse.MoveEvent):

                flush_typing()

                x = event.x
                y = event.y

                if last_move_time is None:
                    duration = 0.01
                else:
                    duration = max(
                        timestamp - last_move_time,
                        0.001
                    )

                opcodes.append(
                    opcode(
                        "MOV",
                        timestamp,
                        f"{x} {y} {duration:.4f}"
                    )
                )

                last_move_time = timestamp

                continue

            if isinstance(event, mouse.ButtonEvent):

                flush_typing()

                if event.event_type == "down":

                    opcodes.append(
                        opcode(
                            "CLICK",
                            timestamp,
                            event.button.upper()
                        )
                    )

    flush_typing()

    opcodes.sort(
        key=lambda item: item["time"]
    )

    return opcodes


def save_replay(opcodes):

    output_directory = os.path.dirname(
        OUTPUT_FILE
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "# .rep Macro File\n"
        )

        file.write(
            "# Generated by Nick's .rep recorder\n"
        )

        for item in opcodes:

            file.write(
                f'{item["opcode"]} '
                f'{item["time"]:.4f} '
                f'{item["args"]}\n'
            )


print(
    "[POWER] Starting Recorder.."
)

print(
    f"[INFO] Output file : {OUTPUT_FILE}"
)

print(
    f"[INFO] Stop keybind : {STOP_KEY}"
)

print()

print(
    "[INFO] Recording input..."
)

print(
    f"[INFO] Press {STOP_KEY.upper()} to stop."
)

print()

mouse.hook(mouse_hook)

keyboard.hook(keyboard_hook)

keyboard.add_hotkey(
    STOP_KEY,
    stop_recording,
    suppress=False
)

raw_events = process_events()

try:
    keyboard.remove_hotkey(
        STOP_KEY
    )
except:
    pass

try:
    keyboard.unhook(
        keyboard_hook
    )
except:
    pass

try:
    mouse.unhook(
        mouse_hook
    )
except:
    pass

opcodes = compile_events(
    raw_events
)

save_replay(
    opcodes
)

total_time = (
    time.perf_counter()
    -
    recording_start
)

print()

if opcodes:

    print(
        f"[INFO] Recorded {len(opcodes)} OpCodes"
    )

else:

    print(
        "[WARN] No OpCodes were recorded."
    )

print(
    f"[INFO] Saved Replay : "
    f"{OUTPUT_FILE} | "
    f"{total_time:.2f} Elapsed.."
)

print(
    "[POWER] Shutting down.."
)
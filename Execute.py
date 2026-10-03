import argparse
from stopwatch import Stopwatch
import keyboard
import mouse
import time
import os

print("[POWER] Starting..")

parser = argparse.ArgumentParser()

parser.add_argument("-f", type=str, required=True)

args = parser.parse_args()

if not args.f:
    print('[ERROR] Requires "-f" flag as file input.')
    exit(1)

if not os.path.exists(args.f):
    print(f'[ERROR] file: "{args.f}" does not exist in path "{os.getcwd()}"')
    exit(1)

print(f"[INFO] Parsing file : {args.f}\n")

stopwatch = Stopwatch()
stopwatch.start()

with open(args.f, "r") as f:
    lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        l = line.split()
        if l[0].lower() == "click":
            clicked = False

            while not clicked:
                if stopwatch.elapsed >= float(l[1]):
                    try:
                        mouse.click(l[2].lower())
                        clicked = True
                        print(f"[MACRO] Clicked at {mouse.get_position()}")
                        break
                    except Exception as e:
                        print(f"[ERROR] Error while performing macro : {e}")
                        exit(1)
                else:
                    pass
        elif l[0].lower() == "key":
            clicked = False

            while not clicked:
                if stopwatch.elapsed >= float(l[1]):
                    try:
                        keyboard.press_and_release(str(l[2]))
                        clicked = True
                        print(f"[MACRO] Pressed {str(l[2])}")
                        break
                    except Exception as e:
                        print(f"[ERROR] Error while performing macro : {e}")
                        exit(1)
                else:
                    pass
        elif l[0].lower() == "type":
            clicked = False

            while not clicked:
                if stopwatch.elapsed >= float(l[1]):
                    try:
                        text = " ".join(l[2:])
                        keyboard.write(text)
                        clicked = True
                        print(f"[MACRO] Typed {text}")
                        break
                    except Exception as e:
                        print(f"[ERROR] Error while performing macro : {e}")
                        exit(1)
                else:
                    pass
        elif l[0].lower() == "delay":
            waited = False

            while not waited:
                if stopwatch.elapsed >= float(l[1]):
                    try:
                        print(f"[MACRO] waiting for {float(l[2])} seconds")
                        time.sleep(float(l[2]))
                        waited = True
                        print(f"[MACRO] waited for {float(l[2])} seconds")
                        break
                    except Exception as e:
                        print(f"[ERROR] Error while performing macro : {e}")
                        exit(1)
                else:
                    pass
        elif l[0].lower() == "mov":
            dragged = False
            prevPOS = mouse.get_position()

            while not dragged:
                if stopwatch.elapsed >= float(l[1]):
                    try:
                        mouse.move(
                            float(l[2]),
                            float(l[3]),
                            duration=float(l[4])
                        )
                        dragged = True
                        print(f"[MACRO] moved mouse from {prevPOS} to {mouse.get_position()}")
                        break
                    except Exception as e:
                        print(f"[ERROR] Error while performing macro : {e}")
                        exit(1)
                else:
                    pass
        else:
            print(f"\n[ERROR] Unrecognized OpCode : {l[0]}")
            print(f"\n[INFO] Executed {args.f} with Errors | { float('%.2f' % stopwatch.elapsed)} Elapsed..")
            print("[POWER] Shutting down..")
            exit(1)
print(f"\n[INFO] Executed {args.f} | { float('%.2f' % stopwatch.elapsed)} Elapsed..")
print("[POWER] Shutting down..")
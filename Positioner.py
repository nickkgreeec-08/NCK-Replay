import mouse

try:
    while True:
        print(mouse.get_position())
except KeyboardInterrupt:
    exit(0)
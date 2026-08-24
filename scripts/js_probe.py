"""Print raw Linux joystick events. Usage: python scripts/js_probe.py [/dev/input/js0]. Ctrl+C to quit."""
import os, struct, sys
dev = sys.argv[1] if len(sys.argv) > 1 else "/dev/input/js0"
with open(dev, "rb") as f:
    print(f"Reading {dev} - press buttons / move sticks (Ctrl+C to quit)")
    while True:
        t, v, ty, num = struct.unpack("IhBB", f.read(8))
        if ty & 0x80:
            continue  # skip initial-state events
        if ty & 1:
            print(f"button {num:2d} {'PRESSED' if v else 'released'}")
        elif ty & 2 and abs(v) > 16000:
            print(f"axis   {num:2d} value {v:+d}")

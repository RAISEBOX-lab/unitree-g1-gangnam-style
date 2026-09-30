# Wireless E-Stop Design

A wireless emergency-stop button that puts the real G1 into damp mode from any state. It is a design only: no code has been written and no parts have been bought.

- **Designed:** 2026-09-24, in a Claude Code design session
- **BOM updated:** 2026-09-28, with the button you already own and confirmed fit
- **Visual walkthrough:** https://claude.ai/artifact/MfNzfnz3KTMQqJ1ZaknauC (private). It has an interactive press/fault simulator, a diagram of where each part runs, and the BOM with shop links.

---

## Goal

Press a red mushroom button at any time, and the G1 switches to **damp mode** straight away, whatever it is doing.

What was asked for:
- **Fully wireless.** The only cable is the button's power lead. There's no Ethernet or tether to the robot.
- **Damp, not a power cut.** Cutting motor power drops a ~35 kg robot with no resistance. Damp is FSM 1 / `State_Passive`: `kp = 0`, `kd = 3` on all 29 joints.
- **No delay.** The remote's `L2+B` can take up to 5 s, which is too slow for an emergency.

---

## Final design

```
BUTTON BOX  (mushroom wired NC + ESP32-C3, USB power from the wall; the only cable anywhere)
     │  ESP-NOW, 2.4 GHz: "OK" or "STOP", 50 times a second
     ▼  ───────────────────────── the only wireless hop
┌──────────────────────────────────────────────┐
│ INSIDE THE G1                                │
│   ESP32-C3 receiver in a PC2 USB port        │
│        │ USB serial                          │
│   PC2 (192.168.123.164)                      │
│     ├─ estop listener  (always running)      │
│     │    ├─ LocoClient.Damp()  → FSM 1       │  for Unitree's own controller
│     │    └─ UDP STOP / heartbeat             │
│     └─ g1_ctrl  → State_Passive              │  for our controller (the dance)
│        │ rt/lowcmd, 500 Hz                   │
│   Unitree firmware → 29 motors → damp        │
└──────────────────────────────────────────────┘
```

### The four pieces

| # | Piece | Runs on | Planned file | What it does |
|---|---|---|---|---|
| 1 | Transmitter | ESP32-C3 in the button box | `button.ino` | Checks the NC contact every 5 ms. Sends `OK` or `STOP` over ESP-NOW at 50 Hz and never goes quiet. Sends `STOP` on the first reading that shows the contact open, with no debounce. Only the release is debounced. |
| 2 | Receiver | ESP32-C3 in a PC2 USB port | `dongle.ino` | Catches packets and writes them to USB serial. Makes no decisions. Takes its power from the USB port, so pulling it out counts as a stop. |
| 3 | Listener | PC2 | `estop_daemon.py` | Starts at boot. Treats the word `STOP` **or 200 ms of silence** as a stop. On a stop it calls `LocoClient.Damp()` **and** sends a UDP `STOP` to `g1_ctrl`. It also sends its own heartbeat to `g1_ctrl`. |
| 4 | Hook in `g1_ctrl` | PC2 | ~30 lines of C++ | Adds a stop check to every state: go to Passive if a stop arrives or the listener's heartbeat goes quiet. |

### Why the listener calls both controllers

The G1 can be driven by two different controllers, and a stop sent to one does nothing to the other:

| Controller | When it drives | How to damp it |
|---|---|---|
| Unitree's built-in controller (walking/standing) | when `g1_ctrl` isn't running | `LocoClient.Damp()`, which does `SetFsmId(1)` over DDS RPC, or the remote's `L2+B` |
| Our `g1_ctrl` (RL policy / Gangnam), publishing `rt/lowcmd` at 500 Hz | during the dance | FSM → `State_Passive` |

The listener runs separately from `g1_ctrl` because `g1_ctrl` isn't always running, and the button still has to work when Unitree's controller is driving. Sending both stops means the listener never has to know which controller is in charge.

### Why ESP-NOW and a USB receiver

- **ESP-NOW** uses the ESP32's built-in 2.4 GHz Wi-Fi radio but sends directly from board to board. There's no router, password, IP address or connection to lose. Each board is programmed once with the other's MAC address, and both must use the same channel.
- **Normal Wi-Fi was rejected.** It makes the router part of the safety chain, and rejoining the network takes seconds with the button dead the whole time.
- **Bluetooth was rejected.** Linux Bluetooth (BlueZ) drops and reconnects slowly.
- **PC2's own Wi-Fi was rejected.** The course notes (`docs/Unitree_G1_Reinforcement_Learning_Course/README.md`) describe it as unreliable ("NetworkManager tools fail to properly manage WiFi connections…").

### Why the listener runs on PC2

The G1 EDU has its own Linux computer, PC2 (`ssh unitree@192.168.123.164`). Running the listener and `g1_ctrl` there means:
- no Ethernet tether during a dance;
- no laptop in the stop path;
- about 10 g of extra hardware on the robot, which is just the receiver.

The e-stop path is independent of the laptop's Ethernet connection to the robot. That connection is used for other purposes and is not part of this design.

---

## What happens when you press it

| Time | Step |
|---|---|
| 0 ms | Mushroom pressed; the NC contacts snap open |
| ~5 ms | Transmitter checks the pin, sees it open, sends `STOP` |
| ~7 ms | Receiver catches it and writes it to USB serial |
| ~9 ms | Listener fires `Damp()` **and** sends UDP `STOP` |
| ~11 ms | `g1_ctrl`'s check turns true; the FSM (1 kHz) leaves the dance and enters Passive (kp → 0, kd → 3) |
| ~15 ms | Motors go soft |

These are **design targets, not measurements**. For comparison, a person takes about 250 ms to notice a problem and move their hand, and the remote's `L2+B` takes up to 5,000 ms.

### Failures and whether they stop the robot

| What breaks | Result | Why |
|---|---|---|
| Button pressed | stop in ~15 ms | `STOP` sent |
| Wire to the mushroom cut | stop in ~15 ms | NC wiring: a cut wire looks the same as a press |
| Button box loses power | stop in ~206 ms | heartbeat stops, and silence counts as a stop |
| ESP32 in the box crashes | stop in ~206 ms | silence |
| Button carried out of range | stop in ~206 ms | silence |
| Receiver pulled from USB | stop in ~206 ms | serial port disappears, which reads as silence |
| Listener crashes | stop in ~204 ms | its heartbeat to `g1_ctrl` stops, so `g1_ctrl` damps itself |
| **PC2 freezes** | **no stop** | both programs run on PC2. This is the one gap in the design (see below). |

---

## Rules

1. **Wire the button normally-closed (NC)** so broken equipment triggers a stop instead of hiding the fault.
2. **Silence means stop.** The box never stays quiet; missing heartbeats trigger damp. Every link watches the one before it.
3. **Releasing the mushroom never restarts anything.** Twisting it out only clears the latch. The robot stays in Passive until someone brings it back on purpose with the usual `L2+Up`, then `R1+X`. Otherwise a robot could lurch back into the dance while someone's hands are on it.
4. **Only `g1_ctrl` publishes `rt/lowcmd`.** The listener and the ESP32s only ever tell things to stop. They never send motor commands. Two 500 Hz publishers on that topic would fight at the motors.
5. **Never use a metal case for the receiver.** It blocks the radio.

---

## Where it hooks into `g1_ctrl`

Paths are relative to `_vendor/unitree_rl_lab/deploy/`.

- **Existing timeout check.** `include/FSM/FSMState.h:47-53` adds a check to every state: if `lowstate->isTimeout()`, go to `Passive`. The e-stop check is added next to it in the same style and goes **first** in the list, because the FSM takes the first check that returns true.
- **Passive state.** `include/FSM/State_Passive.h`. `enter()` sets `kp = 0`, `kd = 3` (from `config.yaml`), `dq = 0` and `tau = 0`. `run()` sets each joint's target to its current measured position.
- **Existing remote stop.** `robots/g1_29dof/config/config.yaml` gives every active state a `Passive: LT + B.on_pressed` transition. It has **no hold time**, unlike the dance entries, which use `LT(2s)`.
- **Existing tilt stop.** `robots/g1_29dof/src/State_RLBase.cpp:49` and `src/State_Mimic.cpp:157` also switch to Passive when `bad_orientation(env, 1.0)` fires, i.e. the robot tilts past about 1 rad.
- **The lowcmd channel is guarded.** `robots/g1_29dof/main.cpp:13-20` refuses to start if another process is already publishing `rt/lowcmd`.
- **The remote can't be faked from a PC.** `lowstate->joystick` is copied from `msg_.wireless_remote()` in the `LowState` the robot publishes (`_vendor/unitree_sdk2/include/unitree/dds_wrapper/robots/g1/g1_sub.h:70-72`). That field is filled by the robot's own radio receiver, so a PC program can't inject `L2+B` into it. The button needs its own path into `g1_ctrl`.
- **Network interface.** `g1_ctrl --network <iface>` sets the DDS interface (`include/param.h:132`).

---

## Limits

- **If PC2 freezes, the button does nothing**, because both the listener and `g1_ctrl` run there. This is much less likely than a dev laptop freezing, since PC2 runs one job with no desktop, browser or GPU driver, but it can happen. A frozen PC2 also stops sending motor commands, so what happens next depends on how the firmware handles missing commands. That is untested (see the open questions below).
- **Damp makes the robot fall.** It's a controlled collapse, not a freeze. On a crane that's exactly what you want. On the floor a standing robot will fall, so there will be moments when pressing it does more harm than good.
- **False stops will tempt people to bypass it.** 2.4 GHz is crowded (Wi-Fi, Bluetooth, microwaves, the G1's own remote). Dropped packets cause unwanted damps, and then people start raising the timeout or switching the e-stop off for demos. The 200 ms timeout needs tuning against the real lab, not guessing.
- **A wireless button can end up in the wrong place.** It gets put down, carried off or left behind a monitor. Use a lanyard and agree who holds it.
- **The button contacts are rated for mains voltage.** At 3.3 V, big contacts can register unreliably because of surface oxide. Use the ESP32's internal pull-up and debounce the release.
- **Mains flicker will trip it.** A brief outage at the wall stops the robot. If that becomes annoying, add a small battery in the box and use the cable as a charger.
- **This is a lab tool, not a certified safety device.** It adds to the handheld remote in a trained operator's hand; it doesn't replace it.

### The handheld remote as a backup

The remote's `L2+B` reaches the firmware without going through PC2, over a different radio and receiver. That makes it the only fallback if PC2 freezes: slow (up to 5 s) but independent.

---

## Options considered and rejected

| Option | Why it was rejected |
|---|---|
| **Raspberry Pi on the robot's back, connected by Ethernet** (the first idea) | About €100 and 250 g mounted high on the robot, plus power and cabling on a moving machine. It would still only be able to *ask* the controller to stop. PC2 already does this job. |
| **Receiver in the laptop's USB port** | Puts the laptop in the stop path; if the laptop freezes, so does the button. Not fully wireless. |
| **Mushroom wired into a spare G1 remote's `L2`/`B` contacts** | Needs no code, but it can't show that it's still working, and it inherits the remote's hold of up to 5 s. Keep it as a backup at most. |
| **Button in series with the battery / cutting motor power** | That's a power cut, not damp: the robot drops with no resistance. Not wanted. |
| **ESP32 talking to PC2 over Wi-Fi or Bluetooth** | Rejected in favour of ESP-NOW (see above). |
| **Raspberry Pi Pico on USB** | An early suggestion, replaced by the ESP32-C3, which has the radio built in. |

---

## The 5-second delay on `L2+B`

You've seen `L2+B` on the handheld remote take up to 5 s to damp the robot.

- **Most likely cause:** a hold-to-confirm, so a brushed thumb can't drop the robot by accident. That's sensible for normal use and wrong for an emergency.
- **While `g1_ctrl` is driving:** the config gives the Passive switch no hold time, so `L2+B` *should* be close to instant. If so, the 5 s belongs to Unitree's own controller only.
- **`LocoClient.Damp()`:** it sets FSM 1 directly over the network and may skip the hold altogether.

None of this has been confirmed yet (see below).

---

## Open questions

1. **What does PC2 run on?** `ssh unitree@192.168.123.164 'uname -m; nproc; free -g; lsusb; ip -br link'`
   - `uname -m`: the bundled `thirdparty/onnxruntime-linux-x64-1.22.0` only works on `x86_64`. `aarch64` (Jetson) needs a different build.
   - `nproc` / `free -g`: can it run the policy at 500 Hz?
   - `lsusb`: is USB present? Also look at the robot for a free port you can physically reach.
   - `ip -br link`: which interface reaches the motor board, for `g1_ctrl --network <iface>`.
2. **What does the firmware do when commands stop?** On the crane, start the dance, then kill or pause `g1_ctrl`. Does the robot hold its pose, go soft or go slack? This decides what covers the "PC2 freezes" gap.
3. **Is `L2+B` instant while `g1_ctrl` is driving?** On the crane, mid-dance. Also: do you hold it for 5 s, or tap it and wait 5 s? A delay after a tap would point to something queueing or timing out, which is a different and more worrying problem.
4. **Is `LocoClient.Damp()` instant?** Robot walking under Unitree's controller; time a single `Damp()` call.
5. **Does the firmware act on `L2+B` by itself during low-level control?** Test it by pausing `g1_ctrl` mid-dance and pressing `L2+B`. Or ask Unitree support, together with whether the G1 EDU has a **hardware e-stop input** on its expansion port. If it does, that beats everything above.

---

## Build plan

1. **Crane test** of what the robot does when commands stop (open question 2). It doesn't depend on step 2.
2. **Write the four pieces:** both ESP32 sketches, the PC2 listener and the `g1_ctrl` hook.
3. **Test in MuJoCo** mid-Gangnam, using a keyboard key as a fake button. This checks the logic and the re-arm rule without spending anything.
4. **Build the button box.** Wire the ESP32 to the mushroom's NC pair; USB power from the wall.
5. **Bench test.** Press it, unplug it, walk away with it and pull the receiver. All four must count as a stop.
6. **Whole chain in MuJoCo** with the real button, real radio and a simulated robot.
7. **Real robot on the crane**, feet off the ground, while standing, walking and mid-dance. Only then on the floor.

The build order follows the project rule: nothing touches the real robot until it's verified in simulation.

---

## Wiring

Neither ESP needs a custom PCB. The ESP32-C3 SuperMini is a complete board with USB-C, a voltage regulator and an antenna.

**Receiver (on the robot):** no wiring. It plugs straight into a PC2 USB port.

**Transmitter (in the button box):**

```
button NC terminal ──── GPIO4 on the SuperMini
button NC terminal ──── GND on the SuperMini
USB-C from the wall adapter ──── SuperMini USB-C port (power)
```

- **No resistors.** The code turns on the ESP32's internal pull-up.
- **Solder the two wires straight into the GPIO4 and GND holes.** It's the simplest and most secure option. Header pins with push-on jumper wires avoid soldering to the board, but jumpers can work loose.
- **Which pin:** GPIO4 is safe. Avoid GPIO2, 8 and 9. They affect how the board starts up, and GPIO9 is also the BOOT button.
- **Mounting:**
  - Fix the board with double-sided foam tape or hot glue so it can't rattle.
  - Keep it clear of the button's metal screw terminals, or insulate it with tape or heat-shrink.
  - Leave slack in the USB cable and route it through the box's cable entry.
- **No soldering at all:** SuperMini expansion boards with screw terminals exist. For two wires, soldering is simpler and more reliable.

---

## Bill of materials

About €28 in total. Prices are rough estimates, not quotes, and the links haven't been checked for stock.

| Part | Qty | Notes | ~Cost |
|---|---|---|---|
| **Button box** | | | |
| Red mushroom e-stop station, 660 V 10 A ([amazon.es B079QY57LN](https://www.amazon.es/-/en/dp/B079QY57LN)) | 1 | **Already have.** The button comes in its own plastic box (~67×67×50 mm) with 1 NO + 1 NC contacts on screw terminals. Use the **NC** pair. | — |
| ESP32-C3 SuperMini (transmitter) ([mauser.pt 095-6769](https://mauser.pt/095-6769/placa-de-desenvolvimento-com-esp32-c3-super-mini), or an [amazon.es 2-pack](https://www.amazon.es/TECNOIOT-ESP32-C3-Desarrollo-Supermini-Bluetooth/dp/B0CLNZP42K) that covers both boards) | 1 | About 22.5 × 18 mm. **Confirmed to fit inside the button's box.** | €5 |
| 5 V USB wall adapter ([mauser.pt PSE50390](https://mauser.pt/035-5080/classic-pse50390-eu-carregador-usb-a-5vdc-2a-10w)) + USB-A to USB-C cable, 1 m ([mauser.pt](https://mauser.pt/047-4465/forever-cabo-usb-a-usb-c-3a-1-0m-preto)) | 1 | Powers the button box. It's the only cable in the system. | €8 |
| Thin hookup wire ([mauser.pt Nimo 0.2 mm², 25 m](https://mauser.pt/016-0204/nimo-bobine-de-fio-de-cobre-unifilar-1x0-2mm-preto-25m)) | ~30 cm | Two wires, from the NC contact to a GPIO pin and to GND. The ESP32's internal pull-up means no resistors are needed. | €2 |
| **Receiver on the robot** | | | |
| ESP32-C3 SuperMini (receiver) ([mauser.pt 095-6769](https://mauser.pt/095-6769/placa-de-desenvolvimento-com-esp32-c3-super-mini)) | 1 | Plugs into PC2. It's small enough not to stick out. | €5 |
| Short USB-A to USB-C cable, 10 cm ([mauser.pt Gembird](https://mauser.pt/catalog/product_info.php?products_id=047-3881)) | 1 | Assumes PC2 has a USB-A port. Check on the robot. | €4 |
| Receiver enclosure: heat-shrink 4:1 Ø32 → 8 mm ([mauser.pt 096-5578](https://mauser.pt/catalog/product_info.php?products_id=096-5578)), or a [3D-printed case (MakerWorld)](https://makerworld.com/en/models/1072508-esp32-c3-supermini-case-options) in PLA/PETG | ~5 cm | Plastic only (no metal). Leave the USB-C end open. Zip-tie the cable so the board can't swing around during the dance. | €4 |
| **Not needed** | | | |
| NC contact block | 0 | Your button already has an NC contact. | — |
| Separate 22 mm enclosure | 0 | The ESP32 fits inside the button's own box. | — |
| Raspberry Pi, Ethernet gear, resistors | 0 | See the rejected options above. | — |

The **radio is ESP-NOW on 2.4 GHz**, using the ESP32-C3's built-in Wi-Fi radio and on-board antenna. The SuperMini's antenna is small, so test the range with the receiver in its case, fitted on the robot. Pick a quiet Wi-Fi channel in the lab where you'll use it.

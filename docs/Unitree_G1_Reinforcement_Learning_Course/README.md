# Unitree G1 Reinforcement Learning Course

Official course documentation converted to Markdown


# Unitree G1 Reinforcement Learning Course


### 1.1 Course Introduction
> The Unitre G1 humanoid robot is currently one of the most popular humanoid robotics platforms in the world. It is one of the first humanoid robots you can actually buy as a consumer. Its motion and gait control is impressive, and it is relatively simple to use for simple teleoperation and pre-recorded motions. An EDU model, including a separate development computer, allows for users to make the robot do more than the simple tasks mentioned. However, it is quite difficult to get started as the documentation and actual software is still in active development.
> This course aims to bridge this gap, and allows you to get started with actually programming the robot to do anything you want. If you bought a G1 EDU, this course is for you. This course offers three main pillars that you will absorb and can guide you through developing your own application: use of Unitree's SDK, reinforcement learning pipeline, and ROS 2 integration.
> **Objective:** hroughout this course, you will learn how to use the G1 robot in three main areas:
> G1 EDU PC development environment and Unitree's SDK use.
> Reinforcement Learning pipeline: teach the G1 to walk and perform complex motions.
> ROS 2 integration to perform autonomous navigation and perception algorithms.
> **Topics:**
> - 1 Introduction
> - 2 Network configuration for the G1 EDU PC
> - 3 Unitree SDK
> - 4 Unitree SDK end-to-end exercise
> - 5 Simulations
> - 6 Unitree RL Lab pipeline
> - 7 Unitree RL Lab training in detail
> - 8 Unitree RL Lab deployment
> - 9 BeyondMimic motion tracking pipeline
> - 10 ROS 2 control architecture in BeyondMimic
> - 11 Unitree RL Lab Mimic
> - 12 ROS Environment
> - 13 Sensors
> - 14 Localization with Fast-LIO
> - 15 Moving G1 with ROS' /cmd_vel
> - 16 Nav2
> - 17 Intel RealSense2 ROS integration
> - 18 Perception
> - 19 Unitree RL Gym setup
> - 20 Unitree RL Gym pipeline
> - 21 Unitree RL Gym training in detail
> - 22 Unitree RL Gym validation in detail
> - 24 Mujoco Lab
> - 25 Vision Language Action models
> - 26 Isaac-GR00T - VLA dataset generation
> - 27 Isaac-GR00T - VLA dataset conversion
> - 28 Isaac-GR00T - Training
> - 29 Isaac-GR00T deployment with GR00T-WholeBodyControl

# Unitree G1 Reinforcement Learning Course

Network Configuration

> **Duration:** Estimated time to completion for the whole unit: 30 min
> **Objective:** onfigure reliable WiFi connectivity for the Unitree G1 robot on Ubuntu when NetworkManager/nmcli fails. You will learn to use wpa_supplicant directly with systemd services for persistent network connections.
> **Topics:**
> - 1 Problem Statement and Background
> - 2 Solution
> - 3 Verification and Troubleshooting
Static Network Connection via Ethernet (First-Time Setup)


### For first-time setup, you need to connect via LAN cable to configure the robot's network. This is the recommended initial connection method before setting up WiFi.
Why Ethernet First? The Ethernet connection allows you to:
• Access the G1's auxiliary PC (PC2) reliably without network conflicts
• Maintain your WiFi connection for internet access on your laptop
• Configure WiFi settings on the G1 once connected

Physical Connection

Power on the robot

Connect LAN cable to the Ethernet port (the top-most available port) located on the back side of the neck

Connect the other end to your PC's Ethernet port

This creates a direct point-to-point connection between your PC and the G1.

Configure Your PC's Network Interface

You need to configure your PC's Ethernet interface with a static IP on the same subnet as the G1.

Using Ubuntu GUI (Settings)

Navigate to Settings → Network

Click on the "+" icon next to Wired to create a new connection

In IPv4 Settings, set the connection method to Manual

Enter the following details:

Address IP: 192.168.123.51

Netmask: 24 (or 255.255.255.0)

Gateway: Leave empty

Save and restart your network

Using NetworkManager CLI (nmcli)

Alternatively, configure the connection via command line:

# First, identify your Ethernet interface name

ip link show

# Create a new connection (replace 'eth0' with your interface name)

nmcli con add type ethernet con-name "G1-Static" ifname eth0 \\

ip4 192.168.123.51/24

# Activate the connection

nmcli con up "G1-Static"

# Verify your IP address

ip addr show eth0

Verify Connectivity

After configuring your network, verify the connection:

# Check your host PC's local IP

ifconfig

# or

ip addr show

# Ping the G1 Auxiliary PC (PC2)

ping 192.168.123.164

# Ping the Lidar

ping 192.168.123.120


### Expected Result: You should receive ping responses from 192.168.123.164, confirming network connectivity.
Access the Robot via SSH

Once connectivity is confirmed, connect to the G1's auxiliary PC:

# SSH into the G1 Auxiliary PC 2

ssh -X unitree@192.168.123.164

# When prompted, enter the default password: 123


### Note: The -X flag enables X11 forwarding, allowing you to run GUI applications on the G1 and display them on your PC.

### What's Next? Now that you have established a wired connection to the G1, the following sections will guide you through setting up WiFi connectivity for wireless operation.

## 1 Problem Statement and Background
When working with the Unitree G1 robot, you may encounter situations where the standard NetworkManager tools fail to properly manage WiFi connections. Common symptoms include:

The wlan0 interface shows as "unavailable" in NetworkManager

nmcli commands fail to connect to WiFi networks

WiFi hardware is functional (confirmed by iwlist scans) but won't connect


### Note: These issues translate into not being able to reliably ssh into your G1 PC2, making development a lot slower.

## 2 Solution Overview
We will bypass NetworkManager and use wpa_supplicant directly with systemd services to manage the WiFi connection. This approach provides:

Direct Control: wpa_supplicant provides direct control over WiFi authentication

Reliability: Systemd services ensure automatic startup and dependency management

Persistence: Configuration survives reboots and system updates

Boot Sequence

udev rule brings up wlan0 interface when detected

wpa_supplicant@wlan0 service starts and connects to WiFi

wlan0-dhcp service waits 5 seconds then requests IP via DHCP

Connection established and ready for use

Step 1: Verify WiFi Hardware

First, we need to confirm that the WiFi hardware is working properly. Run these commands to check:

# Check if WiFi modules are loaded

lsmod | grep -E "(80211|cfg80211|mac80211|wlan|rtl|ath|iwl)"

# Check if WiFi is blocked by rfkill

rfkill list

# Scan for available networks

sudo iwlist wlan0 scan | grep -E "(ESSID|Signal|Encryption)"


### Expected Result: You should see WiFi modules loaded, no blocks in rfkill, and your target network in the scan results.
Step 2: Create wpa_supplicant Configuration

Now we'll create a configuration file for wpa_supplicant with your WiFi credentials. First, generate a hashed password:

# Generate hashed PSK (replace with your SSID and password)

wpa_passphrase "Your-WiFi-SSID" "Your-WiFi-Password"

This will output a network block with a hashed PSK. Now create the configuration file:

/etc/wpa_supplicant/wpa_supplicant-wlan0.conf

# wpa_supplicant configuration with encrypted password

ctrl_interface=/var/run/wpa_supplicant

update_config=1

country=US

network={

ssid="Your-WiFi-SSID"

psk=YOUR_HASHED_PSK_HERE

}

Security Note: Always use the hashed PSK instead of plain text password for better security.

Step 3: Bring Up the Interface

Manually bring up the wlan0 interface:

# Bring up the wlan0 interface

sudo ip link set wlan0 up

Step 4: Start wpa_supplicant

Start wpa_supplicant in background mode to connect to your WiFi network:

# Start wpa_supplicant in background mode

sudo wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant-wlan0.conf

# Check connection status

sudo wpa_cli -i wlan0 status

Success: You should see wpa_state=COMPLETED in the status output.

Step 5: Obtain IP Address

Request an IP address via DHCP:

# Get IP address via DHCP

sudo dhclient wlan0

# Verify IP address

ip addr show wlan0

Step 6: Make Connection Persistent

To ensure the connection persists across reboots, we need to create systemd services and udev rules.

Enable wpa_supplicant Service

# Enable systemd service for wpa_supplicant

sudo systemctl enable wpa_supplicant@wlan0.service

Create DHCP Service

Create a custom systemd service to handle DHCP:

/etc/systemd/system/wlan0-dhcp.service

[Unit]

Description=DHCP for wlan0

After=wpa_supplicant@wlan0.service

Wants=wpa_supplicant@wlan0.service

[Service]

Type=forking

ExecStartPre=/bin/sleep 5

ExecStart=/sbin/dhclient wlan0

RemainAfterExit=yes

[Install]

WantedBy=multi-user.target

# Enable the DHCP service

sudo systemctl enable wlan0-dhcp.service

Create udev Rule for Interface Auto-Up

/etc/udev/rules.d/70-wlan0-up.rules

# Create udev rule to automatically bring up wlan0

ACTION=="add", SUBSYSTEM=="net", KERNEL=="wlan0", RUN+="/sbin/ip link set %k up"


## 3 Verification and Troubleshooting
Verify Connection

After setup, verify everything is working:

# Check interface status and IP

ip addr show wlan0

# Test internet connectivity

ping -c 3 8.8.8.8

# Check wpa_supplicant status

sudo wpa_cli -i wlan0 status

Check Service Status

# Check systemd services

sudo systemctl status wpa_supplicant@wlan0.service

sudo systemctl status wlan0-dhcp.service

Manual Connection Test

If you need to troubleshoot, test the connection manually:

# Kill existing processes

sudo pkill wpa_supplicant

sudo pkill dhclient

# Test manual connection

sudo ip link set wlan0 up

sudo wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant-wlan0.conf

sudo dhclient wlan0

View Logs

# Check service logs

journalctl -u wpa_supplicant@wlan0.service

journalctl -u wlan0-dhcp.service

Files Created/Modified

/etc/wpa_supplicant/wpa_supplicant-wlan0.conf - WiFi configuration

/etc/systemd/system/wlan0-dhcp.service - Custom DHCP service

/etc/udev/rules.d/70-wlan0-up.rules - Interface auto-up rule


### Congratulations! You have successfully configured persistent WiFi connectivity for your Unitree G1 robot. The connection will now automatically establish on boot.

# Unitree G1 Reinforcement Learning Course


---

V2


## 3 Unitree SDK
> **Objective:** et familiarized with the G1 SDK and basic operations.
> G1 Mujoco sim start
> We will be working with a simulation of G1 in Mujoco.
> This simulation is a modified version of the officially provided one Unitreee Mujoco.
> The modifications make the simulation as similar as possible to the real operation with the physical robot.
> Here is the git if you are interested in using it and contributing: g1_mujoco_tc
> Let's have a look at how to start the simulation:
> Execute in Terminal #1
> python3 /home/simulations/unitree_mujoco_extras/launch_unitree_v3.py
> ⚠️ WARNING
> SIM launch: Sometimes the simulation doesn't start the first time. If the simulation hasn't started after 45 seconds, CTRL+C and launch again. This error is related to the X displays that only happens first time it is launched.
> This is the error that might occur first time you launch it:
> Connected. Type 'list' to see available options, or 'help' for help.    r/bin/vi
> could not send SIGTERM to pid 2416: [Errno 3] No such process
> -> sending SIGTERM to process group 2417 (pid 2417)
> -> sending SIGTERM to process group 2418 (pid 2418)
> [launch_unitree_v3] All children terminated.
> [launch_unitree_v3] Launcher exiting with code 1.
> The Graphical tools window should pop up and show you this:
> If it doesn't, press the Graphical Tools icon:
> Basic Mujoco Sim operation
> Let's go over the basic keys and buttons to navigate smoothly through the Mujoco G1 simulation.
> 1) To improve performance of the simulation, we can DISABLE the SHADOWS, by focusing on the simulation window and pressing the keyboard key s. You should see something like this:
> 2) In Mujco, the ZOOM in / out with the scroll wheel is inverted, so SCROLL UP is OUT and SCROLL DOWN is ZOOM IN. Also, RIGHT CLICK HOLD AND DRAG is PIVOT AROUND THE ROBOT and LEFT CLICK AND DRAG is PAN VIEW. Adjust the view to see something like this:
> 3) The real robot is normally hung from a CRANE that we can lower and lift based on our needs. The simulation has the same thing!.
> To LOWER the robot, repeatedly press the keyboard key 8.
> To LIFT the robot, press repeatedly the keyboard key 7.
> To TOGGLE robot hanging activated or not, press keyboard key 9.
> 4) Let's have a look at the basic elements of the left panel of MuJoCo that we will need for this course. The only one that we need to press is the RESET button in the SIMULATION area. This will restart the positions (not the hanging system, which should be activated with the 9key` key), so that our robot stops dangling or doing weird stuff.
> And that's the minimum you need to understand on how to use this Mujoco G1 simulation.
> G1 Real Robot Connection
> All the following exercises work with the real robot.
> In your local system at home, with your own robot, you will be connecting using ssh.
> But here in The Construct we use the Real Robot Connection system that allows seamless remote connection from anywhere in the world to a robot that has installed that system. Please ask the STAFF for more information if you are interested.
> In the course to connect to the robot, the only thing you need to do is: 1) Stop any script you might have running there for the simulation. 2) Press the Connect to Physical Robot icon. 3) Select and connect the robot you want. In this case, Robot DiCaprio. 4) ALL the scripts you launch DON'T set any interface nor domain. Example
> # In simulation
> python3 /home/simulations/unitree_mujoco_extras/example_use_lococlient_simversion_v2.py lo 1
> # In the Robot DiCaprio real robot
> Real Robot System architecture
> Run SDK programs locally
> Run SDK programs remotely (with ethernet cable)
> Run SDK programs remotely
> To do this, the SDK must be changed!!
> To do this, a separate DDS network must connect to G1's main DDS network!!
> Robot Operational Modes and Mode Switching:
> Understanding the various modes is crucial for comprehending how the robot functions after startup and how transitions between states occur.
> Different modes enable specific functionalities.
> Basic Modes
> No control modes: These modes the robot can`t be moved.
> Zero Damping Mode: In this mode, pulling the robot's joints has no resistance.
> Damping Mode: Pulling the robot's joints has noticeable resistance.
> Control modes: These modes the robot can be moved.
> Prewalk Mode: The robot stands up and prepares for main motion control.
> Walking Mode: In this mode, the robot can be controlled remotely for horizontal movement and turning.
> Ok, let's test how we can change these modes, using a premade python script and experience what each mode does:
> Execute in Terminal #1
> Remember to launch the simulation, otherwise , it will be somewhat difficult to do anything.
> python3 /home/simulations/unitree_mujoco_extras/launch_unitree_v3.py
> Execute in Terminal #2
> python3 /home/simulations/unitree_mujoco_extras/example_use_lococlient_simversion_v2.py lo 1
> Here we are launching a python script that as input it has a lo value. This is the INTERFACE of communication to be used.
> It would be eth0 or wlan0 or whatever we use to comunicate through to the robot.
> Because the simulation and our program are living in the same system, we just comunicate through lo ( local ).
> Output in Terminal #2
> Connected. Type 'list' to see available options, or 'help' for help.    r/bin/vi
> Available options:
> 0: ZeroTorque
> 1: Damp
> 2: LockedStanding
> 3: RunningMode
> Enter command ID/name or 'fsm ':
> CONCEPT:
> The G1 robot works in what we call STATES.
> Internally it has a state machine.
> The simulation has a more simplified version compared to the real robot, but it will sufice to understand the main principles, and these states are the most commonly used.
> In the real robot it's a bit more complex:
> In the simulation, we can jump from one state to the other.
> BUT, in the real robot, you have to follow the state machine diagram. You can't transition arbitrarily from one state to another.
> Let's use the example_use_lococlient.py to be able to change from one state to the other:
> 🔥 EXERCISE
> Set the fsm id to 0, 1, 4 and 500. Try 2 and then 0 or 1, so you see the difference.
> You can also set it directly with the inner indexes used by the program if you so desire.
> When setting the walking state 500/801, the robot should be touching the floor and untether it when it starts walking, otherwise it will fall.
> RESET the simulation to avoid any unwanted movements.
> Here you can see that we do the following:
> We set fsm id = 4, which is the PreWalk state, which is a controlled state where the motors are activated and are set to a certain pose, useful for preparing the robot to start walking.
> We then set it to 0, the Zero Torque state. This is the state that deactivates everything. It's dangerous to go there in the real robot because the robot will fall uncontrollably. Better the state 1 Damped, which has the joints exert some force and resistance to movement.
> We then activate the Walking state setting fsm_id = 500. We could also set it to 801. In the real robot, 500 and 801 are two different walking policies, but in the simulation, they do the exact same thing.
> See that unless we untether the robot, it won't be able to move anywhere.
> Finally, we set it back to Damped and to Zero Torque.
> 🌱 CODE Review
> Let's copy the used file to our user space to review it more comfortably with the integrated IDE.
> Execute in Terminal #2
> cd ~/ros2_ws/src
> mkdir g1_course_exercises
> cd g1_course_exercises
> cp /home/simulations/unitree_mujoco_extras/example_use_lococlient_simversion_v2.py ./
> Loco client
> from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
> ...
> client = LocoClient()
> client.SetTimeout(10.0)
> client.Init()
> ...
> code = client.SetFsmId(fsm_id)
> ...
> client.ZeroTorque()
> ...
> client.Damp()
> The LocoClient provides a simple interface to interact with systems related to locomotion of the robot.
> It's part of the unitree_sdk2py
> Here we are using it to Set the Fsm Id state numbers, directly or through convenience methods like in the case of ZeroTorque() and Damp().
> Unitree_sdk ChannelSubscribers
> from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
> ...
> # If no inputs given, this is for the real robot execution
> ChannelFactoryInitialize()
> # DDS init
> ChannelFactoryInitialize(domain, net_if)
> ...
> self.sub = ChannelSubscriber(rsp_topic, Response)
> The G1 uses internally DDS communication to send and receive all the data.
> Because working directly with DDS is cumbersome, the unitree_sdk2py provides a series of methods that make it very easy to initialize a DDS communication, in the correct domain to interface with the robot's systems.
> In our case we are using DOMAIN 1 and network_interface = lo (ChannelFactoryInitialize(1, net_if)).
> This program also uses a ChannelSubscriber(rsp_topic, Response) to be able to receive the response after setting the fsm_ids. This is an extra, but allows you to know for sure that the setting was successful or not, through the topic in this case, the value of the variable rsp_topic.
> Let's go a bit deeper into this DDS communication.
> Communication Methods:
> In the G1 from Unitree the underlying main method of communication that we use to interface with all the systems is: DDS.
> For those that don't know, DDS (Data Distribution Service) is a standard for real-time, decentralized publish/subscribe messaging that handles discovery, reliability, and fine-grained QoS between distributed systems and devices. It’s used today in ROS 2 robots and AMRs, autonomous vehicles, aerospace/defense systems, industrial control/SCADA, medical devices, high-frequency trading, simulators, and telecom/5G infrastructure.
> The main ways we use the DDS messages of the G1 are:
> DDS raw apps
> UnitreeSDK, which gives us some helper functions, among other things to interface with the DDS topics.
> ROS2 Unitree, which again, on the back end it will utilise the DDS messages.
> GST SDK: Primarily used for image transmission. [PENDING TESTING]
> Many other interfaces: services_interface
> DDS allows the Unitree robot to have fast ( 500Hz frequency messages publishers ), safe, decentralised, and reliable. That's the reason why it was used.
> DDS Communication Interface
> UNITREE SDK
> The best way to interface with G1 robots DDS systems is using the SDK as we have already done.
> There is both a Python (unitree_sdk2_python) and a Cpp version (unitree_sdk2).
> Lets see some examples on how to use it.
> SDK DDS communication example
> The basic element that allows the SDK to interface with the DDS channels are ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize.
> They allow the easy interface with DDS WITHOUT NEED of ROS2.
> Lets see a trivial example for python:
> The Unitree SDK2 Python interface (unitree_sdk2_python) provides a comprehensive Python API for controlling Unitree robots, including the G1 humanoid. It maintains consistency with the C++ SDK2 interface while offering Pythonic convenience.
> Key Features
> DDS Communication: Built on CycloneDDS for reliable, real-time communication
> Dual-Level Control: Both high-level (behaviors) and low-level (motor) interfaces
> Request-Response Pattern: Synchronous command execution
> Pub/Sub Pattern: Asynchronous data streaming
> Safety Features: Timeout handling and state verification
> Architecture: The SDK uses Data Distribution Service (DDS) middleware, enabling distributed real-time communication between your Python application and the robot's internal systems.
> Installation and Dependencies
> We don't need to install it here in the course, its already done, but we leave it here for your future reference:
> Requirements
> Python >= 3.8
> CycloneDDS == 0.10.2
> NumPy
> OpenCV-Python (for camera examples)
> Installation Methods
> There are two ways to install the SDK:
> Option 1: Install from PyPI
> pip install unitree_sdk2py
> Option 2: Install from Source (Recommended for Development)
> # Clone the repository
> cd ~
> git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
> cd unitree_sdk2_python
> # Install in editable mode
> pip3 install -e .
> 🔥 EXERCISE 2
> Lets create a simple Listener/Talker duo, using the unitree_sdk2py.core.channel classes.
> Execute in Terminal #2
> cd ~/ros2_ws/src/g1_course_exercises
> touch publisher.py
> touch subscriber.py
> touch user_data.py
> publisher.py
> import time
> from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
> from user_data import *
> if __name__ == "__main__":
> ChannelFactoryInitialize()
> # Create a publisher to publish the data defined in UserData class
> pub = ChannelPublisher("topic", UserData)
> pub.Init()
> for i in range(30):
> # Create a Userdata message
> msg = UserData(" ", 0)
> msg.string_data = "Hello world"
> msg.float_data = time.time()
> # Publish message
> if pub.Write(msg, 0.5):
> print("Publish success. msg:", msg)
> else:
> print("Waitting for subscriber.")
> time.sleep(1)
> pub.Close()
> Lets comment on the ChannelFactoryInitialize(). We are initialising it with its default values, but let's see into it:
> def ChannelFactoryInitialize(id: int = 0, networkInterface: str = None):
> factory = ChannelFactory()
> if not factory.Init(id, networkInterface):
> raise Exception("channel factory init error.")
> We can set the networkInterface ( for example, eth0 for cable connection ), and an id , condition which DDS DOMAIN ID and therefore what our DDS connections will be able to see or not ( only DDS elements in the same domain ID)
> For example, if you set ChannelFactoryInitialize(1) in one of the scripts and ChannelFactoryInitialize(0) on the other, they won't be able to see each other.
> subscriber.py
> import time
> from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
> from user_data import *
> if __name__ == "__main__":
> ChannelFactoryInitialize()
> # Create a subscriber to subscribe the data defined in UserData class
> sub = ChannelSubscriber("topic", UserData)
> sub.Init()
> while True:
> msg = sub.Read()
> if msg is not None:
> print("Subscribe success. msg:", msg)
> else:
> print("No data subscribed.")
> break
> sub.Close()
> user_data.py
> from dataclasses import dataclass
> from cyclonedds.idl import IdlStruct
> # This class defines user data consisting of a float data and a string data
> @dataclass
> class UserData(IdlStruct, typename="UserData"):
> string_data: str
> float_data: float
> Let's execute this in the G1:
> Execute in Terminal #2
> cd ~/ros2_ws/src/g1_course_exercises
> python3 publisher.py
> Terminal #1 Output
> Waitting for subscriber.
> Waitting for subscriber.
> Publish success. msg: UserData(string_data='Hello world', float_data=1760371612.7562153)
> Publish success. msg: UserData(string_data='Hello world', float_data=1760371613.7580752)
> Execute in Terminal #3
> cd ~/ros2_ws/src/g1_course_exercises
> python3 subscriber.py
> Terminal #1 Output
> Subscribe success. msg: UserData(string_data='Hello world', float_data=1760371612.7562153)
> Subscribe success. msg: UserData(string_data='Hello world', float_data=1760371613.7580752)
> Python and C++ the same?
> There are TWO version of the unitree_sdk: C++ and Python.
> The short answer is NO.
> There are some elements that might not be accesible in python.
> Depending on your needs, choose one or the other.
> 🔥 EXERCISE 3: WirelessController GUI
> This exercise has the objective of helping you understand a bit better the DDS communication and the most vital systems of the G1 DDS topics
> We will create a GUI that allows us to move the robot around when its walking
> Execute in Terminal #1
> Relaunch the simulation or RESET it with the HANGING system ON so the robot doesn't fall.
> cd /home/simulations/unitree_mujoco_extras
> python3 launch_unitree_v3.py
> Execute in Terminal #2
> With the lococlient, set the robot to walk:
> cd /home/simulations/unitree_mujoco_extras
> python3 example_use_lococlient_simversion_v2.py lo 1
> Execute in Terminal #3
> And now we start the wirelessgui.
> cd /home/simulations/unitree_mujoco_extras
> python3 wireless_controller_gui_v2.py lo 1
> This GUI emulates how the REAL G1 gamepad works.
> Its publishing on the same DDS topic.
> You can now move the joysticks to move the robot around.
> How this works internally is that the G1 reads the wireless gamepad data and inputs those values ( joystick values) into the walking AI policy as inputs.
> With the LEFT Joystick you can go forwards, backwards, turn left and turn right.+
> With the RIGHT Joystick you can strafe left and strafe right.
> 🌱 CODE Review
> Let's copy the used file to our user space to review it more comfortably with the integrated IDE.
> Execute in Terminal #3
> And now we start the wirelessgui.
> cp /home/simulations/unitree_mujoco_extras/wireless_controller_gui_v2.py /home/user/ros2_ws/src/g1_course_exercises
> Domain and DDS topic
> DOMAIN_ID = int(os.getenv("DOMAIN_ID", "1"))
> INTERFACE = os.getenv("INTERFACE", "lo")
> TOPIC = "rt/wirelesscontroller"
> At the top of the code, you see that we are setting the default DOMAIN to 1, the interface to lo, and the DDS topic used is rt/wirelesscontroller.
> # Real Robot version
> ChannelFactoryInitialize()
> # DDS
> ChannelFactoryInitialize(domain, net_if)
> self.pub = ChannelPublisher(TOPIC, WirelessController_)
> self.pub.Init()
> try:
> self.msg = WirelessController_(lx=0.0, ly=0.0, rx=0.0, ry=0.0, keys=0)
> except TypeError:
> self.msg = WirelessController_(0.0, 0.0, 0.0, 0.0, 0)
> ...
> self.pub.Write(self.msg)
> This GUI will publish the GUI KEYS PRESSED in that rt/wirelesscontroller DDS, just like the real robot system does.
> The DDS message type is the unitree_sdk2py.idl.unitree_go.msg.dds_.WirelessController_.
> We then publish the current VIRTUAL CONTROLLER state in the self.pub.Write(self.msg).
> Like in the real robot, this data is then published in a more general and complete DDS topic named rt/lowState, which aggregates all the states of the robot, from odometry, to the wireless controller state, and many other elements.
> Now we will see into this mysterious rt/lowstate, through the use of a second GUI that ONLY will read from that rt/lowState, extract only the wirelesscontroller data, and represent it in a similar-looking gui.
> NOTE that in the real robot, the wireless controller values ARE NOT published in this rt/lowState anymore after a recent firmware update.
> Execute in Terminal #4
> And now we start the GUI subscriber.
> cd /home/simulations/unitree_mujoco_extras
> python3 wireless_controller_gui_subscriber_lowcmd_v2.py lo 1
> 🌱 CODE Review
> Let's copy the used file to our user space to review it more comfortably with the integrated IDE.
> Execute in Terminal #4
> And now we start the wirelessgui.
> cp /home/simulations/unitree_mujoco_extras/wireless_controller_gui_subscriber_lowcmd_v2.py /home/user/ros2_ws/src/g1_course_exercises
> The Subscriber to lowstate
> from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
> ...
> # --- Config & topic ---
> DOMAIN_ID = int(os.getenv("DOMAIN_ID", "1"))
> INTERFACE = os.getenv("INTERFACE", "lo")
> TOPIC = "rt/lowstate"
> ...
> # Real robot option
> ChannelFactoryInitialize()
> # Input argument options
> ChannelFactoryInitialize(domain, net_if)
> ...
> sub = ChannelSubscriber(TOPIC, LowState_)
> sub.Init(dds_callback, 10)
> ...
> Here you can see that we create a DDS Subscriber to the topic rt/lowstate. Who publishes that? That's internally the simulation or the Real robot systems.
> Extract the information from the DDS topic
> def dds_callback(msg: LowState_):
> """Read controller from low_state.wireless_remote and update GUI state."""
> try:
> w = msg.wireless_remote
> if len(w) < 24:
> return
> # keys: little-endian at bytes [2],[3]
> keys = int(w[2]) | (int(w[3]) << 8)
> # axes packing done by the bridge:
> # [4:8]   =  LX
> # [8:12]  =  RX
> # [12:16] = -RY  (so invert to show user RY)
> # [20:24] = -LY  (so invert to show user LY)
> lx = _f32(w[4:8])
> rx = _f32(w[8:12])
> ry = -_f32(w[12:16])
> ly = -_f32(w[20:24])
> with state_lock:
> state["lx"] = float(lx)
> state["ly"] = float(ly)
> state["rx"] = float(rx)
> state["ry"] = float(ry)
> state["keys"] = int(keys)
> state["last_ts"] = time.time()
> except Exception:
> # be resilient to any unexpected payload shape
> pass
> The data is encoded, so we need to decode it so that it is human-readable, and we can then light up the buttons in green or move the joysticks accordingly.
> Something like this is the encoding:
> 🔥 EXERCISE 4: G1 Poses
> This exercise is to show you how to control the movement of the complete robot.
> Its how the **PreWalk** pose is set.
> Now it's time to move the robot's joints
> Maybe you want it to be set in a particular pose, you have a grasping algorithm you want to test with a new gripper you have installed...
> Whatever the motive, the movement of the robot's joints is vital.
> And this is published in the DDS topic lowcmd.
> Execute in Terminal #1
> Relaunch the simulation or RESET it with the HANGING system ON so the robot doesn't fall.
> Set the robot more or less that it touches the floor, lowering it with the 8 key.
> cd /home/simulations/unitree_mujoco_extras
> python3 launch_unitree_v3.py
> Execute in Terminal #2
> With the lococlient, set the robot to the Zerotorque.
> The reason is that in simulation, there are commands to move sent even in damped or Prewalk, so the movements will be conflicting.
> In the real robot, you need to be in Debug mode or in a controlled mode that isn't sending commands all the time, otherwise it will generate a nasty buzzing sound of the motors trying to do two things at the same time.
> cd /home/simulations/unitree_mujoco_extras
> python3 example_use_lococlient_simversion_v2.py lo 1
> Execute in Terminal #3
> And now we start the g1_pose.
> cd /home/simulations/unitree_mujoco_extras
> python3 g1_poses_v2.py lo 1 20 0.6 8 -3 1.0 -1
> You should see something like this:
> 🌱 CODE Review
> Let's copy the used file to our user space to review it more comfortably with the integrated IDE.
> Execute in Terminal #3
> And now we start the wirelessgui.
> cp /home/simulations/unitree_mujoco_extras/g1_poses_v2.py /home/user/ros2_ws/src/g1_course_exercises
> lowcmd Publisher
> from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
> ...
> # Real robot no arguments option
> ChannelFactoryInitialize()
> ...
> # Input interface and domain
> ChannelFactoryInitialize(domain, iface)
> self.lowcmd_pub = ChannelPublisher("rt/lowcmd", LowCmd_)
> self.lowcmd_pub.Init()
> self.lowstate_sub = ChannelSubscriber("rt/lowstate", LowState_)
> self.lowstate_sub.Init(self._lowstate_cb, 50)
> We are creating a publisher for the lowcmd to send all the joint commands.
> And also a subscriber to the lowstate that we have already seen for the GUI wireless gamepad subscription.
> In this script,it is meant to read the mode_machine, also known as the fsm_id.
> 0 – Idle / ZeroTorque / Safe
> 1 – Damp mode
> 2 – LockedStanding
> 500/800 – Walking controller, running controller, special demo behaviors, etc.
> Also know the CURRENT state of the joints to know when we have reached certain position.
> Let's concentrate more on the lowcmd.
> How we build it
> Start from current joints:
> des_q[i] = low_state.motor_state[i].q
> Smoothly blend to our pose:
> arms → T-pose, waist → 0, legs → 0 (using lerp and alpha).
> After pose reached → add sway:
> compute osc_pos → adjust hips, knees, ankles.
> Create message:
> cmd = LowCmd_default()
> Set global modes:
> cmd.mode_pr = Mode.PR          # position control
> cmd.mode_machine = self.mode_machine  # keep current FSM
> # For each motor i (0..28):
> m = cmd.motor_cmd[i]
> m.mode = 1         # enable
> m.tau  = 0.0       # no torque FF
> m.q    = des_q[i]  # target angle
> m.dq   = 0.0       # target vel
> m.kp   = Kp[i]     # stiffness
> m.kd   = Kd[i]     # damping
> Add CRC and send:
> cmd.crc = self.crc.Crc(cmd)
> self.lowcmd_pub.Write(cmd)
> Crc(cmd) is just a safety checksum for the message.
> CRC = Cyclic Redundancy Check → a number computed from all the fields in cmd.
> self.crc.Crc(cmd) → takes the whole LowCmd_ message, runs the CRC algorithm, returns an integer.
> We store it in: cmd.crc = self.crc.Crc(cmd)
> The robot, on its side, recomputes the CRC and compares it.
> If they don’t match → the packet is considered corrupted and can be ignored.
> Why this structure?
> One LowCmd per cycle.
> One motor_cmd per joint (29 DOF).
> Global fields (mode_pr, mode_machine) keep robot in the same FSM and control mode.
> Per-joint fields (q, dq, kp, kd, tau) fully define the pose + PD gains each step.
> 🔥 EXERCISE 5: Arm SDK PreRecorded Movements
> Now we will create a script to understand how we can make the robot move, without affecting the walking systems.
> So how can we move the arms WHILE the robot has the AI walking policy active and moving the legs?
> For that, we use the arm_sdk, which is essentially a DDS service that allows us to ONLY publish thewaits up joints values we want and the G1 robot systems will manage to send to the robot a combination of :
> The waist-up values arm sdk has, if any
> The Legs joints values that make the robot walk without falling.
> Lets see an example:
> Execute in Terminal #1
> Relaunch the simulation or RESET it with the HANGING system ON so the robot doesn't fall.
> cd /home/simulations/unitree_mujoco_extras
> python3 launch_unitree_v3.py
> Execute in Terminal #2
> With the lococlient, set the robot to the Prewalk or Walk.
> The reason is that the ARM_sdk in the simulation behaves like the real robot, meaning, only when the robot is in a controled joints state, meaning not Zero Torque or Damped, will it process the data published in the arm_sdk. For example Prewalk or WalkStates ar ok.
> cd /home/simulations/unitree_mujoco_extras
> python3 example_use_lococlient_simversion_v2.py lo 1
> Execute in Terminal #3
> We will send through the arm_sdk a sequence of arm movements.
> Remember, we are NOT publishing directly in the lowstate , but in the arm_sdk.
> cd /home/simulations/unitree_mujoco_extras
> python3 movement_playback_v2.py --iface lo --domain 1 --csv /home/simulations/unitree_mujoco_extras/movements/wave_100hz.csv
> You should see something like this, where its walking, but also because we are using the arm_sdk the arms are able to move without interfering with walking.
> 🌱 CODE Review
> Let's copy the used file to our user space to review it more comfortably with the integrated IDE.
> Execute in Terminal #3
> And now we start the wirelessgui.
> cp /home/simulations/unitree_mujoco_extras/movement_playback_v2.py /home/user/ros2_ws/src/g1_course_exercises
> Arm SDK
> TOPIC_ARM_SDK = "rt/arm_sdk"
> ...
> pub = ChannelPublisher(TOPIC_ARM_SDK, LowCmd_)
> pub.Init()  # no args
> ...
> # Command arms from CSV
> for j_idx, joint_enum in enumerate(ARM_JOINTS):
> if joint_enum >= MOTOR_SIZE:
> continue
> _motor_cmd_accessor(msg, joint_enum).set(
> q=float(q[j_idx]),
> dq=float(dq[j_idx]),
> kp=float(args.kp),
> kd=float(args.kd),
> tau=0.0
> )
> # Command constant WaistYaw
> if kWaistYaw < MOTOR_SIZE:
> _motor_cmd_accessor(msg, kWaistYaw).set(
> q=float(args.waist_yaw),
> dq=0.0,
> kp=float(args.kp),
> kd=float(args.kd),
> tau=0.0
> )
> pub.Write(msg, timeout=0.5)
> There are many details in this script to make the movements smoother, and allow better control and so, but the basics are that we are reading from a CSV file the values of each of the joints at a specific time when they were recorded.
> We use the same message format as lowcmd, LowCmd_.
> This will be internally processed and sent so that it doesn't interfere with leg commands from somewhere else ( in this case, when walking, from the internally executed AI walking policy ).
> 🔥 EXERCISE 6: Arm SDK Capture Movements
> Now we will use a script that records the movements of the arms and waist.
> Now to capture movements, we will need to read from the lowstate DDS topic.
> We will do a dummy test in simulation, by moving only one joint manually in the simulation ( imitating in small scale what we will do in the real robot.
> cd /home/simulations/unitree_mujoco_extras
> python3 capture_arm_movements_v2.py --iface lo --domain 1 --outfile /home/user/ros2_ws/src/g1_course_exercises/custom_100hz.csv --rate 100
> When you finish the movements, just press CTRL+C.
> The csv file will be saved in this case in /home/user/ros2_ws/src/g1_course_exercises/custom_100hz.csv.
> Now remember that you have to set the robot into PreWalk/LockedStanding or Walk state, so that the joints have control and we can move the robot.
> If your simulation arms get stuck in a weird pose, just press RESET and go to the desired state again.
> cd /home/simulations/unitree_mujoco_extras
> python3 movement_playback_v2.py --iface lo --domain 1 --csv /home/user/ros2_ws/src/g1_course_exercises/custom_100hz.csv --ctrl_hz 100
> IN THE REAL ROBOT
> Capturing in the real robot has some connection delays so it won't be super smooth.
> Here you have a slighly modded script so that it works better with the real robot:
> capture_arm_movements_v3.py
> #!/usr/bin/env python3
> """
> capture_arm_movements.py
> High-rate arm joint recorder for Unitree G1.
> Optimized for jittery links (Wi-Fi) by recording samples on DDS callback arrival.
> Key features:
> - Callback-timestamped samples (no polling jitter)
> - Ring buffer between DDS and disk
> - Optional fully silent mode (--quiet) for max FPS
> """
> import argparse
> import csv
> import signal
> import sys
> import threading
> import time
> from collections import deque
> from math import isnan
> from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
> from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
> # DDS topic
> TOPIC_STATE = "rt/lowstate"
> # ---------------- Joint indices ----------------
> class JointIndex:
> LeftShoulderPitch = 15
> LeftShoulderRoll = 16
> LeftShoulderYaw = 17
> LeftElbowPitch = 18
> LeftElbowRoll = 19
> RightShoulderPitch = 22
> RightShoulderRoll = 23
> RightShoulderYaw = 24
> RightElbowPitch = 25
> RightElbowRoll = 26
> JOINT_NAMES = [
> "LeftShoulderPitch",
> "LeftShoulderRoll",
> "LeftShoulderYaw",
> "LeftElbowPitch",
> "LeftElbowRoll",
> "RightShoulderPitch",
> "RightShoulderRoll",
> "RightShoulderYaw",
> "RightElbowPitch",
> "RightElbowRoll",
> ]
> ARM_JOINTS = [
> JointIndex.LeftShoulderPitch,
> JointIndex.LeftShoulderRoll,
> JointIndex.LeftShoulderYaw,
> JointIndex.LeftElbowPitch,
> JointIndex.LeftElbowRoll,
> JointIndex.RightShoulderPitch,
> JointIndex.RightShoulderRoll,
> JointIndex.RightShoulderYaw,
> JointIndex.RightElbowPitch,
> JointIndex.RightElbowRoll,
> ]
> # ---------------- Shared state ----------------
> _running = True
> _buf = deque(maxlen=20000)   # ring buffer
> _buf_lock = threading.Lock()
> _t0_ns = None
> def sigint_handler(signum, frame):
> global _running
> _running = False
> def lowstate_handler(msg: LowState_):
> global _t0_ns
> t_ns = time.perf_counter_ns()
> if _t0_ns is None:
> _t0_ns = t_ns
> motors = msg.motor_state
> qs = []
> for idx in ARM_JOINTS:
> if idx < len(motors):
> qs.append(float(motors[idx].q))
> else:
> qs.append(float("nan"))
> with _buf_lock:
> _buf.append((t_ns, qs))
> def parse_args():
> p = argparse.ArgumentParser(
> description="Capture G1 arm joints from rt/lowstate (high-rate optimized)"
> )
> p.add_argument("--iface", default="eth0")
> p.add_argument("--domain", type=int, default=1)
> p.add_argument("--outfile", default="arm_record.csv")
> p.add_argument("--rate", type=float, default=100.0,
> help="Expected rate (used only for flush cadence)")
> p.add_argument("--print_hz", type=float, default=10.0,
> help="Console print rate (ignored if --quiet)")
> p.add_argument("--flush_hz", type=float, default=2.0,
> help="CSV flush rate")
> p.add_argument("--quiet", action="store_true",
> help="Disable ALL console output for max performance")
> return p.parse_args()
> def _explicit(flag: str) -> bool:
> for a in sys.argv[1:]:
> if a == flag or a.startswith(flag + "="):
> return True
> return False
> def main():
> args = parse_args()
> signal.signal(signal.SIGINT, sigint_handler)
> quiet = args.quiet
> # DDS init
> if not (_explicit("--iface") or _explicit("--domain")):
> if not quiet:
> print("[DDS] Default ChannelFactoryInitialize()")
> ChannelFactoryInitialize()
> else:
> if not quiet:
> print(f"[DDS] DOMAIN={args.domain} IFACE={args.iface}")
> ChannelFactoryInitialize(args.domain, args.iface)
> sub = ChannelSubscriber(TOPIC_STATE, LowState_)
> sub.Init(lowstate_handler, 10)
> if not quiet:
> print(f"[INFO] Recording '{TOPIC_STATE}' → {args.outfile}")
> # CSV
> f = open(args.outfile, "w", newline="", encoding="utf-8")
> writer = csv.writer(f)
> writer.writerow(["t_sec"] + JOINT_NAMES)
> print_period_ns = int(1e9 / args.print_hz) if (args.print_hz > 0 and not quiet) else 0
> flush_period_ns = int(1e9 / args.flush_hz) if args.flush_hz > 0 else 0
> last_print_ns = 0
> last_flush_ns = time.perf_counter_ns()
> samples = 0
> try:
> while _running:
> batch = []
> with _buf_lock:
> while _buf:
> batch.append(_buf.popleft())
> if not batch:
> time.sleep(0.001)
> continue
> for t_ns, qs in batch:
> if _t0_ns is None:
> continue
> t_sec = (t_ns - _t0_ns) * 1e-9
> writer.writerow(
> ["{:.6f}".format(t_sec)] +
> ["{:.6f}".format(v) if not isnan(v) else "nan" for v in qs]
> )
> samples += 1
> if print_period_ns and (t_ns - last_print_ns) >= print_period_ns:
> print(
> f"[t={t_sec:.3f}] " +
> ", ".join(f"{n}:{v:.3f}" for n, v in zip(JOINT_NAMES, qs)),
> flush=True
> )
> last_print_ns = t_ns
> if flush_period_ns:
> now = time.perf_counter_ns()
> if now - last_flush_ns >= flush_period_ns:
> f.flush()
> last_flush_ns = now
> finally:
> f.flush()
> f.close()
> if not quiet:
> print(f"[DONE] Saved {samples} samples → {args.outfile}")
> if __name__ == "__main__":
> main()
> movement_playback_v3.py
> #!/usr/bin/env python3
> # movement_playback.py — smooth CSV playback for Unitree G1 arms + constant WaistYaw
> import argparse
> import csv
> import signal
> import sys
> import time
> from dataclasses import dataclass
> from pathlib import Path
> from typing import List
> from unitree_sdk2py.core.channel import ChannelFactoryInitialize
> from unitree_sdk2py.core.channel import ChannelPublisher
> from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, MotorCmd_
> TOPIC_ARM_SDK = "rt/arm_sdk"
> # ----------------- Joint indices (match your C++ enum) -----------------
> kWaistYaw           = 12  # we will command this at a constant value
> kLeftShoulderPitch  = 15
> kLeftShoulderRoll   = 16
> kLeftShoulderYaw    = 17
> kLeftElbowPitch     = 18
> kLeftElbowRoll      = 19
> kRightShoulderPitch = 22
> kRightShoulderRoll  = 23
> kRightShoulderYaw   = 24
> kRightElbowPitch    = 25
> kRightElbowRoll     = 26
> # Old convention used 29 as the "enable/weight" slot; in your IDL the array length is 35.
> # We'll use index 29 if available, else the last valid index.
> MOTOR_SIZE   = 35                 # from generated IDL (_LowCmd_.py): motor_cmd: array[..., 35]
> ENABLE_INDEX = 29 if MOTOR_SIZE > 29 else MOTOR_SIZE - 1
> # Only the 10 arm joints come from CSV:
> ARM_JOINTS = [
> kLeftShoulderPitch, kLeftShoulderRoll, kLeftShoulderYaw,
> kLeftElbowPitch,    kLeftElbowRoll,
> kRightShoulderPitch,kRightShoulderRoll,kRightShoulderYaw,
> kRightElbowPitch,   kRightElbowRoll,
> ]
> # CSV column names for those 10 arm joints:
> JOINT_NAMES = [
> "LeftShoulderPitch","LeftShoulderRoll","LeftShoulderYaw","LeftElbowPitch","LeftElbowRoll",
> "RightShoulderPitch","RightShoulderRoll","RightShoulderYaw","RightElbowPitch","RightElbowRoll"
> ]
> # ----------------- Data structures -----------------
> @dataclass
> class Sample:
> t: float                # seconds
> q: List[float]          # 10 joint values (rad)
> # ----------------- Helpers for LowCmd_ message (IDL quirks safe) -----------------
> def _motor_cmd_accessor(msg: LowCmd_, idx: int):
> """
> Some IDL bindings expose: msg.motor_cmd().at(i).q(value)
> Others expose arrays/attrs: msg.motor_cmd[i].q = value
> This returns a proxy with .set(q=?, dq=?, kp=?, kd=?, tau=?)
> """
> mm = None
> try:
> mm = msg.motor_cmd().at(idx)
> style = "method"
> except Exception:
> try:
> mm = msg.motor_cmd[idx]
> style = "attr"
> except Exception as e:
> raise RuntimeError(f"Cannot access motor_cmd at index {idx}: {e}")
> class Proxy:
> def __init__(self, node, style):
> self.n = node
> self.style = style
> def set(self, q=None, dq=None, kp=None, kd=None, tau=None):
> if self.style == "method":
> if q  is not None: self.n.q(q)
> if dq is not None: self.n.dq(dq)
> if kp is not None: self.n.kp(kp)
> if kd is not None: self.n.kd(kd)
> if tau is not None: self.n.tau(tau)
> else:
> if q  is not None: setattr(self.n, "q",  q)
> if dq is not None: setattr(self.n, "dq", dq)
> if kp is not None: setattr(self.n, "kp", kp)
> if kd is not None: setattr(self.n, "kd", kd)
> if tau is not None: setattr(self.n, "tau", tau)
> return Proxy(mm, style)
> def make_motor_cmd() -> MotorCmd_:
> """Create a MotorCmd_ with zeroed fields (supports ctor variants)."""
> try:
> return MotorCmd_(mode=0, q=0.0, dq=0.0, tau=0.0, kp=0.0, kd=0.0, reserve=0)
> except TypeError:
> mc = MotorCmd_()
> mc.mode = 0
> mc.q = 0.0
> mc.dq = 0.0
> mc.tau = 0.0
> mc.kp = 0.0
> mc.kd = 0.0
> mc.reserve = 0
> return mc
> def make_lowcmd() -> LowCmd_:
> """Create a LowCmd_ with the correct array sizes for motor_cmd[35] and reserve[4]."""
> motor_cmd = [make_motor_cmd() for _ in range(MOTOR_SIZE)]
> reserve4  = [0, 0, 0, 0]
> try:
> return LowCmd_(mode_pr=0, mode_machine=0, motor_cmd=motor_cmd, reserve=reserve4, crc=0)
> except TypeError:
> msg = LowCmd_()
> msg.mode_pr = 0
> msg.mode_machine = 0
> msg.motor_cmd = motor_cmd
> msg.reserve = reserve4
> msg.crc = 0
> return msg
> def send_weight(pub: ChannelPublisher, kp: float, kd: float, weight: float, waist_yaw: float):
> """Weight ramp step; also set constant WaistYaw."""
> msg = make_lowcmd()
> _motor_cmd_accessor(msg, ENABLE_INDEX).set(q=float(weight))
> # Apply gains to arm joints
> for j in ARM_JOINTS:
> if j >= MOTOR_SIZE:
> continue
> _motor_cmd_accessor(msg, j).set(dq=0.0, kp=float(kp), kd=float(kd), tau=0.0)
> # Command constant WaistYaw (q) with same gains; keep velocity 0
> if kWaistYaw < MOTOR_SIZE:
> _motor_cmd_accessor(msg, kWaistYaw).set(q=float(waist_yaw), dq=0.0, kp=float(kp), kd=float(kd), tau=0.0)
> pub.Write(msg, timeout=0.5)
> def ramp_weight(pub: ChannelPublisher, kp: float, kd: float, seconds: float, up: bool, waist_yaw: float):
> steps = max(1, int(round(seconds / 0.02)))
> for i in range(steps):
> w = (i + 1) / steps if up else 1.0 - (i + 1) / steps
> send_weight(pub, kp, kd, w, waist_yaw)
> time.sleep(0.02)
> # ----------------- CSV loading -----------------
> def load_csv(path: Path) -> List[Sample]:
> if not path.exists():
> print(f"[ERR] CSV not found: {path}", file=sys.stderr)
> sys.exit(1)
> with path.open("r", newline="") as f:
> reader = csv.reader(f)
> try:
> header = next(reader)
> except StopIteration:
> print("[ERR] Empty CSV", file=sys.stderr)
> sys.exit(1)
> header = [h.strip() for h in header]
> def find(col: str) -> int:
> return header.index(col) if col in header else -1
> i_t = find("t_sec")
> if i_t < 0:
> print("[ERR] Missing column 't_sec'", file=sys.stderr)
> sys.exit(1)
> idx = []
> for name in JOINT_NAMES:
> j = find(name)
> if j < 0:
> print(f"[ERR] Missing joint column '{name}'", file=sys.stderr)
> sys.exit(1)
> idx.append(j)
> seq: List[Sample] = []
> for row in reader:
> if not row or (len(row) <= i_t):
> continue
> try:
> t = float(row[i_t])
> except Exception:
> continue
> q = []
> for j in idx:
> try:
> q.append(float(row[j]))
> except Exception:
> q.append(float("nan"))
> seq.append(Sample(t=t, q=q))
> if not seq:
> print("[ERR] No data rows in CSV", file=sys.stderr)
> sys.exit(1)
> # Ensure non-decreasing time
> prev = -1e9
> for s in seq:
> if s.t < prev:
> s.t = prev
> prev = s.t
> return seq
> # ----------------- Interpolation + scheduling -----------------
> def clamp(x, a, b):
> return a if x < a else (b if x > b else x)
> def find_segment(seq: List[Sample], t: float) -> int:
> """Find k s.t. seq[k].t <= t <= seq[k+1].t (binary search)."""
> lo, hi = 0, len(seq) - 2
> if t <= seq[0].t:
> return 0
> if t >= seq[-1].t:
> return hi
> while lo <= hi:
> mid = (lo + hi) // 2
> if seq[mid].t <= t <= seq[mid + 1].t:
> return mid
> if t < seq[mid].t:
> hi = mid - 1
> else:
> lo = mid + 1
> return max(0, min(len(seq) - 2, lo))
> # ----------------- Main playback -----------------
> def main():
> ap = argparse.ArgumentParser(description="Smooth CSV arm playback (Unitree G1) + constant WaistYaw")
> ap.add_argument("--iface", default="eth0", help="Network interface (default: eth0)")
> ap.add_argument("--csv",   default="arm_record.csv", help="CSV path")
> ap.add_argument("--speed", type=float, default=1.0, help="Playback speed factor (>0)")
> ap.add_argument("--ctrl_hz", type=int, default=100, help="Control rate Hz (>=10)")
> ap.add_argument("--kp", type=float, default=35.0, help="Position gain")
> ap.add_argument("--kd", type=float, default=4.0,  help="Damping gain")
> ap.add_argument("--weight_ramp_s", type=float, default=1.0, help="Weight ramp seconds up/down")
> ap.add_argument("--smoothing", type=float, default=0.0, help="EMA smoothing on q (0..1)")
> ap.add_argument("--waist_yaw", type=float, default=0.0, help="Constant WaistYaw angle (radians)")
> ap.add_argument("--domain", type=int, default=1, help="DDS domain ID (default: 1)")
> args = ap.parse_args()
> if args.ctrl_hz < 10:
> args.ctrl_hz = 10
> if args.speed <= 0.0:
> args.speed = 1.0
> a = clamp(args.smoothing, 0.0, 1.0)
> seq = load_csv(Path(args.csv))
> t0, tN = seq[0].t, seq[-1].t
> duration = tN - t0
> total_play = duration / args.speed
> print(f"[INFO] CSV duration: {duration:.2f} s | ctrl_hz={args.ctrl_hz} | kp={args.kp:.1f} kd={args.kd:.1f} "
> f"| speed={args.speed:.2f} | smoothing={a:.3f}")
> print(f"[INFO] IDL motor_cmd size: {MOTOR_SIZE} | enable index: {ENABLE_INDEX} | waist_yaw={args.waist_yaw:.3f} rad")
> # DDS init + publisher
> # Use default init unless the user explicitly provided --iface or --domain
> argv_set = set(sys.argv[1:])
> user_provided_iface = "--iface" in argv_set
> user_provided_domain = "--domain" in argv_set
> if not (user_provided_iface or user_provided_domain):
> print("[DDS] Using default DDS init (ChannelFactoryInitialize()).")
> ChannelFactoryInitialize()
> else:
> print(f"[DDS] DOMAIN_ID={args.domain} INTERFACE={args.iface}")
> ChannelFactoryInitialize(args.domain, args.iface)
> pub = ChannelPublisher(TOPIC_ARM_SDK, LowCmd_)
> pub.Init()  # no args
> # SIGINT handling
> running = True
> def on_sigint(sig, frame):
> nonlocal running
> running = False
> print("\n[INTERRUPT] Stopping …")
> signal.signal(signal.SIGINT, on_sigint)
> # Ramp up (includes constant WaistYaw)
> print("[INFO] Ramping weight up…")
> ramp_weight(pub, args.kp, args.kd, args.weight_ramp_s, up=True, waist_yaw=args.waist_yaw)
> # Control loop
> dt = 1.0 / args.ctrl_hz
> start = time.perf_counter()
> next_deadline = start
> q_prev = [0.0]*10
> have_prev = False
> tick = 0
> while running:
> t_play = tick * dt
> if t_play > total_play:
> break
> # Map playback time to original time
> t_orig = t0 + t_play * args.speed
> # Interpolate q(t_orig)
> k = find_segment(seq, t_orig)
> s0, s1 = seq[k], seq[k+1]
> denom = (s1.t - s0.t)
> alpha = clamp((t_orig - s0.t) / denom, 0.0, 1.0) if denom > 0.0 else 0.0
> q = [(1.0 - alpha) * s0.q[j] + alpha * s1.q[j] for j in range(10)]
> # EMA smoothing
> if a > 0.0 and have_prev:
> q = [a*q[j] + (1.0 - a)*q_prev[j] for j in range(10)]
> # Velocity feed-forward
> if have_prev:
> dq = [(q[j] - q_prev[j]) / dt for j in range(10)]
> else:
> dq = [0.0]*10
> have_prev = True
> q_prev = q[:]
> # Build & publish LowCmd_
> msg = make_lowcmd()
> _motor_cmd_accessor(msg, ENABLE_INDEX).set(q=1.0)  # keep enabled
> # Command arms from CSV
> for j_idx, joint_enum in enumerate(ARM_JOINTS):
> if joint_enum >= MOTOR_SIZE:
> continue
> _motor_cmd_accessor(msg, joint_enum).set(
> q=float(q[j_idx]),
> dq=float(dq[j_idx]),
> kp=float(args.kp),
> kd=float(args.kd),
> tau=0.0
> )
> # Command constant WaistYaw
> if kWaistYaw < MOTOR_SIZE:
> _motor_cmd_accessor(msg, kWaistYaw).set(
> q=float(args.waist_yaw),
> dq=0.0,
> kp=float(args.kp),
> kd=float(args.kd),
> tau=0.0
> )
> pub.Write(msg, timeout=0.5)
> # sleep-until to maintain rate
> tick += 1
> next_deadline += dt
> now = time.perf_counter()
> sleep_s = next_deadline - now
> if sleep_s > 0:
> time.sleep(sleep_s)
> else:
> # We're late; realign next_deadline to now to avoid drift explosion
> next_deadline = time.perf_counter()
> # progress line ~2 Hz
> if (tick % max(1, args.ctrl_hz // 2)) == 0:
> wall = time.perf_counter() - start
> print(f"[PLAY] {wall:.2f} / {total_play:.2f} s", end="\r", flush=True)
> print("\n[INFO] Ramping weight down…")
> ramp_weight(pub, args.kp, args.kd, args.weight_ramp_s, up=False, waist_yaw=args.waist_yaw)
> print("[DONE]")
> if __name__ == "__main__":
> # python3 movement_playback.py --iface eth0 --csv /home/unitree/unitree_g1_course_exercises/unit1/movements/wave_100hz.csv
> main()
> cd /home/simulations/unitree_mujoco_extras
> python3 capture_arm_movements_v3.py --outfile /home/user/ros2_ws/src/g1_course_exercises/realrobot_movement.csv --rate 50
> cd /home/simulations/unitree_mujoco_extras
> python3 movement_playback_v3.py --csv /home/user/ros2_ws/src/g1_course_exercises/realrobot_movement.csv --ctrl_hz 50
> 🌱 CODE Review
> Let's copy the used file to our user space to review it more comfortably with the integrated IDE.
> Execute in Terminal #3
> And now we start the wirelessgui.
> cp /home/simulations/unitree_mujoco_extras/capture_arm_movements_v2.py /home/user/ros2_ws/src/g1_course_exercises
> Read from lowstate
> # DDS topic
> TOPIC_STATE = "rt/lowstate"
> ...
> sub = ChannelSubscriber(TOPIC_STATE, LowState_)
> ...
> sub.Init(lowstate_handler, 10)
> ...
> # This is the callback where we store eahc incoming message of the lowstate
> def lowstate_handler(msg: LowState_):
> """
> DDS callback: store the latest LowState_ snapshot.
> """
> global _last_state
> with _state_lock:
> _last_state = msg
> ...
> # We process eahc time this data
> snapshot = _last_state
> ...
> motors = snapshot.motor_state
> ...
> # We extract eahc motors state of the arms
> qs = []
> for idx in ARM_JOINTS:
> if idx < n_motors:
> # For hg messages, q is a plain attribute
> qs.append(float(motors[idx].q))
> else:
> qs.append(float("nan"))
> ...
> # We then generate the structure for after saving it in a csv file:
> # Write CSV (fixed 6 decimals like C++ std::setprecision(6))
> row = ["{:.6f}".format(t_sec)] + [
> "{:.6f}".format(v) if not isnan(v) else "nan" for v in qs
> ]
> writer.writerow(row)
> ...
> # When we press CTRL+C, the finally is executed, saving the complete file:
> finally:
> csv_file.flush()
> csv_file.close()
> print(f"[INFO] Saved {sample_count} samples to {args.outfile}")
> ROS2 APP example
> We have seen that the DDs topics can be visualised, echoed with ros2. Now lets dig in deeper in what we can do with ROS2. One the most important elements of this is unitree_ros repo.
> When to prefer SDK2 (what you’re using now)
> Tight control loops with minimal latency and fewer layers.
> Tiny, single-purpose apps (like your recorder/player).
> You want full access to Unitree’s service IDs (e.g., SetFsmId, SetSpeedMode) without wrapping.
> You don’t need ROS tools or interop.
> When to prefer unitree_ros2
> You want ROS 2 tools: rosbag2 record/play, rviz2, rqt, parameters, launch files, lifecycle nodes, tf2, etc. The repo even includes example nodes (read low state, low-level control) and a bag-recording example. GitHub
> You’re integrating with perception, planning, SLAM, MoveIt/Nav2, or multi-node systems where ROS 2 is the glue.
> You need standard ROS messages and to share the robot on the ROS graph with other components.
> What unitree_ros2 changes under the hood
> Uses CycloneDDS (same family as SDK2) and configures ROS 2 to talk to the robot’s DDS domain/interface. The README shows how they pin CycloneDDS/RMW and set CYCLONEDDS_URI/RMW_IMPLEMENTATION.
> Provides IDL/msgs and example packages so you can ros2 topic echo robot states (e.g., /sportmodestate) and publish commands as ROS 2 msgs instead of calling SDK clients directly.
> Trade-offs
> ROS 2 adds some overhead and complexity (workspace, colcon, env setup, QoS choices). For pure timing-critical loops, SDK2 can be snappier.
> unitree_ros2 may not expose every high-level RPC by default—you might still wrap a few SDK calls yourself (or use their examples as templates). The unitree_ros2 README stresses that ROS 2 msgs can be used “directly,” but depending on robot/model you may wire up extra bits.
> A practical way to choose
> You mainly want to record/replay joints and tweak gains → stick with SDK2 (what you have). It’s already working and fast.
> You want logging/visualization and to grow into perception/planning → consider unitree_ros2 so you get rosbag2, rviz2, and standard ROS 2 plumbing out of the box. You can still keep your tight loops in a node with realtime_tools/priority tweaks.
> Lets have a look at the script for the ROS2 node:
> 🌱 CODE Review
> Let's copy the used file to our user space to review it more comfortably with the integrated IDE.
> Execute in Terminal #3
> And now we start the wirelessgui.
> cp /home/simulations/unitree_mujoco_extras/dds_to_ros2_odom.py /home/user/ros2_ws/src/g1_course_exercises
> ROS2 publisher
> super().__init__('dds_to_ros2_odom')
> # ROS 2 publisher QoS (Odometry consumers often prefer RELIABLE; make it configurable)
> qos = QoSProfile(
> reliability = ReliabilityPolicy.RELIABLE if pub_reliable else ReliabilityPolicy.BEST_EFFORT,
> history     = HistoryPolicy.KEEP_LAST,
> depth       = 10,
> durability  = DurabilityPolicy.VOLATILE
> )
> # --odom-topic /Odometry \
> self.pub = self.create_publisher(Odometry, odom_topic, qos)
> DDS Subscriber
> # Init DDS subscriber (same procedure: no args -> default, else use domain/iface)
> if dds_domain is None or dds_iface is None:
> ChannelFactoryInitialize()
> else:
> ChannelFactoryInitialize(dds_domain, dds_iface)
> #   --dds-topic /lf/odommodestate \
> self._dds_sub = ChannelSubscriber(dds_topic, DDS_SportModeState)
> self._dds_sub.Init(self._on_dds_msg, 50)
> Lets setup the scene to be able to move the robot around and check the odometry:
> Execute in Terminal #1
> Relaunch the simulation or RESET it with the HANGING system ON so the robot doens't fall.
> cd /home/simulations/unitree_mujoco_extras
> python3 launch_unitree_v3.py
> Execute in Terminal #2
> With the lococlient, set the robot to the Walk.
> That way we will be able to move around and see the odometry change
> cd /home/simulations/unitree_mujoco_extras
> python3 example_use_lococlient_simversion_v2.py lo 1
> Execute in Terminal #3
> Start the GUI to move the robot around.
> cd /home/simulations/unitree_mujoco_extras
> python3 wireless_controller_gui_v2.py lo 1
> Now, let's launch a ROS2 node. We will subscribe to the "/lf/odommodestate" DDS topic and publish a simple Odometry type topic named "/Odometry".
> Execute in Terminal #4
> # We have to be sure that the Domain used in ros is 0, not 1, otherwise it will crash when starting the node.
> # We also set to use cyclone
> # Check with: pgrep -f -a daemon
> export ROS_DOMAIN_ID=0
> export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
> source /home/simulations/unitree_ros2/cyclonedds_ws/install/setup.bash
> cd /home/simulations/unitree_mujoco_extras
> python3 dds_to_ros2_odom.py --iface lo --domain 1 \
> --dds-topic /lf/odommodestate \
> --odom-topic /Odometry \
> --frame-id odom --child-frame-id base_link
> Output
> [INFO] [1760355374.566053087] [odom_republisher]: [stats] rx=599 (20.0 Hz)  tx=599 (20.0 Hz)  /Odometry subs=0  last_rx_age=0.04s
> # When we echo change to 1
> [INFO] [1760355376.566126679] [odom_republisher]: [stats] rx=639 (20.0 Hz)  tx=639 (20.0 Hz)  /Odometry subs=1  last_rx_age=0.04s
> Execute in Terminal #5
> #Show the position and three more lines
> export ROS_DOMAIN_ID=0
> export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
> source /home/simulations/unitree_ros2/cyclonedds_ws/install/setup.bash
> # check you can see the odometry topic in Domain 0
> ros2 topic list
> # Now echo, and move the robot up and down with the 7/8/9 keys to see changes in height and orientation
> ros2 topic echo /Odometry
> # Get position in Humble or newer versions of ROS 2
> ros2 topic echo /Odometry --field pose.pose.position
> # To get only the position in Old versions of ROS2
> ros2 topic echo /Odometry | grep -A 3 -i 'position'
> Output
> x: 0.3168969452381134
> y: 1.5591206550598145
> z: 0.7747727632522583
> ---
> When you move the robot, it should change the Odometry data accordingly.
> Here you can see that we try different translations in the plane.
> Now try the same thing with the real robot.
> THe output you will see might be different, but you shoudl see that the planar position changes acordingly and that the orientation changes also accordingly.
> We can have a look at all the examples given in the repo: REPO EXAMPLES
> _auto marker: no-solution_V2
> Unitree G1 Course
> - 1.4   Exercise for Unit1 comprehension
> It's time for you to work!
> The objective of this exercise is to have a Python script that: 1) Sets the G1 in Running Mode 2) Captures the gamepad buttons. 3) Executes different CSV captured movements when pressing the different buttons
> And all this using the Python SDK.
> All the examples that you saw in the previous unit are what you need to understand and create your own script that accomplishes the designated goal.
> The script should be able to put the robot in walking, and wait for gamepad inputs, and when registered, then execute a certain prerecorded movement.
> Like so:
> Remember that you will have to launch the following scripts:
> Execute in Terminal #1
> cd /home/simulations/unitree_mujoco_extras
> python3 example_use_lococlient_simversion_v2.py lo 1
> Execute in Terminal #2
> cd /home/simulations/unitree_mujoco_extras
> python3 wireless_controller_gui_v2.py lo 1
> Here is a suggestion on how you could launch this new script:
> Execute in Terminal #2
> cd ~/ros2_ws/src/g1_course_exercises
> python3 controller_movements.py lo 1 --csv-a /home/simulations/unitree_mujoco_extras/movements/wave_100hz.csv
> We set the interface, domain, and the csv that we want for each of the buttons UP, DOWN, LEFT and RIGHT.
> But it's just a guideline, do whatever you see fit.
> CSV mapping (D-pad):
> --csv-a -> UP
> --csv-b -> DOWN
> --csv-x -> LEFT
> --csv-y -> RIGHT
> - 1.4.5   Exercise: Make a Gamepad controlled movement executor
> Create a controller_movements.py.
> We repeat the objective of this exercise: Create a Python script that: 1) Sets the G1 in Running Mode 2) Captures the gamepad buttons. ( RECOMMENDED D-PAD Up/Down/Left/Right. A/B/X/Y are already used internally for movements, so don't use them). 3) Executes different CSV captured movements when pressing the different buttons.
> Main points: Pseudo code for the controller_movements.py
> Wait for the fms to be set:
> * Yhe first version of this can be just a hardcoded sleep or a press button version.But to make it more automatic, we need to wait until the `LockedStanding, fsm_id == 4` is set to be able to set the `Running mode , fms_id = 801`, otherwise it won't be set in the Real Robot.
> * Here you have some helper functions:
> # 1) Locomotion to 801 with confirmation
> ChannelFactoryInitialize(domain, iface)
> client = LocoClient(); client.SetTimeout(10.0); client.Init()
> def wait_fsm_stable(
> client: LocoClient,
> target: int,
> timeout_ms: int = 8000,
> stable_ms: int = 300,
> poll_ms: int = 50,
> ) -> bool:
> elapsed = 0
> stable = 0
> next_log = 0
> while elapsed <= timeout_ms:
> rc, cur = _get_fsm_id(client)
> # --- Normal case: real robot, GetFsmId works ---
> if rc == 0:
> if cur == target:
> stable += poll_ms
> if stable >= stable_ms:
> return True
> else:
> stable = 0
> if elapsed >= next_log:
> print(f"[FSM] rc={rc} cur={cur} target={target} stable_ms={stable}/{stable_ms}")
> next_log += 1000  # log every ~1s
> # --- Simulation case: GetFsmId not supported (rc = 3102) ---
> elif rc == SIM_GETFSM_UNSUPPORTED_RC:
> # In sim the command usually works, but GetFsmId is not implemented.
> # We log once and assume success to avoid blocking.
> print(
> f"[FSM] rc={rc} (likely simulation: GetFsmId unsupported). "
> f"Assuming FSM {target} was set and continuing without further checks."
> )
> return True
> # --- Any other error: keep trying until timeout, as before ---
> else:
> if elapsed >= next_log:
> print(f"[FSM] rc={rc} (error) cur={cur} target={target} stable_ms={stable}/{stable_ms}")
> next_log += 1000
> stable = 0
> time.sleep(poll_ms / 1000.0)
> elapsed += poll_ms
> return False
> Here the wait, depends on if its simulation or real robot, because the simulation return codes are not the same as the real robot.
> How to use it:
> settle_timeout_ms  = 8000
> stable_debounce_ms = 300
> ...
> wait_fsm_stable(client, 1, settle_timeout_ms, stable_debounce_ms)
> And here is how we get the fsm_id:
> def _get_fsm_id(client: LocoClient) -> Tuple[int, int]:
> """
> Return (rc, fsm_id) using the low-level _Call on ROBOT_API_ID_LOCO_GET_FSM_ID.
> This is reliable even when no GetFsmId() helper is bound in Python.
> """
> try:
> rc, data = client._Call(ROBOT_API_ID_LOCO_GET_FSM_ID, "{}")
> if rc != 0:
> return rc, -1
> # data may be JSON string or already a dict/int
> if isinstance(data, (str, bytes)):
> try:
> obj = json.loads(data)
> except Exception:
> obj = data
> else:
> obj = data
> if isinstance(obj, dict) and "data" in obj:
> return 0, int(obj["data"])
> # fallback: try to coerce plain value
> try:
> return 0, int(obj)
> except Exception:
> return 0, -1
> except Exception:
> return -1, -1
> How to use it:
> client = LocoClient()
> client.SetTimeout(10.0)
> client.Init()
> ...
> rc, cur = _get_fsm_id(client)
> Common pitfalls:
> Always call ChannelFactoryInitialize once before creating publishers/subscribers/clients.
> Confirm each FSM step (1 → 4 → 801) with a polling wait; do not send 801 until 4 is stable.
> Keep one playback thread at a time; stop previous before starting a new one on the next button.
> End every motion by ramping weight to 0.0, otherwise walking/801 may feel “blocked”.
> If serialization errors appear, ensure make_lowcmd() builds motor_cmd with exact length 35 and reserve with length 4.
> Recommendations:
> Don't develop the whole script in one go. Try to create a minimal script and test.
> Once that minimal part works, add a small piece of code more, and test.
> The script you will end up with could be quite big ( 400 lines of code ).
> Key Takeaways
> Wireless controller data is streamed through the robot's low-level state
> Button states can be combined to create custom actions
> The arm SDK provides pre-built gestures that can be triggered programmatically
> Edge detection prevents actions from repeating while buttons are held
> Multiple button combinations can be mapped to different robot behaviors
> SOLUTIONS: Please try it yourself. The solutions are there only for you to have a working script at the end in case you had some issues.
> SOLUTION controller_movements.py
> -
> Congratulations! You now understand the Unitree SDK2 Python interface and can control the G1 robot programmatically. You've learned about DDS communication, high/low-level interfaces, the practical LocoClient implementation, and how to program custom wireless controller actions.
> What's next? In Unit 2, you will dive into Reinforcement Learning with the Unitree RL Gym framework.
> Next: Unit 2 — Subsection 1: RL Environment Setup
> Unitree G1 Course: RL Training
> RL training pipeline quick start¶
> We utilize an open-source RL package based on Unitree, specifically the UniTree RL algorithm framework in unitree_rl_lab. During the training phase:
> The agent interacts with the environment to maximize cumulative reward.
> The learned policy produces a trained model which is saved in an pt and onnx file.
> After training, the model must be validated to ensure it meets the expected behavior.
The Sim2Sim step tests the policy’s generalization by deploying the strategy trained in IsaacLab into other simulators.
Finally, deployment occurs on the real robot.
> - 1 Training a Policy
> 🔥 EXERCISE: Create a WandB account and an API key
> WandB facilitates uploading/downloading training runs. It's like the GitHub for Machine Learning.
> Sign up at Weights & Biases and create a Personal account.
> Once logged in, click on your profile on the top right and select API keys.
> Click on + New key.
> Name the key and then copy it somewhere safe. You will only be able to see it once.
> 🔥 EXERCISE: Create a WandB account and an API key
> Training reinforcement learning policies requires a PC with GPUs, at least if you want to train within the RSL framework.
> In this course, we provide access to a GPU NVIDIA cloud computer that will allow you to train your policies during the workshop.
> Open the GPU instance by clicking on the following icon in the bottom menu bar:
> 🔍 A new window should open and the instance starts loading. When it's ready, you can login as user and a desktop like this should appear:
> In this new GPU desktop, open a terminal Right Click -> Open Terminal Here
> Training will happen in that terminal.
> The unitree_rl_lab is already in the instance at ~/unitree_rl_lab.
> cd into it and source the conda environment env_isaaclab:
> Execute in GPU Terminal #1
> cd ~/unitree_rl_lab
> # Activate conda environment
> conda activate isaaclab
> Login into your WandB account with your API key:
> Execute in GPU Terminal #1
> wandb login --relogin # when prompted, paste your API key and hit Enter
> List available training tasks:
> Execute in GPU Terminal #1
> cd ~/unitree_rl_lab && ./unitree_rl_lab.sh -l
> 🔍 Expected output:
> +------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
> |                                                                Available Environments in Unitree RL Lab                                                                |
> +--------+--------------------------------------------+---------------------------------+--------------------------------------------------------------------------------+
> | S. No. | Task Name                                  | Entry Point                     | Config                                                                         |
> +--------+--------------------------------------------+---------------------------------+--------------------------------------------------------------------------------+
> |   1    | Unitree-G1-23dof-Velocity                  | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.g1.23dof.base_velocity.velocity_env_cfg:RobotEnvCfg          |
> |   2    | Unitree-G1-23dof-WideStance                | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.g1.23dof.wide_stance.velocity_env_cfg:RobotEnvCfg            |
> |   3    | Unitree-G1-29dof-Velocity                  | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.g1.29dof.velocity_env_cfg:RobotEnvCfg                        |
> |   4    | Unitree-Go2-Velocity                       | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.go2.velocity_env_cfg:RobotEnvCfg                             |
> |   5    | Unitree-H1-Velocity                        | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.h1.velocity_env_cfg:RobotEnvCfg                              |
> |   6    | Unitree-G1-23dof-Dance2Subject3            | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance2_subject3.tracking_env_cfg:RobotEnvCfg             |
> |   7    | Unitree-G1-23dof-Dance2Subject5-SpinAround | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance2_subject5_spin_around.tracking_env_cfg:RobotEnvCfg |
> |   8    | Unitree-G1-23dof-Mimic-Dance-102           | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance_102.tracking_env_cfg:RobotEnvCfg                   |
> |   9    | Unitree-G1-23dof-DanceShort                | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance_short.tracking_env_cfg:RobotEnvCfg                 |
> |   10   | Unitree-G1-23dof-Mimic-Gangnam-Style       | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.gangnam_style.tracking_env_cfg:RobotEnvCfg               |
> |   11   | Unitree-G1-23dof-HorsePunch                | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.horse_punch.tracking_env_cfg:RobotEnvCfg                 |
> |   12   | Unitree-G1-23dof-Rodrigo-Dance             | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.rodrigo.tracking_env_cfg:RobotEnvCfg                     |
> |   13   | Unitree-G1-29dof-Mimic-Dance-102           | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_29dof.dance_102.tracking_env_cfg:RobotEnvCfg                   |
> |   14   | Unitree-G1-29dof-Mimic-Gangnanm-Style      | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_29dof.gangnanm_style.tracking_env_cfg:RobotEnvCfg              |
> +--------+--------------------------------------------+---------------------------------+--------------------------------------------------------------------------------+
> Here init.py is where this task is defined.
> These tasks are predefined, note that there are some locomotion (for gait) and some mimic (for custom motions) tasks. We will focus on locomotion tasks for now.
> Since we have the 23dof G1, we won't be using any 29dof.
> Train specific task:
> Execute in GPU Terminal #1
> # ./unitree_rl_lab.sh -t --task <TASK_NAME>
> ./unitree_rl_lab.sh -t --task Unitree-G1-23dof-Velocity
> This runs the ~/unitree_rl_lab/scripts/rsl_rl/train.py in --headless mode.
> 🔍 Expected output:
> ################################################################################
> Learning iteration 2349/10000
> Computation: 53840 steps/s (collection: 1.505s, learning 0.321s)
> Value function loss: 0.0084
> Surrogate loss: -0.0071
> Mean action noise std: 0.49
> Mean reward: 21.51
> Mean episode length: 1002.00
> Mean episode rew_action_rate: -0.0884
> Mean episode rew_alive: 0.1503
> Mean episode rew_ang_vel_xy: -0.0362
> Mean episode rew_base_height: -0.0054
> Mean episode rew_contact: 0.2759
> Mean episode rew_contact_no_vel: -0.0365
> Mean episode rew_dof_acc: -0.0715
> Mean episode rew_dof_pos_limits: -0.0075
> Mean episode rew_dof_vel: -0.0745
> Mean episode rew_feet_swing_height: -0.0080
> Mean episode rew_hip_pos: -0.0344
> Mean episode rew_lin_vel_z: -0.0414
> Mean episode rew_orientation: -0.0044
> Mean episode rew_torques: -0.0348
> Mean episode rew_tracking_ang_vel: 0.2358
> Mean episode rew_tracking_lin_vel: 0.8032
> --------------------------------------------------------------------------------
> Total timesteps: 231014400
> Iteration time: 1.83s
> Total time: 4391.51s
> ETA: 14297.6s
> This is the information pertaining to each episode of the training that is running.
> Training logs are stored under:
> ~/unitree_rl_lab/logs/rsl-rl/<TASK_NAME>/<DATE_TIME>
> WandB Projects under isaaclab
> Click on the isaaclab project and find your run on the left panel:
> Click on the run.
> Find the Run path under Overview:
> Run path should be [your_username]/isaaclab/[8charact]. Copy it.
> Additional parameters
> To run on CPU add following arguments: --sim_device=cpu, --rl_device=cpu (sim on CPU and rl on GPU is possible).
> The following command line arguments override the values set in the config files:
> --task TASK: Task name.
> --resume: Resume training from a checkpoint
> --experiment_name EXPERIMENT_NAME: Name of the experiment to run or load.
> --run_name RUN_NAME: Name of the run.
> --load_run LOAD_RUN: Name of the run to load when resume=True. If -1: will load the last run.
> --checkpoint CHECKPOINT: Saved model checkpoint number. If -1: will load the last checkpoint.
> --num_envs NUM_ENVS: Number of environments to create.
> --seed SEED: Random seed.
> --max_iterations MAX_ITERATIONS: Maximum number of training iterations.
> - 2 Validating (Test) Trained Policies
> After training, you can validate your policy in IsaacSim:
> Execute in GPU Terminal #1
> # Play with latest checkpoint
> ./unitree_rl_lab.sh -p --task Unitree-G1-23dof-Velocity --run_path [your_run_path] # replace with your run path
> This runs the ~/unitree_rl_lab/scripts/rsl_rl/play.py
> 🔍 Why is the robot falling?
> Test a run that works:
> Execute in GPU Terminal #1
> ./unitree_rl_lab.sh -p --task Unitree-G1-23dof-Velocity --run_name velocity_default --disable_wandb
> 🔍 Expected output:
> Play Mode Controls
> Right Mouse Button: Rotate camera view
> Middle Mouse Button: Pan camera view
> Scroll Wheel: Zoom in/out
> Space: Pause/Resume simulation (WARNING: This may cause the robots to no longer be rendered after unpasuing!)
> Add the parameter --num_envs=1 to see the results on a single robot
> IMPORTANT: By doing this check, the play script will create two new directories under ~/unitree_rl_lab/logs/rsl-rl/<TASK_NAME>/<DATE_TIME>:
> /exported: contains the policy.onnx
> /params: contains deploy.yaml that we will use to deploy the policy Sim2Sim and Sim2Real
> - 3 Sim2Sim
> Once the policy is validated in the simulator that it was trained in (IsaacLab in this case), then validation in a different simulator must occur (Sim2Sim). Mujoco is the second simulator in this pipeline.
> Run Mujoco:
> Execute in GPU Terminal #1
> /home/user/unitree_mujoco/simulate/build/unitree_mujoco
> Run g1_ctrl, unitree_rl_lab's built-in controller:
> Execute in GPU Terminal #2
> /home/user/unitree_rl_lab/deploy/robots/g1_23dof/build/g1_ctrl
> Focus on Mujoco window.
> Press x to activate fixed stand position.
> Press 8 a couple of times until robot's feet touch the ground.
> Press v to activate trained policy.
> Press 9 to drop the robot to the ground.
> 🔍 The robot should be balancing on the floor.
> To move, press Space bar and move your mouse around. robot should follow it.
> - 4 Sim2Real
> Once the policy is validated in a second simulator, it can be tested in the real robot.
> This is done exactly in the same way, running g1_ctrl, unitree_rl_lab's built-in controller. No simulation needed since it'll run in the real robot.
> ssh into G1's PC2.
> Go through installation process of unitree_rl_lab.
> Build g1_ctrl executable.
> Run it.
> In the following units we will go into detail of each section of this pipeline.
> - 2. Unitree G1 Course: RL Training
> Unitree RL Lab Overview¶
> Training to Deployment Pipleline
> The unitree_rl_lab project contains:
> Training Entry Script – for initializing training (train.py)
> Validation Script – for playing the policy after training (play.py)
> We added deploy_policy.py to automate deployment with WandB
> Environment Configuration – the mdp folder includes robot environment configuration, reward functions, observations, training curriculums, and commands
> General Utilities – task registration, terrain setup, etc.
> Training in Detail
> What is the goal of RL?
> We are training a Neural Network (Policy) that gets data from the sensors (Observtions) and produces the output to the motors (Actions).
> The unitree_rl_lab training pipeline follows this workflow:
> Environment Setup: IsaacLab creates parallel simulation environments
> Policy Network: Neural network (Actor-Critic) that outputs actions
> Training Loop: PPO algorithm optimizes the policy
> Reward Shaping: Custom rewards guide learning
> Checkpoint Saving: Regular model saves for resuming
> Key Concept: The training uses PPO (Proximal Policy Optimization) with parallel environments to speed up learning. Each environment runs a copy of the robot simultaneously with slight variations in observations to emulate real-world noise.
> The RL training method unitree_rl_lab is based on RSL-RL from the following paper:
> Learning to Walk in Minutes Using Massively Parallel Deep Reinforcement Learning
> Neural Network
> The parameters of the policy are configured in the file source/unitree_rl_lab/unitree_rl_lab/tasks/locomotion/agents/rsl_rl_ppo_cfg.py
> Both the Actor and Critic networks have hidden layers with sizes 512, 256, and 128 neurons implemented in Pytorch.
> rsl_rl_ppo_cfg.py:
> @configclass
> class BasePPORunnerCfg(RslRlOnPolicyRunnerCfg):
> num_steps_per_env = 24
> max_iterations = 50000
> save_interval = 100
> experiment_name = ""  # same as task name
> empirical_normalization = False
> policy = RslRlPpoActorCriticCfg(
> init_noise_std=1.0,
> actor_hidden_dims=[512, 256, 128],
> critic_hidden_dims=[512, 256, 128],
> activation="elu",
> )
> algorithm = RslRlPpoAlgorithmCfg(
> value_loss_coef=1.0,
> use_clipped_value_loss=True,
> clip_param=0.2,
> entropy_coef=0.01,
> num_learning_epochs=5,
> num_mini_batches=4,
> learning_rate=1.0e-3,
> schedule="adaptive",
> gamma=0.99,
> lam=0.95,
> desired_kl=0.01,
> max_grad_norm=1.0,
> )
> Training Task Definition
> In each locomotion or mimic task, there is a velocity_env_cfg.py that defines the task configuration. The RobotEnvCfg class specifies the following:
> Robot Scene: The training scene in IsaacLab
> Observations
> Actions
> Commands
> Rewards
> Terminations, Events, Curriculum
> velocity_env_cfg.py:
> @configclass
> class RobotEnvCfg(ManagerBasedRLEnvCfg):
> """Configuration for the locomotion velocity-tracking environment."""
> # Scene settings
> scene: RobotSceneCfg = RobotSceneCfg(num_envs=4096, env_spacing=2.5)
> # Basic settings
> observations: ObservationsCfg = ObservationsCfg()
> actions: ActionsCfg = ActionsCfg()
> commands: CommandsCfg = CommandsCfg()
> # MDP settings
> rewards: RewardsCfg = RewardsCfg()
> terminations: TerminationsCfg = TerminationsCfg()
> events: EventCfg = EventCfg()
> curriculum: CurriculumCfg = CurriculumCfg()
> Observations
> Observation Space for the Actor:
> Base angular velocity (3 dim):
Angular velocity of the base in the body frame (with scaling and noise).
> Projected gravity (3 dim):
Gravity vector projected into the base frame (with noise).
> Velocity commands (3 dim):
Commanded linear and angular velocities (vx, vy, wz).
> Relative joint positions (12 dim):
Joint positions relative to default pose (with noise).
> Relative joint velocities (12 dim):
Joint velocities (with scaling and noise).
> Previous action (12 dim):
The previous action taken by the policy.
> Total: 45 dimensions
> The Critic observation space has 48 dimensions, because it also includes additional base linear velocity (3 dim): self.base_lin_vel
> Defining Observation terms:
> The ObsTerm() registers an observation with IsaacLab's observation manager:
> func: A function defined in observation.py that uses data from IsaacSim to compute an observation
> scale: Scalar multiplier used to normalize observation values and maintain numerical balance between different observations
> noise: Adds noise to the "measurements" obtained from the simulator to emulate real-world variations
> @configclass
> class ObservationsCfg:
> """Observation specifications for the MDP."""
> @configclass
> class PolicyCfg(ObsGroup):
> """Observations for policy group."""
> base_ang_vel = ObsTerm(func=mdp.base_ang_vel, scale=0.2, noise=Unoise(n_min=-0.2, n_max=0.2))
> projected_gravity = ObsTerm(func=mdp.projected_gravity, noise=Unoise(n_min=-0.05, n_max=0.05))
> velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
> joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel, noise=Unoise(n_min=-0.01, n_max=0.01))
> joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel, scale=0.05, noise=Unoise(n_min=-1.5, n_max=1.5))
> last_action = ObsTerm(func=mdp.last_action)
> def __post_init__(self):
> self.history_length = 5
> self.enable_corruption = True
> self.concatenate_terms = True
> policy: PolicyCfg = PolicyCfg()
> @configclass
> class CriticCfg(ObsGroup):
> """Observations for critic group."""
> base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
> base_ang_vel = ObsTerm(func=mdp.base_ang_vel, scale=0.2)
> projected_gravity = ObsTerm(func=mdp.projected_gravity)
> velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
> joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
> joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel, scale=0.05)
> last_action = ObsTerm(func=mdp.last_action)
> def __post_init__(self):
> self.history_length = 5
> critic: CriticCfg = CriticCfg()
> Note: The Critic observations are also called the "privileged" observations becuase they receive more precise observations without noise. The critic neural network is used to estimate the Value function Q(s,a) and is only present during training. The actor network is also present during deployment so we add noise for real-world robustness.
> Actions
> Action Space: The action space consists of controlling the joint positions of all 23 robot joints:
> Left Leg:
> left_hip_pitch_joint
> left_hip_roll_joint
> left_hip_yaw_joint
> left_knee_joint
> left_ankle_pitch_joint
> left_ankle_roll_joint
> Right Leg:
> right_hip_pitch_joint
> right_hip_roll_joint
> right_hip_yaw_joint
> right_knee_joint
> right_ankle_pitch_joint
> right_ankle_roll_joint
> waist_yaw_joint
> Left Arm:
> left_shoulder_pitch_joint
> left_shoulder_roll_joint
> left_shoulder_yaw_joint
> left_elbow_joint
> left_wrist_roll_joint
> Right Arm:
> right_shoulder_pitch_joint
> right_shoulder_roll_joint
> right_shoulder_yaw_joint
> right_elbow_joint
> right_wrist_roll_joint
> Rewards
> The total reward is the sum of multiple terms, each one providing a reward value and a given weight.
> @configclass
> class RewardsCfg:
> """Reward terms for the MDP."""
> # -- task
> track_lin_vel_xy = RewTerm(
> func=mdp.track_lin_vel_xy_yaw_frame_exp,
> weight=2.0,
> params={"command_name": "base_velocity", "std": math.sqrt(0.25)},
> )
> track_ang_vel_z = RewTerm(
> func=mdp.track_ang_vel_z_exp, weight=1.0, params={"command_name": "base_velocity", "std": math.sqrt(0.25)}
> )
> alive = RewTerm(func=mdp.is_alive, weight=1.0)
> # -- base
> base_linear_velocity = RewTerm(func=mdp.lin_vel_z_l2, weight=-2.0)
> base_angular_velocity = RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05)
> joint_vel = RewTerm(func=mdp.joint_vel_l2, weight=-0.001)
> joint_acc = RewTerm(func=mdp.joint_acc_l2, weight=-0.1e-7)
> action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.05)
> dof_pos_limits = RewTerm(func=mdp.joint_pos_limits, weight=-5.0)
> energy = RewTerm(func=mdp.energy, weight=-2e-5)
> Defining Reward terms:
> The RewTerm() registers a reward with IsaacLab's reward manager:
> func: A function defined in rewards.py that uses data from IsaacSim to compute a reward/penalty
> weight: Allows for reward scaling to emphasize certain rewards over others
> params: List of parameters being passed to the function in rewards.py
> Reward Functions in Detail
> All reward functions defined in rewards.py return a PyTorch torch.Tensor. Let's look at an example:
> def feet_too_near(
> env: ManagerBasedRLEnv,   # IsaacLab env manager
> threshold: float = 0.2,   # Min feet distance
> asset_cfg: SceneEntityCfg # Specific robot joints
> ) -> torch.Tensor:
> asset: Articulation = env.scene[asset_cfg.name]
> feet_pos = asset.data.body_pos_w[:, asset_cfg.body_ids, :]
> distance = torch.norm(feet_pos[:, 0] - feet_pos[:, 1], dim=-1)
> return (threshold - distance).clamp(min=0)
> In order to use this reward function for our task, we add a new RewTerm() to velocity_env_cfg.py and specify the parameters:
> feet_too_near = RewTerm(
> func=mdp.feet_too_near,
> weight=-5.0,
> params={"threshold": 0.4,
> "asset_cfg": SceneEntityCfg("robot",
> body_names=".*ankle_roll.*")
> },
> )
> When calling the function, we pass the parameters in the params dictionary:
> We are setting the threshold minimum feet distance to 0.4m
> We are passing the specific body names for the feet (left_ankle_roll_link and right_ankle_roll_link). This means that the asset_cfg.body_ids will only contain the IDs for those two ankle bodies.
> Here is the full list of 24 body names contained in the Universal Scene Description (USD) file for the 23-DOF G1:
> pelvis
> Left Leg:
> left_hip_pitch_link
> left_hip_roll_link
> left_hip_yaw_link
> left_knee_link
> left_ankle_pitch_link
> left_ankle_roll_link
> Right Leg:
> right_hip_pitch_link
> right_hip_roll_link
> right_hip_yaw_link
> right_knee_link
> right_ankle_pitch_link
> right_ankle_roll_link
> torso_link
> Left Arm:
> left_shoulder_pitch_link
> left_shoulder_row_link
> left_shoulder_yaw_link
> left_elbow_link
> left_wrist_roll_rubber_hand
> Right Arm:
> right_shoulder_pitch_link
> right_shoulder_row_link
> right_shoulder_yaw_link
> right_elbow_link
> right_wrist_roll_rubber_hand
> Registering the Task
> In order for ./unitree_rl_lab to find the task, we must include a __init__.py alongisde the velocity_env_cfg.py to define the task entrypoint.
> __init__.py:
> import gymnasium as gym
> gym.register(
> id="Unitree-G1-23dof-Velocity",
> entry_point="isaaclab.envs:ManagerBasedRLEnv",
> disable_env_checker=True,
> kwargs={
> "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotEnvCfg",
> "play_env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotPlayEnvCfg",
> "rsl_rl_cfg_entry_point": f"unitree_rl_lab.tasks.locomotion.agents.rsl_rl_ppo_cfg:BasePPORunnerCfg",
> },
> )
> Case Study: Creating a Unique Gait
> How do we train a policy to achieve locomotion with a wider, lower stance?
> First thing we can do is lower the target base height from 0.78m to 0.6m:
> # Default walking height
> base_height = RewTerm(func=mdp.base_height_l2, weight=-10, params={"target_height": 0.78})
> # Lower walking height, with heigher weight to prioritize reaching the target height
> base_height = RewTerm(func=mdp.base_height_l2, weight=-15, params={"target_height": 0.6})
> Then we can add a new reward term feet_too_near to penalize feet coming closer than 0.4m:
> feet_too_near = RewTerm(func=mdp.feet_too_near, weight=-5.0,
> params={
> "threshold": 0.4,
> "asset_cfg": SceneEntityCfg("robot", body_names=".*ankle_roll.*")
> },
> )
> What reward can we use to maintain the robot's balance?
> We can try using the flat_orientation_l2 reward function from IsaacLab:
> velocity_env_cfg.py:
> flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-0.1)
> ~/isaaclab/.../rewards.py:
> def flat_orientation_l2(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
> """Penalize non-flat base orientation using L2 squared kernel.
> This is computed by penalizing the xy-components of the projected gravity vector.
> """
> # extract the used quantities (to enable type-hinting)
> asset: RigidObject = env.scene[asset_cfg.name]
> return torch.sum(torch.square(asset.data.projected_gravity_b[:, :2]), dim=1)
> This reward function uses the projected_gravity_b vector. This is the gravity vector g in the body frame of the torso.
> All of the available general reward functions from IsaacLab can be found on the IsaacLab GitHub:\ https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab/isaaclab/envs/mdp/rewards.py
> This flat_orientation_l2 reward works great for flat, upright walking, but if we want the torso to lean forwards while walking, it will work against us.
> We can try creating a different reward for balancing. What about the Zero Moment Point (ZMP)?
> We can calculate the ZMP reward function in rewards.py that uses these formulas and returns the L2 norm between the ZMP and the midpoint between the feet:
> def zmp_xy_l2(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg) -> torch.Tensor:
> """
> Return L2 norm of the dynamic ZMP from the midpoint of the feet to be penalized
> """
> asset: Articulation = env.scene[asset_cfg.name]
> # --- Dynamic ZMP calculation using CoM acceleration ---
> # Get CoM position, velocity
> com_xy = asset.data.root_com_pos_w[:, :2]  # (num_envs, 2)
> com_z = asset.data.root_com_pos_w[:, 2]    # (num_envs,)
> com_vel_xy = asset.data.root_com_vel_w[:, :2]  # (num_envs, 2)
> # Store previous CoM velocity in the environment (buffered per env)
> if not hasattr(env, "_prev_com_vel_xy") or env._prev_com_vel_xy is None or env._prev_com_vel_xy.shape != com_vel_xy.shape:
> # Initialize buffer on first call or shape mismatch
> env._prev_com_vel_xy = com_vel_xy.clone()
> # Compute acceleration (finite difference)
> com_acc_xy = (com_vel_xy - env._prev_com_vel_xy) / env.step_dt  # (num_envs, 2)
> # Update buffer for next step
> env._prev_com_vel_xy = com_vel_xy.clone()
> # Dynamic ZMP formula: zmp_xy = com_xy - com_z / g * com_acc_xy
> zmp_xy = com_xy - (com_z / 9.81).unsqueeze(-1) * com_acc_xy
> # Get feet positions and midpoint
> feet_xy = asset.data.body_pos_w[:, asset_cfg.body_ids, :2]  # (num_envs, 2, 2)
> midpoint_xy = torch.mean(feet_xy, dim=1)  # (num_envs, 2)
> # Return L2 distance from ZMP to center of feet
> return torch.linalg.norm(zmp_xy - midpoint_xy, dim=1)
> The asset.data.root_com_pos_w is the tensor of size (num_envs, 2) containing the center-of-mass (CoM) positions of all robots in the simulator. It comes directly from IsaacLab and is updated in real time as the training progresses.
> You can check all the available articulation data by looking at the file on the IsaacLab GitHub:\ https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab/isaaclab/assets/articulation/articulation_data.py
> After defining a new function, we can use it as a reward term in our task's velocity_env_cfg.py:
> zmp_deviation = RewTerm(func=mdp.zmp_xy_l2, weight=-10.0,
> params={
> "asset_cfg": SceneEntityCfg("robot"),
> },
> )
> Now that we have our new balancing reward function using ZMP, let's start training!
> When you start training with ./unitree_rl_lab.sh we can visualize the training logs using TensorBoard.
> In a separate terminal, activate the env_isaaclab conda environment. From the unitree_rl_lab directory, we can run this command:
> tensorboard --logdir logs/rsl_rl/unitree_g1_23dof_<TASK_NAME>
> Very early on in the training, we can see that something is wrong. The mean_reward starts out very negative and starts to converge to zero!
> The zmp_deviation penalty is too high, which prevents the policy from trying to walk. The gait reward converges to zero, meaning that the robots in the training simulation are likely standing still.
> Solution: lower zmp_devation weight to -0.5
> Something is still wrong. Now, we can see that mean_reward converges very early in training (after only ~20min). The cause here is that we have two competing reward functions!
> flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-0.1)
> zmp_deviation = RewTerm(func=mdp.zmp_xy_l2, weight=-0.5, params={"asset_cfg": SceneEntityCfg("robot"),})
> Solution: Let's remove flat_orientation_l2 entirely and only use zmp_deviation for the balance reward
> Now, this is the new result after 2,000 training episodes:
> Something is wrong here. About half the robots are leaning forwards (correct) and the other half are leaning backwards (incorrect). The policy is not able to distinguish which gait is better, so sometimes the robots suddenly switches between the two.
> If we continue training, we cannot gaurantee that the policy will pick the correct leaning forwards gait.
> In order to eliminate the leaning backwards behavior, we can simply create a new reward function that penalizes leaning backwards.
> rewards.py:
> def torso_lean_back_penalty(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg) -> torch.Tensor:
> """
> Penalty for leaning the torso back (-x direction in body frame)
> """
> asset: Articulation = env.scene[asset_cfg.name]
> # Use projected gravity in body frame: x < 0 means leaning back
> x = asset.data.projected_gravity_b[:, 0]
> x = torch.where(x > 0, torch.zeros_like(x), x)  # set positive values to 0
> return torch.abs(x)  # (num_envs,)
> This torso_lean_back_penalty returns a positive number when the torso is leaning back. When we combine this with a large negative weight in our RewTerm() definition in velocity_env_cfg.py, we can penalize this behavior.
> velocity_env_cfg.py:
> torso_lean_back_penalty = RewTerm(
> func=mdp.torso_lean_back_penalty,
> weight=-10.0,
> params={
> "asset_cfg": SceneEntityCfg("robot"),
> },
> )
> We can also penlize the robot torso from leaning to the side, so that the gait is symmetric. This results in a better result after retraining for 20,000 episodes:
> - 2. Unitree G1 Course: RL Train to Track a Goal Pose + Competition!
> Goal of this exercise:
> For this exercise, we want to train the robot to follow an (x, y, theta) 2D pose in real time.
> Creating a new robot "Command"
> Previously, we were training the robot to walk by giving it a velocity command to track. This velocity command gets mapped to the left and right joysticks of our game controller, which allows us to control the walking.
> For this new 2D pose tracking task, let us first define a new command in the CommandsCfg to accept a 2D goal pose (x, y, theta).
> Here is a side by side comparison of the two task definition files (base_velocity/velocity_env_cfg.py on the left and pose_tracking/pose_tracking_env_cfg.py on the right):
> Now, let us modify the reward functions to encourage the robot to track this 2D goal pose in the RewardsCfg:
> Pose Tracking Rewards
> Let's take a closer look at the position tracking rewards. We have two reward functions that encourage the robot to track the goal position:
> position_tracking rewards the robot for starting to move in the right direction to minimize the position error
> position_tracking_fine_grained is a stronger reward, that encourages tracking the goal position more precisely
> These two reward functions are plotted below (with the default 1.0 weight)
> We have another orientation_tracking reward that encourages the robot to minimize the yaw angle error.
> Exercise: Improving the PoseTracking task config:
> Open the task config file: source/unitree_rl_lab/unitree_rl_lab/tasks/locomotion/robots/g1_23dof/pose_tracking/pose_tracking_env_cfg.py
> Modify, add, or remove reward functions from the RewardsCfg class, it will look like this:
> @configclass
> class RewardsCfg:
> """Reward terms for the MDP."""
> # === Pose tracking rewards ===
> position_tracking = RewTerm(
> func=mdp.position_command_error_tanh,
> weight=5.0,
> params={"std": 2.0, "command_name": "pose_command"},
> )
> position_tracking_fine_grained = RewTerm(
> func=mdp.position_command_error_tanh,
> weight=20.0,
> params={"std": 0.2, "command_name": "pose_command"},
> )
> orientation_tracking = RewTerm(
> func=mdp.heading_command_error_abs,
> weight=-10.0,
> params={"command_name": "pose_command"},
> )
> # OTHER REWARD FUNCTIONS
> Creating a new reward function:
> Define the new reward function in: source/unitree_rl_lab/unitree_rl_lab/tasks/locomotion/mdp/rewards.py
> def new_reward_function(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg) -> torch.Tensor:
> """
> This reward function is the best one! Follow other examples in this file to implement your own reward functions.
> """
> asset: Articulation = env.scene[asset_cfg.name] # Access the robot articulation data
> y = asset.data.projected_gravity_b[:, 1]
> return torch.abs(y)  # The returned tensor has a shape of (num_envs,), where num_envs is the number of parallel robots in the training batch.
> To apply this reward, define a reward term RewTerm() in RewardsCfg() class in pose_tracking_env_cfg.py:
> @configclass
> class RewardsCfg:
> """Reward terms for the MDP."""
> # ...
> # OTHER REWARD FUNCTIONS
> # ...
> new_reward_term = RewTerm(
> func=mdp.new_reward_function,
> weight=1.0, # + for positive reward, - for penalty
> params={
> "asset_cfg": SceneEntityCfg("robot"), # Pass the asset_cfg used for robot articulation data
> },
> )
> To start training your modified PoseTracking task, use this command:
> ./unitree_rl_lab.sh -t --task Unitree-G1-23dof-PoseTracking
> Check your WandB isaaclab Project for the new run. They are named by default as <DATE>_<TIME> in YYYY-MM-DD_hh-mm-ss format.
> The Train/mean_reward aggregates all of the rewards into a single number. We want to see a positive trend in the mean reward like in the green plot.
> If you see mean reward decreasing like in the red plot, there is something wrong in the reward terms. For example:
> One of the reward function has a negative reward that is too large, and it preventing the robot from learning.
> Maybe the reward function itself is incorrectly defined
> Creating your own experiment logs
> Reinforcement Learning involves a lot of trial and error. You may end up changing many different reward weights and add/remove rewards altogether.
> To keep track of what changes you are doing for each experiment in WandB, you can add a markdown text block.
> Click on + Add panels, then Text and code, and then Code to add a markdown panel.
> Here are what my experiment logs look like (maybe they can help you!)
> 2026-03-18_17-13-05 based on commit "Fixes deploy cfg..." (dc90e3db13963d38676edac38aedef17322d8944)
> Reduces weights for flat_orientation, gait, feet_slide, and feet_clearance from 10.0 to 1.0
> Increases gait threshold from 0.55 to 0.6
> 2026-03-18_18-08-36 resumes from episode 1000:
> Reduces joint_deviation_hip_roll from -0.5 to -0.1
> Reduces joint_deviation_hip_yaw from -1.5 to -0.5
> Increases feet_clearance from 1.0 to 5.0 and target_height from 0.1 to 0.15
> 2026-03-18_18-15-58 resumes from episode 1100:
> Increases position_tracking_fine_grained from 5.0 to 15.0
> 2026-03-19_09-56-10 starts over:
> Increases joint_deviation_hip_roll from -0.1 to -0.25
> Increases gait, feet_slide, and feet_clearance from 1.0 to 5.0
> Increases flat_orientationfrom -1.0 to -10.0
> Increases base_ang_vel_xy from -1.0 to -5.0
> Increases action_rate from -0.05 to -0.1
> Notes:
> Robot is hopping with both feet when moving forward
> Robot is having trouble turning to track orientation, maybe competing rewards
> 2026-03-19_11-22-17 resumes from episode 900:
> Reduces base_ang_vel_xy from -5.0 to -1.0
> Reduces flat_orientation from -10.0 to -5.0
> Increases joint_acc from -1e-7 to -1e-6
> Changes to gait:
> Sets command_name: None
> Reduces threshold from 0.6 to 0.55 (20% double-support phase overlap is too much)
> Adds feet_air_time reward with 0.5 and threshold: 0.3
> 2026-03-19_12-15-25 starts over:
> Increases flat_orientation from -5.0 to -10.0
> Increases feet_air_time from 0.5 to 5.0
> Removes feet_clearance (likely causing hopping behavior)
> 2026-03-19_13-04-35 starts over:
> Reduces feet_air_time from 5.0 to 2.0
> Adds hopping_penalty with -100.0
> Increases curriculum success_threshold from 0.5 to 0.8 (was increasing too fast)
> 2026-03-19_14-27-34 starts over:
> Increases gait from 5.0 to 10.0
> Increases feet_air_time from 2.0 to 5.0
> Increases orientation_tracking from -5.0 to -10.0
> Increases hip_yaw_joint_deviation from -0.5 to -2.0
> 2026-03-19_15-53-59 starts over:
> Increases joint_deviation_arms from -1.0 to -5.0
> Adds leg_joint_avg_deviation = -0.1 to stop limping behavior
> 2026-03-19_16-30-15 starts over:
> Removes leg_joint_avg_deviation and adds feet_asymmetry = -1.0
> Playing you trained policy
> To stop your training run, simply Ctrl + C in the terminal. The log files are saved both locally in logs/rsl_rl/unitree_g1_23dof_posetracking and on WandB.
> When you are ready to play your trained policy in IsaacLab, use this command:
> ./unitree_rl_lab.sh -p --task Unitree-G1-23dof-PoseTracking --run_path <RUN_PATH>
> You can copy your Run path from WandB like this:
> For example, one of my run paths is: robertogroza1/isaaclab/9cv98wlv
> Once IsaacSim launches you will see something like this:
> After IsaacSim launches you should see this in your terminal. The policy.pt and policy.onnx gets generated in the /exported diretory and are automatically uploaded to WandB:
> Sim-to-Sim: Deploying and testing in Mujoco
> Now it is time to validate the policy by transferring it from IsaacSim to Mujoco. The reason that we do this is that IsaacSim is optimized for parallelized RL training on a GPU while Mujoco has a better physics engine that is closer to reality, allowing us to validate our trained policies.
> We will use a script to automatically deploy your trained policy. This is how it works:
> It pulls your policy from WandB, specifically: policy.onnx and deploy.yaml
> It creates a new directory in the deploy section of the repo called: deploy/robots/g1_23dof/config/policy/pose_tracking/<RUN_NAME>
> It adds the new policy to the config.yaml, using the keypress that you assign it to activate the policy
> Run this command using the same <RUN_PATH> that you copied from WandB:
> python scripts/deploy_policy.py --run_path <RUN_PATH> --policy_type pose_tracking
> You will be prompted to enter a new keypress (it must be alphanumeric!). This is the key that you will use in Mujoco to activate the policy. You should see this output and the new directory created in your repo.
> WHY TIME
> Why do we need /deploy_policy.py ?
> To understand this, we need to understand the program that will be launched for swapping between policies: g1_ctrl
> In essence, to swap between policies without falling, we need a program that manages the transitions safely.
> g1_ctrl has all the policies defined inside the config.yaml
> config.yaml FILE
> all_transitions: &all_transitions
> Passive: key_z.on_pressed
> FixStand: key_x.on_pressed
> NavigationPIDv1: RB + X.on_pressed
> 2026-04-07_10-35-55: key_u.on_pressed
> FSM:
> enable_keyboard: true  # Enable keyboard input for FSM transitions
> _: # enabled fsms
> Passive:
> id: 1
> FixStand:
> id: 2
> NavigationPIDv1:
> id: 101
> type: NavigationPID
> 2026-04-07_10-35-55:
> id: 102
> type: RLBase
> Passive:
> transitions: *all_transitions
> mode: [
> 1,1,1,1,1,1,
> 1,1,1,1,1,1,
> 1,1,1,
> 1,1,1,1,1,1,1,
> 1,1,1,1,1,1,1,
> ]
> kd: [
> 3,3,3,3,3,3,
> 3,3,3,3,3,3,
> 3,3,3,
> 3,3,3,3,3,3,3,
> 3,3,3,3,3,3,3,
> ]
> FixStand:
> transitions: *all_transitions
> kp: [
> - 100., 100., 100., 150., 40., 40.,
> - 100., 100., 100., 150., 40., 40.,
> 200,200,200,
> 40,40,40,40,40,40,40,
> 40,40,40,40,40,40,40,
> ]
> kd: [
> 2,2,2,4,2,2,
> 2,2,2,4,2,2,
> 5,5,5,
> 10,10,10,10,10,10,10,
> 10,10,10,10,10,10,10,
> ]
> ts: [0, 3]
> qs: [
> [],
> [ -0.1, 0,0,0.3,-0.2,0,
> -0.1, 0,0,0.3,-0.2,0,
> 0,0,0,
> 0, 0.25,0,0.97,0.15, 0,0,
> 0, -0.25,0,0.97,-0.15, 0,0
> ]
> ]
> NavigationPIDv1:
> transitions: *all_transitions
> policy_dir: config/policy/velocity/v2.6
> goal_pose_topic: rt/goal_pose
> pid_gains:
> kp_x: 5.0
> kp_y: 5.0
> kp_yaw: 10.0
> # debug_print: true
> 2026-04-07_10-35-55:
> transitions: *all_transitions
> policy_dir: config/policy/velocity/2026-04-07_10-35-55
> So in order for this to work, it's the deploy_policy.py that does three things: 1) DOWNLAODS the policy form WAND 2) Puts the downloaded files into the unitree_rl_lab/deploy/robots/g1_23dof/config/policypath . 3) **Edits** theconfig.yamlfor the new policy in **three** distinct places. Let's see the example above for the policy2026-04-07_10-35-55`.
> all_transitions: &all_transitions
> Passive: key_z.on_pressed
> FixStand: key_x.on_pressed
> NavigationPIDv1: RB + X.on_pressed
> 2026-04-07_10-35-55: key_u.on_pressed
> Its added to the transitions tag, and assigned the key from the keyboard/Joystick that when pressed it will activate that policy. In this case, u ( key_u.on_pressed ) .
> Passive:
> id: 1
> FixStand:
> id: 2
> NavigationPIDv1:
> id: 101
> type: NavigationPID
> 2026-04-07_10-35-55:
> id: 102
> type: RLBase
> Here we add its id , in this case 102. Its whatever we want that is unique.
> 2026-04-07_10-35-55:
> transitions: *all_transitions
> policy_dir: config/policy/velocity/2026-04-07_10-35-55
> And here we add the policy info of our policy. In this case it transitions form ALL the other states and the policy has been copied inside the config/policy/velocity/2026-04-07_10-35-55.
> END WHY TIME
> Launching Mujoco and g1_ctrl
> Launch Mujoco in your terminal:
> cd ~/unitree_mujoco/simulate/build
> ./unitree_mujoco
> Launch g1_ctrl in another terminal:
> cd ~/unitree_rl_lab/deploy/robots/g1_23dof/build/
> ./g1_ctrl
> Activating the policy
> Here are the steps for lowering the robot to the ground and starting activating the policy. All of these keypress must be done while focused on the Mujoco window:
> Press 8 multiple times to lower the robot until it touches the ground with some pressure. Press 7 to raise up.
> Activate your policy using the same key that you configured (this can be found at the top of the the config.yaml, see the screenshot above)
> Press 9 to toggle the elastic tether on/off
> When the policy is activated, you will see:
> [2026-04-02 14:59:50.456] [info] FSM: Change state from Passive to NavigationPIDv1
> To move the robot around we have a couple of options:
> Press Right Alt (Alt Gr) on your keyboard. Mujoco will display a red sphere on the ground, which is the goal position we are sending to the policy.
> Press and hold Space to send a goal position and orientation. While holding Space, you can change the direction of the goal yaw angle.
> Evaluating pose tracking
> To evaluate your policy, first make sure that the policy is currently active. Then, press the E key to start the evaluation trajectory.
> Once the evaluation trajectory is finished, you will see a score summary that looks like this:
> ============== Trajectory Scoring Summary ===============
> Time Steps: 33055
> Position Error (2D):
> Average: 0.0348219 m
> Total:   1151.04 m
> Min:     1.6e-06 m
> Max:     0.101115 m
> Orientation Error (Yaw):
> Average: 1.65021 deg (0.0288016 rad)
> Total:   54547.7 deg (952.037 rad)
> Min:     0 deg (0 rad)
> Max:     7.34332 deg (0.128165 rad)
> =========================================================
> *** Your FINAL SCORE: 0.037702 (lower is better) ***
> =========================================================
> Take you best score (lowest number) and post it in the Google Spreadsheet next to your name. No cheating please!
> We will test the top 5 policies on the real robot with an ArUco marker!
> Unitree G1 Course
> - 2.3   BeyondMimic Motion Tracking Pipeline
> **Duration:** Estimated time to completion for the whole unit: 90 min
> **Objective:** earn how to apply HybridRobotics' BeyondMimic reinforcement learning training pipeline to train humanoid motion tracking policies, deploy them in simulation (sim2sim), and transfer them to real robots (sim2real).
> **Topics:**
> - 2.3.1 Introduction to BeyondMimic
> - 2.3.2 Pipeline Overview
> - 2.3.3 Part 1: Training with whole_body_tracking
> - 2.3.4 Motion Preprocessing & Registry Setup
> - 2.3.5 Policy Training
> - 2.3.6 Policy Evaluation
> - 2.3.7 Part 2: Deployment with motion_tracking_controller
> - 2.3.8 Setting Up the Docker Environment
> - 2.3.9 Sim2Sim: MuJoCo Simulation
> - 2.3.10 Sim2Real: Real Robot Deployment
> - 2.3.11 Code Structure and Key Components
> - 2.3.12 Best Practices and Tips

#### 2.3.1 Introduction to BeyondMimic
BeyondMimic is a versatile humanoid control framework developed by HybridRobotics that provides highly dynamic motion tracking with state-of-the-art motion quality on real-world deployment and steerable test-time control with guided diffusion-based controllers (guided diffusion still untested)

Key features:

Motion Tracking: Train policies to track any motion from datasets like LAFAN1

No Parameter Tuning Required: Works out-of-the-box for sim-to-real motion tracking

Isaac Lab Integration: Leverages Isaac Lab 2.1.0 for high-performance training

Modular Deployment: Separate training and deployment pipelines

Reference: Website | Arxiv | Video


#### 2.3.2 Pipeline Overview
The BeyondMimic pipeline is divided into two main components:

1. Training Phase: whole_body_tracking/

Training is performed on an NVIDIA GPU-equipped PC using Isaac Lab.

Environment: Isaac Lab 2.1.0 with Isaac Sim 4.5.0

Requirements: Python 3.10, NVIDIA GPU with CUDA support

Output: Trained ONNX policy files for deployment

2. Deployment Phase: motion_tracking_controller/

Deployment uses the legged_control2 framework.

Environment: ROS 2 Humble with legged_control2

Deployment Options: Sim2Sim (MuJoCo) and Sim2Real (Real Robot)

Inference: C++ implementation with ONNX CPU inference engine

Docker Support: Containerized environment for easy deployment


### Key Advantage: The separation allows training on powerful GPU workstations while deploying on resource-constrained systems.

#### 2.3.3 Part 1: Training with whole_body_tracking

### The training phase uses Isaac Lab to train motion tracking policies from reference motion data, and WandB for policy cloud upload.
Prerequisites

NVIDIA GPU with CUDA support

Ubuntu 20.04/22.04

Isaac Lab v2.1.0 installed

WandB account for motion registry and experiment tracking

Installation


### First, install Isaac Lab v2.1.0 following the official installation guide. We recommend using the conda installation method.
# Clone the repository (outside IsaacLab directory)

cd ~/git-repo

git clone https://github.com/HybridRobotics/whole_body_tracking.git

# Enter the repository

cd whole_body_tracking

# Download robot description files from GCS

curl -L -o unitree_description.tar.gz https://storage.googleapis.com/qiayuanl_robot_descriptions/unitree_description.tar.gz && \

tar -xzf unitree_description.tar.gz -C source/whole_body_tracking/whole_body_tracking/assets/ && \

rm unitree_description.tar.gz

# Install using Isaac Lab's Python environment

python -m pip install -e source/whole_body_tracking


#### 2.3.4 Motion Preprocessing & Registry Setup

### BeyondMimic uses WandB Registry to manage and load reference motions automatically. This allows for organized storage and easy access to motion datasets.
Motion Datasets

Supported motion datasets include:

LAFAN1: Available on HuggingFace (Unitree-retargeted)

Sidekicks: From KungfuBot

Celebrations: From ASAP

Balance Motions: From HuB

Important: Reference motions should be retargeted and use generalized coordinates only. The only dataset that can be used as-is is LAFAN1

Retargeting motions for whole_body_tracking


### Retargeting means adapting the motion you have (either a .pkl (python pickle: tuples) or .csv (excel) file) so it fits the available joint movements of the G1.
The BeyondMimic pipeline only accepts .csv files as inputs. The format is as follows:

No headers. Only numbers.


## 36 columns

### The first 7 columns are the "root joint", the pelvis position and orientation based on all of the joint configurations. Think of it as the base_link.
x, y, z, qx, qy, qz, qw

The next 29 columns are the G1 joints (for the 29 DoF version)

Since this robot only has 23 DoF, we set the following joint columns to 0.0:

waist_roll (column 12)

waist_pitch (column 13)

left_wrist_pitch (column 24)

left_wrist_yaw (column 25)

right_wrist_pitch (column 28)

right_wrist_yaw (column 29)


### We assume that BeyondMimic only takes 29 joints, that's why we replace above columns with zeros. We haven't tried deleting them altogether.
We'll retarget PBHC's Horse-stance_punch.pkl. In this example dataset, each .pkl contains:

root_trans: Root translation (3D position)

root_rot: Root rotation as quaternion (qx, qy, qz, qw)

dof: Joint angles for all degrees of freedom

fps: Frame rate (typically 30 FPS)

See the conversion script here. All we are doing is extracting the required raw data BeyondMimic requires and putting it in a .csv:

cd beyondmimic/

python3 convert_pbhc_to_g1_fixed.py

Motion safety considerations


### These reinforcement learning pipelines must be executed while the robot is in debug mode. This means that when the trained movement finishes, the robot will just fall to the ground. BeyondMimic has implemented a clever "standing safe pose" with ROS 2 control that you can switch into/out of, but to be even safer, we'll include a standing phase of 1 minute after the motion is completed.

### To do that, we just copy and paste the last position for a bunch of lines (I expanded it from line 200 to line 2000 just to be safe!) This means that the training will include a whole minute or so where the robot is doing nothing, enough time to safely hook the robot back in its crane.
The extended motion file horse_stance_punch_with_standing.csv is here.

Setting Up WandB Registry

Create Registry Collection:

Access WandB web interface

Navigate to Registry under Core (left sidebar)

Create a new collection named "Motions" with artifact type "All Types"

Converting Motion Files

Convert retargeted CSV motions to NPZ format with maximum coordinates information:

# Convert motion to NPZ and upload to WandB registry

python scripts/csv_to_npz.py \

--input_file /path/to/motion.csv \

--input_fps 30 \

--output_name motion_name \

--headless

Verifying Motion Registry

Test that the WandB registry works by replaying the motion in Isaac Sim:

# Replay motion from registry

python scripts/replay_npz.py \

--registry_name=your-organization-org/wandb-registry-motions/motion_name

Troubleshooting:

Make sure WANDB_ENTITY is set to your organization name, not username


#### 2.3.5 Policy Training
Once motions are uploaded to the WandB registry, you can train policies to track them.

Basic Training Command

# Train policy for G1 robot on flat terrain

python scripts/rsl_rl/train.py --task=Tracking-Flat-G1-v0 --registry_name {your-username}-org/wandb-registry-motions/horse_stance_punch_with_standing --headless --logger wandb --log_project_name horse_stance_punch_with_standing --run_name run1_horse_stance_punch_with_standing --max_iterations 30000

Training Parameters

Training Progress

During training, you'll see metrics in the console and WandB dashboard:

Mean Reward: DeepMimic reward indicating pose tracking quality

Episode Length: How long the robot maintains stable tracking

Policy/Value Loss: Neural network optimization metrics

FPS: Training simulation speed

No Tuning Required: BeyondMimic is designed to work out-of-the-box for LAFAN1 motions without parameter tuning!


#### 2.3.6 Policy Evaluation
After training, evaluate the policy in Isaac Sim to visualize performance.

# Play trained policy

python scripts/rsl_rl/play.py \

--task=Tracking-Flat-G1-v0 \

--num_envs=2 \

--wandb_path=your_organization/project_name/run_id

Finding the WandB Path:

Go to your WandB project

Click on the run

Find the path in the run overview (format: organization/project_name/run_id)

Note: run_name is different from run_path


#### 2.3.7 Part 2: Deployment with motion_tracking_controller

### The deployment phase uses ROS 2 Humble and the legged_control2 framework to run trained policies in simulation or on real robots.
Key Features

C++ Implementation: Fast inference using ONNX CPU engine

Metadata Storage: Joint order, impedance, and other parameters stored in ONNX

Reference Motion: Returned via the forward() function

Framework Example: Serves as a template for custom legged_control2 controllers


#### 2.3.8 Setting Up the Docker Environment
For easy deployment on most PCs, a Docker container is provided with all dependencies pre-installed.

Docker Setup

The Dockerfile and docker-compose.yaml are located here.

# docker-compose.yaml

services:

ros_humble_beyondmimic:

image: theconstructai/ros-humble-beyondmimic

container_name: ros_humble_beyondmimic

environment:


## - DISPLAY=$DISPLAY

## - ROS_DOMAIN_ID=0
volumes:

- /tmp/.X11-unix:/tmp/.X11-unix:rw

privileged: true

network_mode: "host"

devices:

- /dev/dri:/dev/dri  # GPU access (if available) for visualization

Building and Running the Container

# Navigate to the docker directory

cd ~/git-repo/beyondmimic

# Build the Docker image

docker compose build

# Start the container

docker compose up -d

# Enter the container

docker exec -it ros_humble_beyondmimic bash

What's Included in the Docker Image

Base: ROS 2 Humble Desktop Full

legged_control2: Core control framework

MuJoCo ROS 2: For sim2sim deployment

Unitree Packages: Robot descriptions and hardware interfaces

motion_tracking_controller: Pre-built and ready to use

WandB: For downloading trained policies


#### 2.3.9 Sim2Sim: MuJoCo Simulation
Test your trained policy in MuJoCo simulation before deploying to the real robot.

Loading Policy from WandB

# Inside the Docker container

ros2 launch motion_tracking_controller mujoco.launch.py \

wandb_path:=your_organization/project_name/run_id

Loading Policy from Local File

# Use absolute path or ~ prefix

ros2 launch motion_tracking_controller mujoco.launch.py \

policy_path:=~/path/to/policy.onnx

Launch Parameters

Note: You can specify either wandb_path or policy_path, but not both.


#### 2.3.10 Sim2Real: Real Robot Deployment

> **⚠️ Note:** ⚠️ Disclaimer: Running these models on real robots is dangerous and entirely at your own risk. They are provided for research only, and we accept no responsibility for any harm, damage, or malfunction.
Hardware Setup

Connect to the robot via ethernet cable

Use ifconfig to find the network interface (e.g., eth0, enp3s0)

Ensure the robot is in debug mode

Launching on Real Robot

# Find network interface

ip -c a

# Launch with WandB policy

ros2 launch motion_tracking_controller real.launch.py \

network_interface:=enp3s0 \

wandb_path:=your_organization/project_name/run_id

# OR launch with local policy

ros2 launch motion_tracking_controller real.launch.py \

network_interface:=enp3s0 \

policy_path:=~/path/to/policy.onnx

Controller Switching with Unitree Remote

The robot starts in standby controller mode. Use the Unitree joystick to switch controllers:


### Safety First: Always be ready to press B for emergency stop. Start with simple motions and gradually increase complexity.
Data Logging

The real robot launch file automatically records rosbags:

Format: MCAP

Topics: All topics except Unitree internal topics

Location: Current directory

# Rosbag is automatically recorded during real robot experiments

# To replay:

ros2 bag play rosbag2_YYYY_MM_DD-HH_MM_SS


#### 2.3.11 Code Structure and Key Components
Understanding the code structure helps when customizing or debugging the pipeline.

Training Code Structure (whole_body_tracking)

whole_body_tracking/

├── source/whole_body_tracking/whole_body_tracking/

│   ├── tasks/tracking/mdp/

│   │   ├── commands.py          # Reference motion processing

│   │   ├── rewards.py           # DeepMimic reward functions

│   │   ├── observations.py      # Observation terms

│   │   ├── events.py            # Domain randomization

│   │   └── terminations.py      # Early termination conditions

│   ├── tasks/tracking/

│   │   └── tracking_env_cfg.py  # Environment configuration

│   ├── tasks/tracking/config/g1/agents/

│   │   └── rsl_rl_ppo_cfg.py    # PPO hyperparameters

│   └── robots/                   # Robot-specific settings

└── scripts/

├── csv_to_npz.py             # Motion preprocessing

├── replay_npz.py             # Motion replay

└── rsl_rl/

├── train.py              # Training script

└── play.py               # Evaluation script

Deployment Code Structure (motion_tracking_controller)

motion_tracking_controller/

├── include/ & src/

│   ├── MotionTrackingController  # Main controller class

│   ├── MotionOnnxPolicy          # Neural network wrapper

│   └── MotionCommand             # Observation management

├── launch/

│   ├── mujoco.launch.py          # Sim2Sim launch file

│   ├── real.launch.py            # Sim2Real launch file

│   └── wandb.launch.py           # WandB downloader

└── config/

└── g1/

└── controllers.yaml      # Controller parameters

Key Components Explained

MotionTrackingController

Manages the observation space (similar to an RL environment) and passes observations to the policy.

MotionOnnxPolicy


### Wraps the neural network, runs ONNX inference, and extracts reference motion. Model parameters (joint order, impedance) are stored in ONNX metadata.
MotionCommand

Defines observation terms aligned with the training code to ensure sim2real consistency.


### Template Project: This repository serves as an excellent example for creating custom legged_control2 controllers. See legged_template_controller for a minimal starting point.

#### 2.3.12 Best Practices and Tips
Training Tips

Motion Selection: Start with simple walking motions before attempting complex acrobatics

Headless Mode: Always use --headless for faster training

WandB Logging: Use WandB to track experiments and compare different runs

GPU Usage: Monitor GPU memory with nvidia-smi during training

Training Time: Most motions converge within 10-50 million steps

Deployment Tips

Test in Sim First: Always validate in MuJoCo before real robot deployment

Network Check: Verify ethernet connection with ping 192.168.123.161

Policy Files: Keep local backups of ONNX files, don't rely solely on WandB

Docker Volumes: Mount local directories to persist data outside containers

ROS Domain ID: Use unique ROS_DOMAIN_ID to avoid conflicts with other robots

Safety Considerations

Clear Space: Ensure adequate space around the robot

Emergency Stop: Keep the remote control within reach at all times

Gradual Testing: Test incrementally: standby → simple motion → complex motion

Monitoring: Watch joint temperatures and motor currents

Backup Plan: Have a recovery procedure ready

Common Issues and Solutions

Issue: Cannot connect to robot

Check ethernet cable connection

Verify static IP configuration (192.168.123.11)

Ensure robot is powered on and in debug mode

Try ping 192.168.123.161 to test connectivity

Issue: Policy not found in WandB

Check WANDB_ENTITY is set to organization name

Verify wandb_path format: org/project/run_id

Ensure you're logged in: wandb login

Check registry permissions

Issue: MuJoCo simulation crashes

Check GPU driver compatibility

Verify X11 forwarding is working (xhost +local:docker)

Try reducing number of environments

Check ONNX file is not corrupted

Complete Example Pipeline

#!/bin/bash

# Complete BeyondMimic pipeline example

# ====================


## # PART 1: TRAINING
# ====================

# Setup WandB

export WANDB_ENTITY=your-organization

wandb login

# Convert and upload motion

cd ~/git-repo/whole_body_tracking

python scripts/csv_to_npz.py \

--input_file ~/motions/walking.csv \

--input_fps 30 \

--output_name walking_motion \

--headless

# Verify motion

python scripts/replay_npz.py \

--registry_name=your-organization-org/wandb-registry-motions/walking_motion

# Train policy

python scripts/rsl_rl/train.py \

--task=Tracking-Flat-G1-v0 \

--registry_name your-organization-org/wandb-registry-motions/walking_motion \

--headless \

--logger wandb \

--log_project_name g1_tracking \

--run_name walking_v1

# Evaluate policy

python scripts/rsl_rl/play.py \

--task=Tracking-Flat-G1-v0 \

--num_envs=2 \

--wandb_path=your-organization/g1_tracking/abc12345

# ====================


## # PART 2: DEPLOYMENT
# ====================

# Start Docker container

cd ~/git-repo/beyondmimic

docker compose up -d

docker exec -it ros_humble_beyondmimic bash

# Test in MuJoCo

ros2 launch motion_tracking_controller mujoco.launch.py \

wandb_path:=your-organization/g1_tracking/abc12345

# Deploy to real robot (after sim validation)

ros2 launch motion_tracking_controller real.launch.py \

network_interface:=enp3s0 \

wandb_path:=your-organization/g1_tracking/abc12345


### Congratulations! You now understand the complete BeyondMimic pipeline from motion preprocessing to real robot deployment. You can train motion tracking policies in Isaac Lab and deploy them efficiently using the legged_control2 framework.

### What's next? In the next unit, you will learn about the ROS 2 control infrastructure BeyondMimic uses.

---

**Next:** Unit 3 — Subsection 4: Understanding ros2_control Architecture in BeyondMimic

# Unitree G1 Reinforcement Learning Course


### 2.4   Understanding ros2_control Architecture in BeyondMimic
> **Duration:** Estimated time to completion for the whole unit: 30 min
> **Objective:** nderstand how trained neural network policies execute through ros2_control framework to command the real robot hardware, including the complete data flow from policy inference to motor commands.
> **Topics:**
> - 2.4.1 Introduction to ros2_control
> - 2.4.2 The Real-Time Control Loop
> - 2.4.3 Hardware Interface Configuration
> - 2.4.4 The UnitreeSdk2 Hardware Interface
> - 2.4.5 Complete Data Flow: Policy to Motors
> - 2.4.6 Why ros2_control for Policy Execution?
> - 2.4.7 Launch File Architecture
> - 2.4.8 Controller Management

#### 2.4.1 Introduction to ros2_control
A common question when looking at the BeyondMimic deployment architecture is: "How does the trained policy actually move the robot? Where are the motor commands published?"


### The answer lies in understanding that policy execution happens entirely through ros2_control, not through traditional ROS topics. This is a fundamental architectural choice that provides real-time performance and deterministic behavior.
Key Insight

ros2_control uses direct C++ function calls instead of ROS topics for the real-time control loop. This provides:

Speed: Function calls are ~1000x faster than ROS topics (nanoseconds vs microseconds)

Determinism: No network stack, no serialization overhead

Real-time Safety: Direct memory access, no dynamic allocation

Reference: ros2_control Documentation | legged_control2 Documentation


#### 2.4.2 The Real-Time Control Loop
At the heart of ros2_control is a simple, high-frequency control loop that runs at 200-500 Hz:

Simplified Control Loop

// ros2_control_node runs this loop at ~200-500 Hz

while(running) {

hardware_interface->read();        // Get joint states via Unitree SDK2

walking_controller->update();      // Your policy computes actions

hardware_interface->write();       // Send commands via Unitree SDK2

}

The Complete Architecture Stack

Here's how all the components fit together:

┌─────────────────────────────────────────────────────────────────┐

│                    Your Trained Policy                          │

│                  (ONNX/PyTorch Neural Network)                  │

└────────────────────────────┬────────────────────────────────────┘

│

↓

┌─────────────────────────────────────────────────────────────────┐

│              MotionTrackingController                           │

│              (ros2_control Controller)                          │

│                                                                 │

│   update() {                                                    │

│     observations = read_state_interfaces()    ← Direct memory  │

│     actions = policy.forward(observations)                      │

│     write_command_interfaces(actions)         → Direct memory  │

│   }                                                             │

└────────────────────────────┬────────────────────────────────────┘

│ (C++ function calls)

↓

┌─────────────────────────────────────────────────────────────────┐

│              UnitreeSdk2 Hardware Interface                     │

│              (ros2_control SystemInterface)                     │

│                                                                 │

│   read() {                                                      │

│     state_interfaces = robot.getState()     ← Unitree SDK2 DDS │

│   }                                                             │

│                                                                 │

│   write() {                                                     │

│     robot.sendCommand(commands)             → Unitree SDK2 DDS │

│   }                                                             │

└────────────────────────────┬────────────────────────────────────┘

│ (DDS over network_interface)

↓

┌─────────────────────────────────────────────────────────────────┐

│                    G1 Robot Hardware                            │

│                    (Motor Controllers)                          │

└─────────────────────────────────────────────────────────────────┘


### Key Point: Notice there are NO ROS topics in the critical control path. Everything happens through direct function calls for maximum performance.

#### 2.4.3 Hardware Interface Configuration

### The hardware interface is defined in the robot's URDF files using the ros2_control tag. Let's look at the actual configuration files used in BeyondMimic.
1. Hardware Interface Definition (real.xacro)

Located at: /opt/ros/humble/share/unitree_description/urdf/g1/real.xacro

<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

<xacro:include filename="$(find unitree_description)/urdf/g1/ros2_control.xacro"/>

<xacro:arg name="network_interface" default=""/>

<ros2_control name="UnitreeSdk2" type="system">

<hardware>

<plugin>unitree/UnitreeSdk2</plugin>

<param name="network_interface">$(arg network_interface)</param>

</hardware>

<xacro:hardware_interface/>

</ros2_control>

</robot>

Key Components Explained

2. Joint Interface Configuration (ros2_control.xacro)

Located at: /opt/ros/humble/share/unitree_description/urdf/g1/ros2_control.xacro

Each joint exposes command and state interfaces:

<xacro:macro name="joint_interface" params="name initial_pos kp:=80 kd:=3">

<joint name="${name}">

<!-- Command interfaces: What the controller can write -->

<command_interface name="stiffness">

<param name="initial_value">${kp}</param>

</command_interface>

<command_interface name="damping">

<param name="initial_value">${kd}</param>

</command_interface>

<!-- State interfaces: What the controller can read -->

<state_interface name="position">

<param name="initial_value">${initial_pos}</param>

</state_interface>

</joint>

</xacro:macro>

Interface Types

Command Interfaces (Controller → Hardware):

stiffness: PD controller position gain (kp)

damping: PD controller velocity gain (kd)

State Interfaces (Hardware → Controller):

position: Current joint angle (read from encoders)

velocity: Current joint velocity (derived)

torque: Current motor torque (from current sensors)

The hardware interface also includes an IMU sensor:

<sensor name="base_imu">

<state_interface name="orientation.x"/>

<state_interface name="orientation.y"/>

<state_interface name="orientation.z"/>

<state_interface name="orientation.w"/>

<state_interface name="angular_velocity.x"/>

<state_interface name="angular_velocity.y"/>

<state_interface name="angular_velocity.z"/>

<state_interface name="linear_acceleration.x"/>

<state_interface name="linear_acceleration.y"/>

<state_interface name="linear_acceleration.z"/>

</sensor>


#### 2.4.4 The UnitreeSdk2 Hardware Interface

### The UnitreeSdk2 class is the C++ implementation that bridges ros2_control and the Unitree robot hardware.
Class Definition

Located at: /opt/ros/humble/include/unitree_systems/UnitreeSdk2.h

class UnitreeSdk2 : public hardware_interface::SystemInterface {

public:

// Lifecycle methods

CallbackReturn on_init(const hardware_interface::HardwareInfo& info) override;

// Interface export methods

std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;


## // THE CRITICAL REAL-TIME METHODS:
hardware_interface::return_type read(

const rclcpp::Time& time,

const rclcpp::Duration& period) override;

hardware_interface::return_type write(

const rclcpp::Time& time,

const rclcpp::Duration& period) override;

private:

void lowStateHandler(const void* message);  // Receives from robot

void lowCommandWriter();                    // Sends to robot

// DDS communication channels

ChannelPublisherPtr<LowCmd_> lowcmd_publisher_;      // → Robot

ChannelSubscriberPtr<LowState_> lowstate_subscriber_; // ← Robot

ChannelSubscriberPtr<IMUState_> imutorso_subscriber_; // ← Robot

// Data storage

UnitreeMotorData jointData_[G1_NUM_MOTOR]{};  // Joint state/command

UnitreeImuData imuData_{};                     // IMU data

};

Critical Methods Explained

1. read() Method

Called by ros2_control at the start of each control loop iteration:

Receives latest robot state via DDS (Unitree SDK2)

Updates jointData_[] with joint positions, velocities, torques

Updates imuData_ with IMU measurements

Makes data available to controllers via state interfaces

2. write() Method

Called by ros2_control at the end of each control loop iteration:

Reads desired commands from controller via command interfaces

Packages commands into Unitree SDK2 format

Sends commands to robot via DDS

Commands include position targets, kp, kd for each joint


### DDS Communication: The Unitree SDK2 uses DDS (Data Distribution Service) for high-speed, real-time communication with the robot. The network_interface parameter specifies which network adapter to use.

#### 2.4.5 Complete Data Flow: Policy to Motors
Let's trace a single control cycle from policy inference to motor commands:

Step-by-Step Flow

┌─────────────────────────────────────────────────────────────────┐

│ STEP 1: Hardware Interface Reads Robot State                   │

└─────────────────────────────────────────────────────────────────┘

G1 Robot → DDS → UnitreeSdk2::lowStateHandler()

→ Updates jointData_[29] positions

→ Updates imuData_ orientation/velocity

→ UnitreeSdk2::read() exposes via state_interfaces

┌─────────────────────────────────────────────────────────────────┐

│ STEP 2: Controller Reads States                                │

└─────────────────────────────────────────────────────────────────┘

MotionTrackingController::update()

→ Calls read_state_interfaces()

→ Gets: joint_pos[29], joint_vel[29], imu_quat[4], imu_ang_vel[3]

→ Builds observation vector

┌─────────────────────────────────────────────────────────────────┐

│ STEP 3: Policy Inference                                       │

└─────────────────────────────────────────────────────────────────┘

MotionOnnxPolicy::forward(observations)

→ ONNX Runtime inference (CPU)

→ Neural network forward pass (~1-2 ms)

→ Returns: action[29] (desired joint positions)

┌─────────────────────────────────────────────────────────────────┐

│ STEP 4: Controller Writes Commands                             │

└─────────────────────────────────────────────────────────────────┘

MotionTrackingController::update()

→ Processes policy output

→ Calls write_command_interfaces()

→ Sets: joint_position_cmd[29], stiffness[29], damping[29]

┌─────────────────────────────────────────────────────────────────┐

│ STEP 5: Hardware Interface Sends Commands                      │

└─────────────────────────────────────────────────────────────────┘

UnitreeSdk2::write()

→ Reads from command_interfaces

→ Packages into LowCmd format

→ lowCommandWriter() → DDS → G1 Robot Motors

Total latency: ~2-5 ms (including DDS communication)

Timing Diagram

Time →

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

│←────── 5ms @ 200Hz ────→│←────── 5ms @ 200Hz ────→│

│                         │                         │

Hardware │  read()                 │  read()                 │

↓      │    ↓                    │    ↓                    │

Controller│  update()               │  update()               │

│   ├─ observations       │   ├─ observations       │

Policy   │   ├─ forward()          │   ├─ forward()          │

│   └─ actions            │   └─ actions            │

│    ↓                    │    ↓                    │

Hardware │  write()                │  write()                │

│    ↓                    │    ↓                    │

Robot    │  Motors execute         │  Motors execute         │

│                         │                         │


### Performance: The entire cycle from sensor reading to motor command takes only 2-5 milliseconds, enabling smooth, dynamic locomotion at 200 Hz.

#### 2.4.6 Why ros2_control for Policy Execution?
You might wonder: Why use ros2_control instead of just publishing to ROS topics? Here are the key advantages:

1. Real-Time Performance

2. Hardware Abstraction

Same controller code works in simulation (MuJoCo) and on real hardware

Just swap the hardware interface plugin

No changes needed to policy or controller logic

3. Safety Features

Joint Limits: Automatic enforcement of position/velocity/torque limits

Emergency Stops: Built-in e-stop handling

Controller Switching: Safe transitions between controllers

Watchdog Timers: Automatic safety mode if controller fails

4. Ecosystem Integration

Compatible with standard ROS 2 tools (ros2 control CLI)

Works with controller manager for runtime switching

Integrates with diagnostic tools

Supports multiple robots and controller types


### Important: ROS topics are still used for non-realtime tasks like visualization (/joint_states), commands (/cmd_vel), and sensor data (/camera/image). The ros2_control loop only handles time-critical motor commands.

#### 2.4.7 Launch File Architecture
Let's examine how real.launch.py sets up the entire ros2_control system:

Key Components in real.launch.py

# 1. Generate robot description with hardware interface

robot_description_command = Command([

PathJoinSubstitution([FindExecutable(name='xacro')]),

" ",

PathJoinSubstitution([

FindPackageShare("unitree_description"),

"urdf", "g1", "robot.xacro"

]),

" ", "robot_type:=", robot_type,

" ", "simulation:=", "false",

" ", "network_interface:=", network_interface  # ← DDS network config

])

# 2. Launch ros2_control_node

control_node = Node(

package="controller_manager",

executable="ros2_control_node",

parameters=[robot_description, LaunchConfiguration('controllers_yaml')],

output="both",

respawn=True,  # Auto-restart if crashes

)

# 3. Dynamically inject policy path into controller config

def setup_controllers(context):

policy_path_value = LaunchConfiguration('policy_path').perform(context)

kv_pairs = []

if policy_path_value:

abs_path = os.path.abspath(os.path.expanduser(policy_path_value))

kv_pairs.append(('walking_controller.policy.path', abs_path))

# Generate temporary config with policy path

temp_config = generate_temp_config(

'config/g1/controllers.yaml',

'motion_tracking_controller',

kv_pairs

)

return [set_controllers_yaml, active_spawner, inactive_spawner]

# 4. Spawn controllers

active_list = ["state_estimator", "standby_controller"]

inactive_list = ["walking_controller"]  # Starts inactive for safety

active_spawner = control_spawner(active_list)

inactive_spawner = control_spawner(inactive_list, inactive=True)

Launch Sequence

1. Parse URDF with xacro

├─ Includes UnitreeSdk2 hardware interface

├─ Configures network_interface parameter

└─ Defines all joint command/state interfaces

2. Start ros2_control_node

├─ Loads UnitreeSdk2 hardware interface plugin

├─ Initializes DDS communication

├─ Starts real-time control loop

└─ Waits for controllers

3. Spawn Controllers

├─ state_estimator (ACTIVE)

│  └─ Estimates robot pose/velocity from IMU + joints

├─ standby_controller (ACTIVE)

│  └─ Safe joint position control mode

└─ walking_controller (INACTIVE)

└─ Loads policy, ready to activate via joystick

4. Start Additional Nodes

├─ robot_state_publisher (publishes TF tree)

├─ rosbag2 (records data)

└─ teleop (joystick interface)


#### 2.4.8 Controller Management
ros2_control allows runtime switching between controllers for safe operation.

Available Controllers

Switching Controllers

Via Unitree Joystick:

L1 + A: Activate standby_controller (safe mode)

R1 + A: Activate walking_controller (policy execution)

B: Emergency stop (damping mode)

Via ROS 2 CLI:

# List all controllers

ros2 control list_controllers

# Switch to walking controller

ros2 service call /controller_manager/switch_controller \

controller_manager_msgs/srv/SwitchController \

"{activate_controllers: ['walking_controller'], \

deactivate_controllers: ['standby_controller']}"

# Get controller state

ros2 control list_controllers | grep walking_controller

Controller Lifecycle

┌─────────────┐


## │  UNCONFIGURED│
└──────┬───────┘

│ configure()

↓

┌─────────────┐

│  INACTIVE   │  ← walking_controller starts here

└──────┬───────┘

│ activate()

↓

┌─────────────┐

│   ACTIVE    │  ← Policy execution happens here

└──────┬───────┘  ← update() called at 200 Hz

│ deactivate()

↓

┌─────────────┐


## │  INACTIVE   │
└─────────────┘


### Safety: The walking_controller starts in INACTIVE state by design. This prevents the policy from running immediately on launch, giving you time to prepare and activate it deliberately via the joystick.
What ROS Topics ARE Used For

While the control loop doesn't use topics, ROS topics are still important for:

These topics run at lower rates and are used for monitoring, not real-time control.

Summary: The Complete Picture

Let's recap the entire architecture with a comprehensive diagram:

╔═════════════════════════════════════════════════════════════════╗

║                  BeyondMimic Deployment Architecture            ║

╚═════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────┐

│                    Training Phase (Isaac Lab)                 │

│                                                               │

│  Reference Motion → PPO Training → Trained Policy (ONNX)     │

│                                            │                  │

└────────────────────────────────────────────┼──────────────────┘

│

↓ (upload to WandB)

┌───────────────────────────────────────────────────────────────┐

│              Deployment Phase (ros2_control)                  │

└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐

│   real.launch.py                                        │

│   ├─ Loads URDF with hardware interface config         │

│   ├─ Starts ros2_control_node                           │

│   ├─ Spawns controllers (with policy path)             │

│   └─ Starts teleop, rosbag, robot_state_publisher      │

└────────────────────────┬────────────────────────────────┘

│

↓

┌──────────────────────────────────────────────────────────┐

│  ros2_control_node (Real-Time Loop @ 200 Hz)            │

│  ┌────────────────────────────────────────────────────┐ │

│  │  while(running) {                                  │ │

│  │    hardware->read()      ← UnitreeSdk2 via DDS     │ │

│  │    controller->update()  ← Policy inference        │ │

│  │    hardware->write()     → UnitreeSdk2 via DDS     │ │

│  │  }                                                  │ │

│  └────────────────────────────────────────────────────┘ │

└────────────────────────┬──────────────────────┬──────────┘

│                      │

↓                      ↓

┌──────────────────────────────┐  ┌──────────────────────────┐

│  MotionTrackingController    │  │  UnitreeSdk2             │

│  ├─ read_state_interfaces()  │  │  ├─ read() → DDS RX      │

│  ├─ policy.forward()         │  │  ├─ write() → DDS TX     │

│  └─ write_command_interfaces│  │  └─ network_interface cfg│

└──────────────────────────────┘  └─────────────┬────────────┘

│


## ↓ (DDS)
┌──────────────────────────┐

│   G1 Robot Hardware      │

│   ├─ 29 Joint Motors     │

│   ├─ IMU Sensor          │

│   └─ Motor Controllers   │

└──────────────────────────┘

═══════════════════════════════════════════════════════════════

Key Concepts:

• Policy executes INSIDE a ros2_control controller

• No ROS topics in the critical control path

• Direct C++ function calls for real-time performance

• DDS (via Unitree SDK2) handles robot communication

• Total latency: 2-5 ms sensor-to-actuator

═══════════════════════════════════════════════════════════════


### Key Takeaways

Policy execution happens through ros2_control - not ROS topics

Real-time loop uses C++ function calls - nanosecond latency

Hardware interface abstracts communication - same code for sim/real

DDS handles robot communication - via network_interface parameter

Controller lifecycle ensures safety - starts inactive, explicit activation


### What's next? Now that you understand how policies execute on real hardware, you can explore advanced topics like custom reward functions, multi-modal policies, and integration with perception systems.

---

**Previous:** Unit 2.3 — BeyondMimic Motion Tracking Pipeline
Exercise

Explore ros2_control Interfaces

Use ros2 control list_hardware_interfaces to see all available interfaces

Identify which interfaces are command interfaces vs state interfaces

Compare the interfaces in simulation vs real robot

Controller Inspection

List all loaded controllers with ros2 control list_controllers

Check the configuration of walking_controller in config/g1/controllers.yaml

Understand which hardware interfaces each controller claims

Manual Controller Switching

Practice switching between controllers using the ROS 2 CLI

Monitor the controller states during transitions

Understand the safety implications of controller switching

Advanced Challenge

Read the UnitreeSdk2 hardware interface source code

Trace the data flow from DDS message to state_interface

Measure the actual control loop frequency using /diagnostics

Create a custom hardware interface for a different robot


# Unitree G1 Reinforcement Learning Course

mimic in unitree_rl_lab

> **Duration:** Estimated time to completion for the whole unit: 90 min
> **Objective:** nderstand and use mimic, the motion tracking framework in unitree_rl_lab
Introduction

As we saw in the unit describing BeyondMimic, the mimic portion of unitree_rl_lab is basically a copy of whole_body_tracking, the training side of BeyondMimic:


### To train, it requires a .csv file with the correct number of joints for the robot, the reference motion.

### The trained .onnx policy is then used by g1_ctrl in order to read the current joint states and try to match them to the reference motion in the most efficient way possible.

### In Beyondmimic, a ros2_control framework is implemented, while here, it is only an executable. Our goal is goal is to create a new controller that can take in the Velocity (gait) policies so we can implemente this more convenient method than just using the plain g1_ctrl executable.

### In the previous unit, you learned how to load mimic motions into g1_ctrl to easily switch between them and a gait policy. Now, you will train your own motion based on a list of .csv files we adapted from LAFAN1_Retargeting_Dataset, so shoutout to lvhaidong.

### 🔥 Exercise

🔥 EXERCISE: train and deploy your own custom motion

### The first part of the exercise is to extract a 10 second fragment of a longer motion from our dataset.
Open your GPU instance.

Clone The Construct's fork of LAFAN1 dataset.

Execute in Terminal #1

cd && git clone https://bitbucket.org/theconstructcore/lafan1_retargeting_dataset.git

Visualizing motions

Create retarget conda environment, activate it, and install dependencies:

# Step 1: Set up a Conda virtual environment

conda create -n retarget python=3.10

conda activate retarget

# Step 2: Install dependencies

conda install pinocchio -c conda-forge

pip install numpy rerun-sdk==0.22.0 trimesh joblib

Check all of the motions available for g1_23dof:

ls ~/lafan1_retargeting_dataset/g1_23dof

Run rerun_visualize.py in any of the above .csv files and pick one you like. 🚨 To deploy in real robot, make sure it doesn't move around too much, and that the movements aren't too violent 🚨

cd ~/lafan1_retargeting_dataset && python rerun_visualize.py --file_name dance1_subject2 --robot_type g1_23dof

🔍 The motion should be displaying in a rerun.io window:

Extracting 10 seconds from motion

Pick your favorite 10 seconds of your favorite motion.csv. Running at 30 fps * 10 seconds = 300 frames

Use our program to extract the section you selected:

Execute in Terminal #1

cd ~/lafan1_retargeting_dataset && python extract_frames.py g1_23dof/[MOTION_NAME].csv --start [FRAME_START] --num-frames 300

🔍 Look for the generated file in ~/lafan1_retargeting_dataset that ends with _extract_[START]-[END].csv


### Visualize your extracted frames the same way you visualized the original to make sure everything looks ok.
Convert .csv to .npz


### All trainings we've done so far for motion tracking require the reference motion to be in .npz format, which is just a file format by numpy that provides storage of array data using gzip compression.
To do this, use the file ~/unitree_rl_lab/scripts/mimic/csv_to_nz.py

Activate env_isaaclab conda environment:

Execute in Terminal #1

conda activate isaaclab

And make sure you are logged into your WandB account:

Execute in Terminal #1

wandb login --relogin

Convert your motion_extracted.csv:

Execute in Terminal #1

cd ~/unitree_rl_lab && python scripts/mimic/csv_to_npz.py -f /home/user/lafan1_retargeting_dataset/g1_23dof/[MOTION_NAME]_extract_[START]-[END].csv --input_fps 30

🔍 Look for generated .npz file in ~/lafan1_retargeting_dataset/g1_23dof

Execute in Terminal #1

ls ~/lafan1_retargeting_dataset/g1_23dof/ | grep npz

Create custom task for training


### Now that you have a motion_extracted.npz, copy the structure of existing tasks to train this new one.

### You can do this either directly in the GPU instance terminal (easiest for me) or push your files to your fork of unitree_rl_lab and pull them on the main course (in ~/ros2_ws). That way, you can use the IDE to do the actions below.
Execute in Terminal #1

cd ~/unitree_rl_lab/source/unitree_rl_lab/unitree_rl_lab/tasks/mimic/robots/g1_23dof/

🔍 Check existing task directories with ls. For example, look at structure of rodrigo/ (The coolest one):

Execute in Terminal #1

ls rodrigo/

__init__.py  dance1_subject2_23dof.csv

__pycache__  tracking_env_cfg.py

You need to copy this structure and add the generated .npz file:

Execute in Terminal #1

cp -r rodrigo/ [YOUR_MOTION_NAME]

Remove old .csv:

Execute in Terminal #1

cd [YOUR_MOTION_NAME] && rm -rf dance1_subject2_23dof.csv

Copy both of your generated .csv and .npz files from ~/lafan1_retargeting_dataset:

Execute in Terminal #1

cp ~/lafan1_retargeting_dataset/g1_23dof/[YOUR_GENERATED_MOTION].* .

Edit __init__.py with your desired task name:

Execute in Terminal #1

vim __init__.py

import gymnasium as gym

gym.register(

id="Unitree-G1-23dof-Rodrigo-Dance", ### <<<----------------- CHANGE ID FOR YOUR DESIRED NAME, LIKE Unitree-G1-23dof-[YOUR_NAME]-Motion

entry_point="isaaclab.envs:ManagerBasedRLEnv",

disable_env_checker=True,

kwargs={

"env_cfg_entry_point": f"{__name__}.tracking_env_cfg:RobotEnvCfg",

"play_env_cfg_entry_point": f"{__name__}.tracking_env_cfg:RobotPlayEnvCfg",

"rsl_rl_cfg_entry_point": f"unitree_rl_lab.tasks.mimic.agents.rsl_rl_ppo_cfg:BasePPORunnerCfg",

},

)

Edit tracking_env_cfg.py to reference YOUR_MOTION.npz that you generated:

Execute in Terminal #1

vim tracking_env_cfg.py

class CommandsCfg:

"""Command specifications for the MDP."""

motion = mdp.MotionCommandCfg(

asset_name="robot",

# generate npz file before training

# python python scripts/mimic/csv_to_npz.py -f path/to/G1_gangnam_style_V01.bvh_60hz.csv --input_fps 60

motion_file=f"{os.path.dirname(__file__)}/gangnam_style_4sec.npz", ### <<<------------------------------------ CHANGE FOR YOUR GENERATED .npz FILE THAT YOU COPIED IN YOUR TASK DIRECTORY

- ✅ You are ready to train. The file structure should look like this, but with your file names:
__init__.py

__pycache__

fight1_subject2_extract_732-850.csv

fight1_subject2_extract_732-850.npz

tracking_env_cfg.py

Train custom task

Check that your new custom task is available:

Execute in Terminal #1

cd ~/unitree_rl_lab && ./unitree_rl_lab.sh -l

🔍 Look for your new task:

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

|                                                                Available Environments in Unitree RL Lab                                                                |

+--------+--------------------------------------------+---------------------------------+--------------------------------------------------------------------------------+

| S. No. | Task Name                                  | Entry Point                     | Config                                                                         |

+--------+--------------------------------------------+---------------------------------+--------------------------------------------------------------------------------+

|   1    | Unitree-G1-23dof-Velocity                  | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.g1.23dof.base_velocity.velocity_env_cfg:RobotEnvCfg          |

|   2    | Unitree-G1-23dof-WideStance                | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.g1.23dof.wide_stance.velocity_env_cfg:RobotEnvCfg            |

|   3    | Unitree-G1-29dof-Velocity                  | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.g1.29dof.velocity_env_cfg:RobotEnvCfg                        |

|   4    | Unitree-Go2-Velocity                       | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.go2.velocity_env_cfg:RobotEnvCfg                             |

|   5    | Unitree-H1-Velocity                        | isaaclab.envs:ManagerBasedRLEnv | locomotion.robots.h1.velocity_env_cfg:RobotEnvCfg                              |

|   6    | Unitree-G1-23dof-Dance2Subject3            | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance2_subject3.tracking_env_cfg:RobotEnvCfg             |

|   7    | Unitree-G1-23dof-Dance2Subject5-SpinAround | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance2_subject5_spin_around.tracking_env_cfg:RobotEnvCfg |

|   8    | Unitree-G1-23dof-Mimic-Dance-102           | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance_102.tracking_env_cfg:RobotEnvCfg                   |

|   9    | Unitree-G1-23dof-DanceShort                | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.dance_short.tracking_env_cfg:RobotEnvCfg                 |

|   10   | Unitree-G1-23dof-Mimic-Gangnam-Style       | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.gangnam_style.tracking_env_cfg:RobotEnvCfg               |

|   11   | Unitree-G1-23dof-HorsePunch                | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.horse_punch.tracking_env_cfg:RobotEnvCfg                 |

|   12   | Unitree-G1-23dof-Rodrigo-Dance             | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.rodrigo.tracking_env_cfg:RobotEnvCfg                     |

|   13   | Unitree-G1-23dof-Student-Motion-1          | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_23dof.student_motion_1.tracking_env_cfg:RobotEnvCfg            |  ### <<<------- THIS ONE IS NEW!

|   14   | Unitree-G1-29dof-Mimic-Dance-102           | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_29dof.dance_102.tracking_env_cfg:RobotEnvCfg                   |

|   15   | Unitree-G1-29dof-Mimic-Gangnanm-Style      | isaaclab.envs:ManagerBasedRLEnv | mimic.robots.g1_29dof.gangnanm_style.tracking_env_cfg:RobotEnvCfg              |

+--------+--------------------------------------------+---------------------------------+--------------------------------------------------------------------------------+

Train your new task:

Execute in Terminal #1

./unitree_rl_lab.sh -t --task Unitree-G1-23dof-[YOUR_TASK_NAME]

🔍 Training episodes should start:

Learning iteration 1081/30000

Computation: 28409 steps/s (collection: 3.007s, learning 0.454s)

Mean action noise std: 0.33

Mean value_function loss: 0.0443

Mean surrogate loss: -0.0064

Mean entropy loss: 7.1966

Mean reward: 80.94

Mean episode length: 1316.54

Episode_Reward/joint_acc: -0.0364

Episode_Reward/joint_torque: -0.0227

Episode_Reward/action_rate_l2: -0.4982

Episode_Reward/joint_limit: -0.0151

Episode_Reward/motion_global_anchor_pos: 0.2006

Episode_Reward/motion_global_anchor_ori: 0.4101

Episode_Reward/motion_body_pos: 0.8516

Episode_Reward/motion_body_ori: 0.6604

Episode_Reward/motion_body_lin_vel: 0.7319

Episode_Reward/motion_body_ang_vel: 0.5108

Episode_Reward/undesired_contacts: -0.0022

Metrics/motion/error_anchor_pos: 0.4392

Metrics/motion/error_anchor_rot: 0.2086

Metrics/motion/error_anchor_lin_vel: 0.6768

Metrics/motion/error_anchor_ang_vel: 1.3256

Metrics/motion/error_body_pos: 0.1003

Metrics/motion/error_body_rot: 0.3376

Metrics/motion/error_joint_pos: 1.3296

Metrics/motion/error_joint_vel: 12.6798

Metrics/motion/sampling_entropy: 0.7817

Metrics/motion/sampling_top1_prob: 0.3950

Metrics/motion/sampling_top1_bin: 0.3000

Metrics/motion/error_body_lin_vel: 0.7172

Metrics/motion/error_body_ang_vel: 3.0357

Episode_Termination/time_out: 2.2500

Episode_Termination/anchor_pos: 0.2500

Episode_Termination/anchor_ori: 0.0417

Episode_Termination/ee_body_pos: 0.4583

--------------------------------------------------------------------------------

Total timesteps: 106364928

Iteration time: 3.46s

Total time: 3670.34s

ETA: 98098.5s

You can check the progress of your run in WandB, just like you did for the gait training.

Play trained policy in IsaacSim

Play inference with the trained agent in IsaacSim:

Execute in Terminal #1

cd ~/unitree_rl_lab && ./unitree_rl_lab.sh -p --task Unitree-G1-23dof-[YOUR_TASK_NAME] --run_path [YOUR_WANDB_RUN_PATH]

🔍 You should see the robot executing your movement (at a random starting point)

🔍 Running this play program generated the policy.onnx we need for deploy.

Check that your files have been generated:

Execute in Terminal #1

ls ~/unitree_rl_lab/logs/rsl_rl/unitree_g1_23dof_[YOUR_MOTION_NAME]/[DATE_AND_TIME]/

events.out.tfevents.1769521158.ip-172-31-45-187.4959.0  model_0.pt     model_200.pt  model_500.pt  model_800.pt

exported                                                model_100.pt   model_300.pt  model_600.pt  model_900.pt

git                                                     model_1000.pt  model_400.pt  model_700.pt  params

Execute in Terminal #1

ls ~/unitree_rl_lab/logs/rsl_rl/unitree_g1_23dof_[YOUR_MOTION_NAME]/[DATE_AND_TIME]/exported

policy.onnx  policy.pt

You can also find the .onnx in WandB, under Artifacts in your run:


# Unitree G1 Reinforcement Learning Course


---

V1

Robot Teleoperation

> **Duration:** Estimated time to completion for the whole unit: 60 min.
> **Objective:** eleoperate the Unitree G1 humanoid robot using either VR whole-body control (GEAR-Sonic) or the decoupled whole-body control stack (decoupled_wbc), and understand why the latter is the preferred pipeline for data collection. (As of April 1st, 2026)
Introduction

Teleoperation lets a human operator directly control the Unitree G1 in real time, mapping human motion or controller inputs to robot joint commands. This is a critical capability for two reasons:

Direct robot control — useful for demonstrations, inspection, and safety monitoring.


### Data collection — high-quality human demonstrations are the foundation of imitation learning and training VLA models such as GR00T.
This unit covers two teleoperation approaches:

Method 1: GEAR-Sonic (VR Whole-Body Teleoperation)


### GEAR-Sonic is NVIDIA's VR-based whole-body teleoperation system. It uses a PICO 4 VR headset and ankle motion trackers to stream full-body SMPL pose data to the robot in real time via the zmq_manager input interface.
📖 Official documentation:

VR Teleop Setup (PICO)

PICO VR Whole-Body Teleop Tutorial

Required Hardware

PICO 4 / PICO 4 Pro headset

2× PICO controllers (included with the headset)

2× PICO motion trackers — strapped to the ankles

A high-speed, low-latency Wi-Fi connection (teleoperation performance is heavily dependent on network quality)

Step 1: Install XRoboToolkit

XRoboToolkit streams body-tracking data from the PICO headset to your workstation. It has two components:

PC Service — runs on your workstation:

Visit XR-Robotics on GitHub and follow the "Install XRoboToolkit-PC-Service" instructions.

For an onboard (robot-side) install, run:

sudo dpkg -i gear_sonic_deploy/thirdparty/roboticsservice_1.0.0.0_arm64.deb

PICO App — runs on the headset:

Wear the headset and complete the PICO quick setup. Connect to Wi-Fi.

Open the PICO browser and search for "xrobotoolkit" → open the XR-Robotics GitHub page.

Enable Developer Mode (Settings → Developer).

Scroll down to find the APK download link and click it with the trigger.


### Open the browser downloads, click XRoboToolkit-PICO-1.1.1.apk, and select Install. The app appears in the Unknown section of your library.
Step 2: Motion Tracker Setup


### Strap one motion tracker to each ankle with the light indicator facing up. Scrunch down any baggy clothing so the trackers remain visible.
In PICO settings → Developer, turn Safeguard off.

Open the Motion Tracker app (or tap the Wi-Fi icon → motion tracker circle).

Click the "i" icon next to each tracker and unpair all trackers.


### Press Pair (top-right corner), then hold each tracker's top button for 6 seconds until lights flash red and blue.
Motion Tracker Calibration:

Wear the headset over your eyes.

Press Calibrate and follow the two sequences:

Sequence 1 — Stand still, controllers hanging at your sides.

Sequence 2 — Look down at the ankle trackers until the cameras recognise them.


### After calibration, move the headset to your forehead (facing forward) so the cameras continue tracking the ankle trackers.
Step 3: Install the PICO Teleop Environment

From the GR00T-WholeBodyControl repo root, run the installer:

bash install_scripts/install_pico.sh


### This creates a .venv_teleop virtual environment (Python 3.10) that includes ZMQ, Pinocchio, PyVista, MuJoCo, and the Unitree SDK2 Python bindings.
Activate it with:

source .venv_teleop/bin/activate   # prompt: (gear_sonic_teleop)

Step 4: Connect the PICO to Your Workstation

Ensure the laptop/PC and PICO are on the same Wi-Fi network. Note the laptop's IPv4 address.


### Open XRoboToolkit on the PICO. Enter the laptop IP next to "PC Service:" → confirm WORKING appears next to "Status:".
In the XRoboToolkit app, make sure the following are selected:

Tracking: tick Head and Controller.

Data/Control: select Send.

Pico Motion Tracker: select Full body.

Running VR Teleop in Simulation

Run three terminals simultaneously.


> **⚠️ Note:** ⚠️ Safety Warning — Whole-body teleoperation involves fast, agile motions. Always maintain a clear safety zone. Keep a safety operator at the keyboard ready to trigger an emergency stop (O in the C++ terminal, or A+B+X+Y on the PICO controllers). Wear tight-fitting pants or leggings so the ankle trackers remain visible.
Execute in Terminal #1 — MuJoCo Simulator

source .venv_teleop/bin/activate

python gear_sonic/scripts/run_sim_loop.py

Execute in Terminal #2 — C++ Deployment

cd gear_sonic_deploy

source scripts/setup_env.sh

./deploy.sh --input-type zmq_manager sim

# Wait until you see "Init done"

Execute in Terminal #3 — PICO Teleop Streamer

source .venv_teleop/bin/activate

# With full visualization (recommended for first run):

python gear_sonic/scripts/pico_manager_thread_server.py --manager \

--vis_vr3pt --vis_smpl

# Without visualization (headless / onboard):

# python gear_sonic/scripts/pico_manager_thread_server.py --manager

🔍 Wait for a window showing the Unitree G1 mesh at default angles. If no window appears, check the PICO's XRoboToolkit IP configuration.

Your First Teleop Session:


### Assume the calibration pose — stand upright, feet together, upper arms at your sides, forearms bent 90° forward (L-shape), palms inward.
Press A + B + X + Y to engage the control policy (triggers CALIB_FULL).


### Align your arms with the robot's current pose, then press A + X to enter POSE mode (full-body SMPL teleop). Move your arms and legs — the robot follows.
Press A + X again to return to PLANNER (idle) mode.

Press A + B + X + Y again to stop the robot.

Running VR Teleop in Real Robot

Execute in Terminal #1

cd ~/git-repo/GR00T-WholeBodyControl/gear_sonic_deploy && source scripts/setup_env.sh

Execute in Terminal #1

./deploy.sh --input-type zmq_manager real --zmq-host 192.168.123.222

In External PC:

Execute in Terminal #2

cd ~/git-repo/GR00T-WholeBodyControl && source .venv_teleop/bin/activate

Execute in Terminal #2

python gear_sonic/scripts/pico_manager_thread_server.py --manager

In PICO:

Open XRoboToolkit App

Select IP that is running XRobotics servcer

Toggle Head, Controller and Motion Tracker

Toggle Send

PICO controllers:

A+B+X+Y to activate walking policy

A+B to activate teleop

PICO Controls Cheatsheet

Method 2: decoupled_wbc (Recommended for Data Collection)

decoupled_wbc is a software stack for loco-manipulation experiments on the Unitree G1. It provides whole-body control policies, a teleoperation stack, and — crucially — a built-in data exporter, making it the preferred approach for collecting robot demonstrations.

📖 Official documentation: decoupled_wbc reference

Installation


### Prerequisites: Ubuntu 22.04, an NVIDIA GPU with a recent driver, Docker, and the NVIDIA Container Toolkit.
Install Git and Git LFS:

sudo apt update

sudo apt install git git-lfs

git lfs install

Clone the repository:

mkdir -p ~/Projects

cd ~/Projects

git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git

cd GR00T-WholeBodyControl

Docker Environment

All dependencies are pre-installed in a Docker image. Pull and start the container:

./docker/run_docker.sh --install --root

To re-enter an existing container:

./docker/run_docker.sh --root

Running the Control Stack

Once inside the Docker container, launch the control policy. In simulation:

Execute in Terminal #1 (Docker) — Control Loop

python decoupled_wbc/control/main/teleop/run_g1_control_loop.py

For the real robot, ensure the host machine is configured with a static IP at 192.168.123.222 (subnet mask 255.255.255.0) per the G1 SDK Development Guide:

python decoupled_wbc/control/main/teleop/run_g1_control_loop.py --interface real

🔍 Keyboard shortcuts (focus on the terminal window):

Running the Teleoperation Stack

Keep run_g1_control_loop.py running (Terminal #1). In a second terminal, launch the teleoperation policy:

Execute in Terminal #2 (Docker) — Teleop Policy

python decoupled_wbc/control/main/teleop/run_teleop_policy_loop.py --hand_control_device=pico --body_control_device=pico

🔍 Before running, configure the teleop app on the PICO by following the XR Robotics guidelines. The PC software is pre-installed inside the Docker container — only the XRoboToolkit-PC-Service component is needed.

Ensure the PICO is connected to the same network as the host computer. To verify the PICO stream is working:

python decoupled_wbc/control/teleop/streamers/pico_streamer.py

PICO Controller Bindings:

Why decoupled_wbc for Data Collection?

While GEAR-Sonic provides a more immersive whole-body teleoperation experience, decoupled_wbc is the recommended approach for collecting robot demonstrations for the following reasons:


### Integrated data exporter — the pipeline records trajectories, camera frames, and task annotations in a single command, with no additional tooling required.

### Clear, reproducible pipeline — a single deploy_g1.py script orchestrates the control loop, teleoperation policy, and camera forwarder in a managed tmux session.

### Automatic task prompting — the data exporter window accepts free-text task descriptions that are saved alongside each trajectory.

### Built-in trajectory management — operators can start/stop/discard recordings directly from the PICO controller without touching the computer.
Running the Data Collection Stack

The deploy_g1.py helper launches the full stack — control loop, teleop policy, and camera forwarder — in a single tmux session named g1_deployment:

Execute in Terminal (Docker) — Data Collection

python decoupled_wbc/scripts/deploy_g1.py \

--interface sim \

--camera_host localhost \

--sim_in_single_process \

--simulator robocasa \

--image-publish \

--enable-offscreen \

--env_name PnPBottle \

--hand_control_device=pico \

--body_control_device=pico

🔍 The tmux session g1_deployment is created with the following panes:

Data collection operations:

- ✅ Each recorded trajectory is automatically saved with the camera frames and task annotation, ready to be used for downstream training.
Summary

In this unit you have learned how to teleoperate the Unitree G1 using two approaches:


### GEAR-Sonic — immersive VR whole-body teleoperation using a PICO headset and ankle motion trackers, streaming full-body SMPL poses via zmq_manager.
decoupled_wbc — controller-based teleoperation with an integrated data collection pipeline, making it the go-to stack for gathering high-quality robot demonstrations.


### The decoupled_wbc pipeline is the foundation for training imitation learning policies and VLA models such as GR00T on the Unitree G1.
4. Unitree G1 Course: Pal Mujoco Lab Intro


---

V1

4.1: TheConstruct and Pal Robotics

Now that you know how to train your Unitree G1, it's time to apply it to other humanoid robots.


### The Objective of this, is that you have a broader and non hardware specific knowledge on how to train a robot to walk or perform a task.
This way you will be able to apply it to any robot, and not be tied to some specific manufacturer.

In this case, you are going to learn the following:

Instead of using IsaacLab, we will use MujocoLab.

Instead of using a Unitree G1 humanoid robot, we will use the Pal Robotics humanoid robot Kangaroo.


### 4.2 What is Mujoco Lab exactly?
Mjlab combines Isaac Lab's manager-based API with MuJoCo Warp, a GPU-accelerated version of MuJoCo.


### The framework provides composable building blocks for environment design, with minimal dependencies and direct access to native MuJoCo data structures.
That is what the documentation says. What does this mean?

Well mainly we needed IsaacLab "Simulator" before because how could we paralelise Mujoco simulator otherwise?

This is where Mujoco WARP comes into play.

MuJoCo Warp is MuJoCo re-implemented on top of Warp, NVIDIA’s GPU-native simulation framework.


### It’s not a new physics engine — it’s the same MuJoCo model semantics, but executed massively in parallel on the GPU.
Classic MuJoCo:

CPU-based

Extremely accurate

Sequential stepping (one env per core, basically)

MuJoCo Warp:

GPU-based

Thousands of envs stepped simultaneously

And is this last feature *Thousands of envs stepped simultaneously^* which sells it.

We need that to be able to iterate fast enough and train our model at a sensible speed.

MuJoCo Warp is designed to plug directly into:


## JAX
PyTorch

CUDA-native training loops

So you can do: policy → physics → reward → gradient

Without round-tripping to CPU.

For VLAs / imitation / policy distillation this matters a LOT.

Lets use MujocoLab


### Lets access again to the GPU NVIDIA cloud computer that will allow you to train your policies during the workshop.
Open the GPU instance by clicking on the following icon in the bottom menu bar:

🔍 A new window should open and the instance starts loading. When it's ready, you can login as user and a desktop like this should appear:

In this new GPU desktop, open a terminal Right Click -> Open Terminal Here.

You can also open VSCode for editing files. Right Click -> Applications -> Developement - VSCode

In this new GPU desktop, open a terminal MIDDLE Click -> See all the windows oppened

Very useful for finding the windows you have minimised.

Start a dummy Pal Kangaroo simulation in mjlab

Execute the following commands in the GPU Instance terminal


### You will have to use the copy icon on the top left corner of teh GPU instance window to be able to copy commands back and forth form inside the GPU instance.
Execute in GPU Terminal #1

conda deactivate

cd ~/pal_mjlab

uv run play Mjlab-Velocity-Flat-Pal-Kangaroo --agent random

Copy these comands into the copy window, to be able to paste them inside the instance:

You should now see something like this:

Here we are just loading the simulated environment and spawning the robot, no trained policy is being executed

You can also use a web based visualiser, in case you are accessing a remote system without graphical interface:

Execute in GPU Terminal #1

conda deactivate

cd ~/pal_mjlab

uv run play Mjlab-Velocity-Flat-Pal-Kangaroo --agent random --viewer viser

UV will install whatever it needs to work.

And you should get an address like so:

http://localhost:8080


### You then can Access through the public IP of your remote system, or even use this in a local system directly in the browser.
In our case, lets do it directly on the GPU instance firefox, because you might not know the IP.

Execute in GPU Terminal #2

firefox http://localhost:8080

You should see something like this:

Also you can clock on share and then that link paste it on your LOCAL computer and you shoudl see the same thing:

What have we just executed?

Let's peek into the code that we just run.

First thing is that we access the pal_mjlab that has all teh environments used for Pal robots.

The structure on how this works is really similar to IsaacLab. * Lets start with the following file, that you can see with VSCode in the **GPU Instance:

pal_mjlab/src/pal_mjlab/tasks/velocity/kangaroo/__init__.py

from mjlab.tasks.registry import register_mjlab_task

from mjlab.tasks.velocity.rl import VelocityOnPolicyRunner

from .env_cfgs import (

pal_kangaroo_flat_env_cfg,

pal_kangaroo_grippers_flat_env_cfg,

pal_kangaroo_grippers_rough_env_cfg,

pal_kangaroo_hands_flat_env_cfg,

pal_kangaroo_hands_rough_env_cfg,

pal_kangaroo_rough_env_cfg,

)

from .rl_cfg import pal_kangaroo_ppo_runner_cfg

register_mjlab_task(

task_id="Mjlab-Velocity-Rough-Pal-Kangaroo",

env_cfg=pal_kangaroo_rough_env_cfg(),

play_env_cfg=pal_kangaroo_rough_env_cfg(play=True),

rl_cfg=pal_kangaroo_ppo_runner_cfg(),

runner_cls=VelocityOnPolicyRunner,

)

register_mjlab_task(

task_id="Mjlab-Velocity-Flat-Pal-Kangaroo",

env_cfg=pal_kangaroo_flat_env_cfg(),

play_env_cfg=pal_kangaroo_flat_env_cfg(play=True),

rl_cfg=pal_kangaroo_ppo_runner_cfg(),

runner_cls=VelocityOnPolicyRunner,

)

register_mjlab_task(

task_id="Mjlab-Velocity-Rough-Pal-Kangaroo-Hands",

env_cfg=pal_kangaroo_hands_rough_env_cfg(),

play_env_cfg=pal_kangaroo_hands_rough_env_cfg(play=True),

rl_cfg=pal_kangaroo_ppo_runner_cfg(),

runner_cls=VelocityOnPolicyRunner,

)

register_mjlab_task(

task_id="Mjlab-Velocity-Flat-Pal-Kangaroo-Hands",

env_cfg=pal_kangaroo_hands_flat_env_cfg(),

play_env_cfg=pal_kangaroo_hands_flat_env_cfg(play=True),

rl_cfg=pal_kangaroo_ppo_runner_cfg(),

runner_cls=VelocityOnPolicyRunner,

)

register_mjlab_task(

task_id="Mjlab-Velocity-Rough-Pal-Kangaroo-Grippers",

env_cfg=pal_kangaroo_grippers_rough_env_cfg(),

play_env_cfg=pal_kangaroo_grippers_rough_env_cfg(play=True),

rl_cfg=pal_kangaroo_ppo_runner_cfg(),

runner_cls=VelocityOnPolicyRunner,

)

register_mjlab_task(

task_id="Mjlab-Velocity-Flat-Pal-Kangaroo-Grippers",

env_cfg=pal_kangaroo_grippers_flat_env_cfg(),

play_env_cfg=pal_kangaroo_grippers_flat_env_cfg(play=True),

rl_cfg=pal_kangaroo_ppo_runner_cfg(),

runner_cls=VelocityOnPolicyRunner,

)

When we execute the command uv run play Mjlab-Velocity-Flat-Pal-Kangaroo --agent random --viewer viser, what happens exactly?

First: The __init__.py is doing registration-by-import: as soon as Python imports pal_mjlab.tasks.velocity.kangaroo, it calls register_mjlab_task(...) six times and wires each task_id to:

an environment config (env_cfg)

a play-time environment config (play_env_cfg)

an RL runner config (rl_cfg)

a runner class (runner_cls=VelocityOnPolicyRunner)

Where Mjlab-Velocity-Flat-Pal-Kangaroo

What is exactly defined here? And how could I potentially change it?

Let's answer those questions.

1) The actual environment composition (robot + terrain + sensors + randomization + rewards/obs)

It's built inside the env config factory you pass in:

pal_mjlab/src/pal_mjlab/tasks/velocity/kangaroo/__init__.py [SNIPPET]

env_cfg=pal_kangaroo_flat_env_cfg(),

play_env_cfg=pal_kangaroo_flat_env_cfg(play=True),

Lets have a look at teh file pal_mjlab-main/src/pal_mjlab/tasks/velocity/kangaroo/env_cfgs.py:

pal_mjlab-main/src/pal_mjlab/tasks/velocity/kangaroo/env_cfgs.py [SNIPPET]

def pal_kangaroo_flat_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:

"""Create PAL Robotics KANGAROO flat terrain velocity configuration."""

cfg = pal_kangaroo_rough_env_cfg(play=play)

cfg.sim.njmax = 300

cfg.sim.mujoco.ccd_iterations = 50

cfg.sim.contact_sensor_maxmatch = 64

cfg.sim.nconmax = None

# Switch to flat terrain.

assert cfg.scene.terrain is not None

cfg.scene.terrain.terrain_type = "plane"

cfg.scene.terrain.terrain_generator = None

# Disable terrain curriculum.

assert cfg.curriculum is not None

assert "terrain_levels" in cfg.curriculum

del cfg.curriculum["terrain_levels"]

if play:

# Disable command curriculum.

assert "command_vel" in cfg.curriculum

del cfg.curriculum["command_vel"]

twist_cmd = cfg.commands["twist"]

assert isinstance(twist_cmd, UniformVelocityCommandCfg)

twist_cmd.ranges.lin_vel_x = (-1.5, 2.0)

twist_cmd.ranges.ang_vel_z = (-0.7, 0.7)

return cfg

Here , we set the environment config (the file you pasted, env_cfgs.py):

pal_kangaroo_flat_env_cfg() builds the env by calling:

cfg = pal_kangaroo_rough_env_cfg(play=play)

Then overrides terrain + some sim params

How we would change the terrain?

For the flat env

Right now, flat is literally:

cfg.scene.terrain.terrain_type = "plane"

cfg.scene.terrain.terrain_generator = None

We have to look into this make_velocity_env_cfg(), inside the pal_kangaroo_rough_env_cfg():

def pal_kangaroo_rough_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:

"""Create PAL Robotics KANGAROO rough terrain velocity configuration."""

cfg = make_velocity_env_cfg()

This is inside the mjlab LINK REPO

In this velocity_env_cfg.py file.

scene=SceneCfg(

terrain=TerrainImporterCfg(

terrain_type="generator",

terrain_generator=replace(ROUGH_TERRAINS_CFG),

max_init_terrain_level=5,

),

...

)


### We need to look into this file mjlab/terrains/config.py, to see how this method works TerrainGeneratorCfg().
Here we can change how terrain works how, rough , pathces sizes everything. In our case we are using the plane, which is in terrainimporter

mjlab/terrains/terrain_importer.py

elif self.cfg.terrain_type == "plane":

self.import_ground_plane("terrain")

self.configure_env_origins()

So the plane is created by:

def import_ground_plane(self, name: str) -> None:

_DEFAULT_PLANE_TEXTURE.edit_spec(self._spec)

_DEFAULT_PLANE_MATERIAL.edit_spec(self._spec)

self._spec.worldbody.add_body(name=name).add_geom(

name=name,

type=mujoco.mjtGeom.mjGEOM_PLANE,

size=(0, 0, 0.01),

material=_DEFAULT_PLANE_MATERIAL.name,

)

spec_cfg.LightCfg(pos=(0, 0, 1.5), type="directional").edit_spec(self._spec)

Which in this case we are adding a simple plane in mujoco.

How we would change the robot?

in pal_mjlab/tasks/velocity/kangaroo/env_cfgs.py:

cfg.scene.entities = {"robot": get_kangaroo_robot_cfg()}

This gets the Kangaroo mujoco entity and places it inside the mujoco environment.

Where is this Kangarooentity? In this file pal_mjlab/robots/pal_kangaroo/kangaroo_constants.py

It gets the models from these files, mainly this file pal_mjlab/robots/pal_kangaroo/xmls/kangaroo.xml:

KANGAROO_PATH = PAL_MJLAB_SRC_PATH / "robots" / "pal_kangaroo" / "xmls"

KANGAROO_XML = KANGAROO_PATH / "kangaroo.xml"

KANGAROO_HANDS_XML = KANGAROO_PATH / "kangaroo_hands.xml"

KANGAROO_GRIPPERS_XML = KANGAROO_PATH / "kangaroo_grippers.xml"

kangaroo.xml

<mujoco model="kangaroo">

<compiler angle="radian" meshdir="assets" autolimits="true"/>

<default>

<default class="kangaroo">

<!-- stiffer contact (solref="0.002 1") worsened sim2real, using defaults -->

<!-- <geom solref="0.002 1" priority="1"/> -->

<site group="5" rgba="1 0 0 1" size="0.01" />

<default class="visual">

<geom type="mesh" contype="0" conaffinity="0" group="2" density="0" material="dark_gray"/>

</default>

<default class="collision">

<geom type="capsule" group="3" material="bright_orange" contype="1" conaffinity="1"/>

<default class="foot_capsule">

<geom type="capsule" size="0.01"/>

</default>

</default>

</default>

</default>

<asset>

<!-- materials -->

<material name="dark_gray"      rgba="0.298039 0.298039 0.298039 1"/>

<material name="bright_orange"  rgba="1 0.65 0 0.2"/>

<!-- meshes -->

<mesh name="base_link_with_pelvis"    content_type="model/stl" file="base/base_link_with_pelvis.STL" />

<mesh name="handle"                   content_type="model/stl" file="base/handle.STL" />

<mesh name="pelvis_base_link"         content_type="model/stl" file="pelvis/pelvis_base_link.STL" />

<mesh name="pelvis_1_link"            content_type="model/stl" file="pelvis/pelvis_1_link.STL" />

<mesh name="pelvis_2_link"            content_type="model/stl" file="pelvis/pelvis_2_link.STL" />

<mesh name="torso_link"               content_type="model/stl" file="torso/torso_link.STL" />

<mesh name="leg_left_1_link"          content_type="model/stl" file="leg/leg_left_1_link.STL" />

<mesh name="leg_left_2_link"          content_type="model/stl" file="leg/leg_left_2_link.STL" />

<mesh name="leg_left_3_link"          content_type="model/stl" file="leg/leg_left_3_link.STL" />

<mesh name="leg_6_link"               content_type="model/stl" file="leg/leg_left_6_link.STL" />

<mesh name="leg_7_link"               content_type="model/stl" file="leg/leg_left_7_link.STL" />

<mesh name="leg_right_1_link"         content_type="model/stl" file="leg/leg_right_1_link.STL" />

<mesh name="leg_right_2_link"         content_type="model/stl" file="leg/leg_right_2_link.STL" />

<mesh name="leg_right_3_link"         content_type="model/stl" file="leg/leg_right_3_link.STL" />

<mesh name="leg_6_link1"              content_type="model/stl" file="leg/leg_right_6_link.STL"/>

<mesh name="leg_7_link1"              content_type="model/stl" file="leg/leg_right_7_link.STL"/>

<mesh name="leg_femur_link"           content_type="model/stl" file="leg/leg_femur_link.STL" />

<mesh name="leg_tibia_link"           content_type="model/stl" file="leg/leg_tibia_link.STL" />

<mesh name="arm_base_link"            content_type="model/stl" file="arm/arm_base_link.STL" />

<mesh name="arm1_link"                content_type="model/stl" file="arm/arm1_link.STL" />

<mesh name="arm2_link"                content_type="model/stl" file="arm/arm2_link.STL" />

<mesh name="arm3_link"                content_type="model/stl" file="arm/arm3_link.STL" />

<mesh name="fake_forearm_left_link"   content_type="model/stl" file="arm/fake_forearm_left_link.STL" />

<mesh name="fake_forearm_right_link"  content_type="model/stl" file="arm/fake_forearm_right_link.STL" />

</asset>

<worldbody>

..

</worldbody>

<contact>

..

</contact>

<sensor>

..

</sensor>

</mujoco>

And loads with this method:

def _load_spec(xml_path: Path) -> mujoco.MjSpec:

spec = mujoco.MjSpec.from_file(str(xml_path))

spec.assets = get_assets(spec.meshdir)

return spec


## EXTRA INFO
You can see in the commands that we are using uv. But what is it exactly?

UV is an extremely fast Python package and project manager, written in Rust.UV Source

The role of uv in that command, think of uv as:

pip + venv + python + reproducibility, all in one fast binary.

So when you write:

uv run play Mjlab-Velocity-Flat-Pal-Kangaroo --agent random *You are not just running play — you’re running it inside a uv-managed Python environment.

It Creates / activates the correct Python environment automatically

Reads pyproject.toml

Ensures:

Correct Python version

Correct dependencies

Installs anything missing (once)

Then runs the command

Equivalent mental model:

source .venv/bin/activate

python -m play ...

…but faster, cleaner, and reproducible.


### 4.3 Training Walking Policy for Kangaroo
Now lets train a olicy to be able to make our Kangaroo robot stand.

For that you have to execute teh following commands:

Execute in GPU Terminal #1

conda deactivate

cd ~/pal_mjlab

uv run train Mjlab-Velocity-Flat-Pal-Kangaroo --env.scene.num-envs 4096

This will train with 4096 simulatneous environments


### When you execute it, one of the things that it will ask is your API key from Weights And Biases. Here is the link to generate the API Key.

### What is Weights And Biases? In a few words, its a webpage where your trainining logs an dpolicies will be stored, allowing you to monitor trianing form anywhere and access your trained models.

### This is key when working with models of other people or just managing your trainings. Its really neat.
Just create an account for free.

In this image, you can see that in this account four trainings were done.

You can access all the training data.

When executing the training command, a new training should have apperared

You should see in the terminal the episodes running, that means its training.


### Also in the WandB page https://wandb.ai/YOUR_USER/mjlab, click on the new training episode, and you will be able to see all the reward values.

### The most important is the Train/mean_reward. When it plateous then it means that it probably wont improve teh policy enymore.
You will need to traing minimum aroudn 2 hourse to have good results.


### You can stop anytime the training and teh policy will be stored in teh "WandB" page with teh training logs.

### You can see also teh files generated. The most important is the "2026-02-10_14-41-18.onnx", where all the policy resides.
If you click on it you will be abel to see teh structure of the Neural Network.

We can download these files to use them in any system that doesnt support direct access to wandb files, by executing this commands:

Get the policy path by pressing on the three points

In this case we get for rdaneellivaw/mjlab/s7ln45vo.

The syntax is: wandb pull RUN with --entity/-e and --project/-p.

Execute in GPU Terminal #1

We download them in a certain folder so that we have everything tidy.

conda deactivate

cd ~/pal_mjlab

uv run wandb login

mkdir -p ~/rl_policies/s7ln45vo

cd ~/rl_policies/s7ln45vo

uv run --project ~/pal_mjlab wandb pull s7ln45vo -e rdaneellivaw -p mjlab

mv ~/rl_policies/s7ln45vo ~/rl_policies/loco_s7ln45vo_mjlab

We Validate in another sim


### To be able to have higher certainty that our trained policy works in the real robot, we need to test it in other simulators to see if it adapts to different versions of the same robot.
It also allows us to move it around and apply forces to test how our policy behaves.

For that, PAL robotics gives us a Docker with a Gazebo-based simulation of Kangaroo.

These are the steps:

Step1 : Create a gitlab account

We need to have an account in order to download the Docker container.

https://about.gitlab.com/

Step2 : Download the Docker container

Pal robotics has already generated a Docker container with all the files needed.

Follow these steps:

Execute in GPU Terminal #1

# Because this docker does sets the hosts inside the docker, previous versions might be inside your instance with the wrong IP, so better remove the Docker and redownload it

docker rm -f pal_kangaroo_sim

# Redownload it and set up

xhost +

docker run --gpus all -it \

--env LOCAL_USER_ID=$(id -u) \

--env LOCAL_GROUP_ID=$(id -g) \

--env LOCAL_GROUP_NAME=$(id -gn) \

--env DISPLAY \

--env QT_X11_NO_MITSHM=1 \

--env="NVIDIA_DRIVER_CAPABILITIES=all" \

--env="NVIDIA_VISIBLE_DEVICES=all" \

--volume=/tmp/.X11-unix:/tmp/.X11-unix:rw \

-v /run/user/$(id -u)/keyring/ssh:/run/host_ssh_auth_sock \

-e SSH_AUTH_SOCK=/run/host_ssh_auth_sock \

--net host \

--privileged \

-v /home/$USER/rl_policies:/home/user/rl_policies \

-v /var/run/docker.sock:/var/run/docker.sock \

--name pal_kangaroo_sim \

registry.gitlab.com/pal-robotics-public/kangaroo_robot/pal-kangaroo-rl-inference

You should now be inside the Docker.

To get out of the Docker just type in the terminal:

Execute in GPU-DOCKER Terminal #1

exit

To start the docker already downloaded execute the following command

Execute in GPU-DOCKER Terminal #1

# For running once downloaded

docker start pal_kangaroo_sim && docker attach pal_kangaroo_sim

#Once started, open a Terminator instance running:

#Shell

terminator -u

Inside these three terminals, execute a default policy that the people at Pal Robotics have already trained really well:

Step3 : Start default already trained policy by Pal Robotics

Execute in GPU-DOCKER Terminal #1


> **⚠️ Note:** WARNING: Please wait until the first command kangar∞palphysicssiμla→r makes the RVIZ appear with the robot standing, to launch the second command in terminal 2.
Execute in GPU-DOCKER-DIVISION Terminal #1

# And split ot horozontally  CTRL+SHIFT+O three


## # T1
roslaunch kangaroo_pal_physics_simulator kangaroo_pal_physics_simulator.launch

Execute in GPU-DOCKER-DIVISION Terminal #2


## # T2
roslaunch pal_policy_deployer kang_rl_deployer.launch model:=v62

Output

If you see this, then the controller loaded correctly:

[INFO] [1770907958.476543, 39.822000]: Loading controller: subscriber_controller

[INFO] [1770907962.491923, 41.117000]: Controller Spawner: Loaded controllers: subscriber_controller

[INFO] [1770907962.501926, 41.120000]: Started controllers: subscriber_controller

Execute in GPU-DOCKER-DIVISION Terminal #3


## # T3
rostopic pub /cmd_vel geometry_msgs/Twist "linear:

x: 0.5

y: 0.0

z: 0.0

angular:

x: 0.0

y: 0.0

z: 0.0"

# T3 : Also you can apply forces to teh robot

~/rl_policies/loco_ns27lvcz_mjlab

# Push in Y axis

rostopic pub /simulator/external_wrench pal_simulation_msgs/ExternalWrench "header:

seq: 0

stamp: {secs: 0, nsecs: 0}

frame_id: 'base_link'

link_name: 'base_link'

wrench:

force: {x: 0.0, y: 100.0, z: 0.0}

torque: {x: 0.0, y: 0.0, z: 0.0}

application_point: {x: 0.0, y: 0.0, z: 0.0}

duration: {secs: 1, nsecs: 0}"

These three commands are:

1) Start the kangaroo_pal_physics_simulator, which loads all the controllers and systems needed for the real/simulated robot to work. You can see that the robot stays upright, which indicates that there is a basic control to make the robot stand.

2) Start the pal_policy_deployer, which will load the AI policy. In this case, we load the v62 Pal already trained walking policy.

3) We can send a cmd_vel command like a joystick to make it move, and also apply forces as if we were pushing the robot. In this case, we are applying a cmd_vel of linear.x = 0.5, and the push is a force in the X direction on the base_link for a duration of 1 second.

You should see something similar to this:

Here you see the push tests in X and in Y axis.

Step4 : Download your own trained policy and place it in Docker container

Remember these commands that we did to download our policy?

If you didn't do it, here is a reminder:

Execute in GPU Terminal #1


## IF YOU DIDNT DO THIS BEFORE, DO IT.
We download them in a certain folder so that we have everything tidy.

conda deactivate

cd ~/pal_mjlab

# We force relogin just in case there is anothers users login there, It will ask your WANDb api key

# found here https://wandb.ai/authorize?signup=true&ref=models

uv run wandb login --relogin

# Otherwise we would log like this normally

uv run wandb login

# Create the folders and download the trained policy files

mkdir -p ~/rl_policies/s7ln45vo

cd ~/rl_policies/s7ln45vo

uv run --project ~/pal_mjlab wandb pull s7ln45vo -e rdaneellivaw -p mjlab

mv ~/rl_policies/s7ln45vo ~/rl_policies/loco_s7ln45vo_mjlab

Here we placed the policy into the folder ~/rl_policies.


### This folder is accessible by teh docker. This way, we have a file connection between the running Docker and the outside of the parent system.

### See here for example, we created a file in the parent system outside the Docker, but it's also inside the Docker container.

### Now we start the docker and execute the following comands inside it to check that our policy is inside the docker also.
PLEASE close the previous docker launch if you still have it running.

Execute in GPU-DOCKER Terminal #1

# For running once downloaded

docker start pal_kangaroo_sim && docker attach pal_kangaroo_sim

Execute in GPU-DOCKER Terminal #1

ls ~/rl_policies/loco_s7ln45vo_mjlab

mv ~/rl_policies/loco_s7ln45vo_mjlab ~/rl_ws/src/pal_policy_deployer/pal_policy_deployer/models/loco

Execute in GPU-DOCKER Terminal #1

#Once started, open a Terminator instance running:

#Shell

terminator -u

Inside these three terminals, execute a default policy that the people at Pal Robotics have already trained really well:

Step3 : Start default already trained policy by Pal Robotics

Execute in GPU-DOCKER Terminal #1


> **⚠️ Note:** WARNING: Please wait until the first command kangar∞palphysicssiμla→r makes the RVIZ appear with the robot standing, to launch the second command in terminal 2.
Execute in GPU-DOCKER-DIVISION Terminal #1

# And split ot horozontally  CTRL+SHIFT+O three


## # T1
roslaunch kangaroo_pal_physics_simulator kangaroo_pal_physics_simulator.launch


> **⚠️ Note:** NOTE we are setting here now our VERSION.
YOU will have to put YOUR VERSION, your YOUR_RUN_ID.

Execute in GPU-DOCKER-DIVISION Terminal #2

# T2, YOUR_RUN_ID, for example following teh exmaple commands here ist shoudl be s7ln45vo

roslaunch pal_policy_deployer kang_rl_deployer.launch model:=YOUR_RUN_ID

#roslaunch pal_policy_deployer kang_rl_deployer.launch model:=s7ln45vo

Output

If you see this, then the controller loaded correctly:

[INFO] [1770907958.476543, 39.822000]: Loading controller: subscriber_controller

[INFO] [1770907962.491923, 41.117000]: Controller Spawner: Loaded controllers: subscriber_controller

[INFO] [1770907962.501926, 41.120000]: Started controllers: subscriber_controller

Execute in GPU-DOCKER-DIVISION Terminal #3


## # T3
rostopic pub /cmd_vel geometry_msgs/Twist "linear:

x: 0.5

y: 0.0

z: 0.0

angular:

x: 0.0

y: 0.0

z: 0.0"

# Turn

rostopic pub /cmd_vel geometry_msgs/Twist "linear:

x: 0.0

y: 0.0

z: 0.0

angular:

x: 0.0

y: 0.0

z: 1.0"

# T3 : Also you can apply forces to teh robot

rostopic pub /simulator/external_wrench pal_simulation_msgs/ExternalWrench "header:

seq: 0

stamp: {secs: 0, nsecs: 0}

frame_id: 'base_link'

link_name: 'base_link'

wrench:

force: {x: 100.0, y: 0.0, z: 0.0}

torque: {x: 0.0, y: 0.0, z: 0.0}

application_point: {x: 0.0, y: 0.0, z: 0.0}

duration: {secs: 1, nsecs: 0}"

# Push in Y axis

rostopic pub /simulator/external_wrench pal_simulation_msgs/ExternalWrench "header:

seq: 0

stamp: {secs: 0, nsecs: 0}

frame_id: 'base_link'

link_name: 'base_link'

wrench:

force: {x: 0.0, y: 100.0, z: 0.0}

torque: {x: 0.0, y: 0.0, z: 0.0}

application_point: {x: 0.0, y: 0.0, z: 0.0}

duration: {secs: 1, nsecs: 0}"

You should now get your walking policy making the robot walk.

Obviously not two policies are alike , so your will behave differently.

Here we push it in th eY axis for 1 second.

Exercise

Train in the Rough environment overnight.

Execute in GPU Terminal #1

conda deactivate

cd ~/pal_mjlab

uv run train Mjlab-Velocity-Rough-Pal-Kangaroo --env.scene.num-envs 10


### See that the training environments went way down. The reason is that in the current instances, it can't handle more than 10 robots training at the same time.
You can use 500 or more without the GPU memory running out, but we get the error:

height field collision overflow, number of collisions >= 50 - please adjust resolution: decrease the number of hfield rows/cols or modify size of colliding geom


### You could run the training like that, but the physics won't be accurate, which would mean that the policy learns to walk in a world with different physics rules than the real world, which is not what we want.
So we lower the number of environments, making the training slower but more accurate.

At the end of the training of 30.000 iterations you should get this:

################################################################################

Learning iteration 29999/30000

Computation: 143 steps/s (collection: 1.569s, learning 0.108s)

Mean action noise std: 0.44

Mean value_function loss: 0.0300

Mean surrogate loss: -0.0576

Mean entropy loss: 11.7419

Mean reward: 1.46

Mean episode length: 97.88

Episode_Reward/track_linear_velocity: 0.0024

Episode_Reward/track_angular_velocity: 0.0413

Episode_Reward/upright: 0.0637

Episode_Reward/pose: 0.0351

Episode_Reward/body_ang_vel: -0.0024

Episode_Reward/angular_momentum: -0.0261

Episode_Reward/dof_pos_limits: -0.0043

Episode_Reward/action_rate_l2: -0.0776

Episode_Reward/air_time: 0.0054

Episode_Reward/foot_clearance: -0.0042

Episode_Reward/foot_swing_height: -0.0042

Episode_Reward/foot_slip: -0.0007

Episode_Reward/soft_landing: -0.0001

Episode_Reward/self_collisions: -0.0045

Curriculum/terrain_levels: 0.0000

Curriculum/command_vel/lin_vel_x_min: -2.0000

Curriculum/command_vel/lin_vel_x_max: 3.0000

Curriculum/command_vel/lin_vel_y_min: -1.0000

Curriculum/command_vel/lin_vel_y_max: 1.0000

Curriculum/command_vel/ang_vel_z_min: -0.7000

Curriculum/command_vel/ang_vel_z_max: 0.7000

Metrics/twist/error_vel_xy: 0.2493

Metrics/twist/error_vel_yaw: 0.1422

Episode_Termination/time_out: 0.0000

Episode_Termination/fell_over: 0.0000

Episode_Termination/illegal_contacts: 1.1250

Metrics/angular_momentum_mean: 4.1258

Metrics/air_time_mean: 0.0168

Metrics/peak_height_mean: 0.0188

Metrics/slip_velocity_mean: 0.1969

Metrics/landing_force_mean: 380.1408

--------------------------------------------------------------------------------

Total timesteps: 7200000

Iteration time: 1.68s

Time elapsed: 12:29:41


## ETA: 00:00:01
wandb:

wandb: 🚀 View run 2026-02-11_19-50-49 at:

wandb: Find logs at: wandb/run-20260211_195055-gi939djp/logs

In WANDB you should see that after around the 5000 episodes, it stabilises.

And if you execute now teh policy you shoudl see something like this:

Execute in GPU Terminal #1

Remember to get the Policy path form the Wandb page.

conda deactivate

cd ~/pal_mjlab

uv run play Mjlab-Velocity-Rough-Pal-Kangaroo --wandb-run-path rdaneellivaw/mjlab/gi939djp

You should see that the robot stays upright.

Now let's execute it in the Docker system to validate it, move it around, and see how it performs.

First , lets download the docker clean, just in case its setup wrong:

Execute in GPU Terminal #1

# Becuase this docker does sets the hosts insid ethe docker, previous versions might be insid eyour instance with teh wrong IP, so better remove teh docker and redownload it

docker rm -f pal_kangaroo_sim

# Redownload it and setup

xhost +

docker run --gpus all -it \

--env LOCAL_USER_ID=$(id -u) \

--env LOCAL_GROUP_ID=$(id -g) \

--env LOCAL_GROUP_NAME=$(id -gn) \

--env DISPLAY \

--env QT_X11_NO_MITSHM=1 \

--env="NVIDIA_DRIVER_CAPABILITIES=all" \

--env="NVIDIA_VISIBLE_DEVICES=all" \

--volume=/tmp/.X11-unix:/tmp/.X11-unix:rw \

-v /run/user/$(id -u)/keyring/ssh:/run/host_ssh_auth_sock \

-e SSH_AUTH_SOCK=/run/host_ssh_auth_sock \

--net host \

--privileged \

-v /home/$USER/rl_policies:/home/user/rl_policies \

-v /var/run/docker.sock:/var/run/docker.sock \

--name pal_kangaroo_sim \

registry.gitlab.com/pal-robotics-public/kangaroo_robot/pal-kangaroo-rl-inference

We have to now download the policy in the correct folder accessible to the Docker that we will launch after for validation:

Execute in GPU Terminal #1

# IF the login is for rdaneelolivaw, please execute the relogin to change it to your own

conda deactivate

cd ~/pal_mjlab

uv run wandb login --relogin


## # -------- CONFIG --------
RUN_ID="gi939djp"

ENTITY="rdaneellivaw"

PROJECT="mjlab"

PREFIX="loco"

PAL_DIR="$HOME/pal_mjlab"

POLICIES_DIR="$HOME/rl_policies"

# ------------------------

conda deactivate

cd "$PAL_DIR"

uv run wandb login

mkdir -p "$POLICIES_DIR/$RUN_ID"

cd "$POLICIES_DIR/$RUN_ID"

uv run --project "$PAL_DIR" wandb pull "$RUN_ID" -e "$ENTITY" -p "$PROJECT"

mv "$POLICIES_DIR/$RUN_ID" "$POLICIES_DIR/${PREFIX}_${RUN_ID}_${PROJECT}"

It will take around 15 minutes to download everything:

Downloading: mjlab/gi939djp

File 2026-02-11_19-50-49.onnx  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

File artifact/2474094397/wandb_manifest.json  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

File config.yaml  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

File model_0.pt  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

File model_100.pt  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

...

File model_5050.pt  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

File model_5100.pt  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

File model_5150.pt  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

File model_5200.pt  [&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&]  100%

Start the docker:

Execute in GPU Terminal #1

# For running once downloaded

docker start pal_kangaroo_sim && docker attach pal_kangaroo_sim

#Once started, open a Terminator instance running:

#Shell

terminator -u

Now let's go inside the Docker and check that our molicy is there accessible:

Execute in GPU-DOCKER Terminal #1

ls ~/rl_policies/loco_gi939djp_mjlab

mv ~/rl_policies/loco_gi939djp_mjlab ~/rl_ws/src/pal_policy_deployer/pal_policy_deployer/models/loco

Now this will open a new terminator terminal that is isnide teh docker running.

Execute in GPU-DOCKER Terminal #1

#Once started, open a Terminator instance running:

#Shell

terminator -u

Divide it in three with CTRL+SHIFT+O and execute these three commands in those three sections.


> **⚠️ Note:** NOTE that you have to replace the RUN_ID for yours.
Execute in GPU-DOCKER Terminal #1, 2 and 3

# And split ot horozontally  CTRL+SHIFT+O three


## # T1
roslaunch kangaroo_pal_physics_simulator kangaroo_pal_physics_simulator.launch

# T2: WAIT UNTIL T1 command is stable ( 30 seconds )

roslaunch pal_policy_deployer kang_rl_deployer.launch model:=gi939djp


## # T3
rostopic pub /cmd_vel geometry_msgs/Twist "linear:

x: 10.0

y: 0.0

z: 0.0

angular:

x: 0.0

y: 0.0

z: 0.0"

# T3 : Push also to test

rostopic pub /simulator/external_wrench pal_simulation_msgs/ExternalWrench "header:

seq: 0

stamp: {secs: 0, nsecs: 0}

frame_id: 'base_link'

link_name: 'base_link'

wrench:

force: {x: 100.0, y: 0.0, z: 0.0}

torque: {x: 0.0, y: 0.0, z: 0.0}

application_point: {x: 0.0, y: 0.0, z: 0.0}

duration: {secs: 1, nsecs: 0}"

The training in our case wasn't very succesfull, but your results may vary:

Machine Learning in Robotics - VLAs


---

V1

Visual Language Action models (VLAs)

> **Duration:** Estimated time to completion for the whole unit: 90 min
> **Objective:** nderstand what VLAs are and what they do.
Introduction

Up until now, we have learned how to control a humanoid robot in various ways:

Control with a program by publishing motor commands directly.


### In the Unitree G1 case, this is done by subscribing/publishing to DDS topics (rt/lowstate, rt/lowcmd).
This approach can be useful for pre-recorded motions, but not for complicated tasks (i.e. how does a program like this control the gait of a humanoid and a manipulation task?)

Control through libraries created by robot manufacturer.

In the Unitree G1 case, the Unitree SDK is used (C++/Python).


### This approach can be useful for combining low level commands (same as direct DDS control), and high level commands like Move(), which leverages work already done by unitree.
⬆️ These are the "traditional" methods.


### With the advent of machine learning, new exciting methods have been introduced. We've already seen what Reinforcement Learning can do by generating policies that can teach a humanoid how to walk or perform complicated motions.
In the Unitree G1 case, the robot learns how to walk using reinforcement learning ➡️ gait policies.


### In the Unitree G1 case, the robot can track complex motions coming from retargeted videos using reinforcement learning ➡️ "dance" policies.
So, what's missing?

These RL techniques are hard to scale. i.e., how to use this to perform an actual useful task?


### With these setups, it's hard to specify behavior. Everyone wants to tell humanoids to go and pick up something useful in a factory.
Even with reinforcement learning, there is no semantic understanding. The robots don't actually know they are walking or dancing. The policies inside are just trying to output numbers that maximize some rewards (a trajectory, a balancing setup, etc.)

That's where the next concept of Visual Language Action (VLA) models come in.

They are the latest technology in robotics that tries to give robots a more complete understanding of the world, closer to how we humans understand it. Not just numbers, but concepts through language, translating to physical actions. Have you seen any of the new 500k "Physical AI experts" on LinkedIn?

What is a VLA?

A VLA is an AI model trained on robot demonstration videos. The goal of them is to perform the next three steps:

Human gives instructions through language.

VLA Model interprets instructions + camera image.

VLA Model decides: "What should robot do next?" and ouputs an action.

🚫 VLAs DO NOT:

Send motor commands.

Replace low level controllers.

Know anything about robot kinematics.

An example of what an action might look like

What a VLA might spit out:

{

"left_arm":  [0.34, 0.76, 1.34, 0.77, 0.11, 1.62, 3.88],  # left arm joint positions

"right_arm": [0.65, 0.12, 1.01, 0.22, 0.66, 0.89, 0.02],  # right arm joint positions

"left_hand":  [0.12, 1.01, 0.22],  # left hand joint positions

"right_hand": [0.99, 0.28, 1.00],  # right hand joint positions

"navigate_command": [1.0, 0.0, 0.5],  # x, y, yaw velocity commands

}

⬆️ The contents of the action will change based on the robot and the data the VLA is trained with.

In order for VLAs to actually move a robot, these are still needed:

Motion controllers.

Inverse kinematics / whole body control.

Hardware drivers.

Evolution of VLAs


### VLAs come from Large Language Models (LLMs). They are basically ChatGPT with things on top of it. I recommend this great video, the diagrams and explanations below are based on it.
1. Large Language Models (LLMs)


### Accept text as input and predicts the next "text tokens" (a word, part of a word, punctuation, even whitespace).
A "transformer" (neural network) uses these input text to predict good "next-tokens".

Output text tokens are continuously re-fed to keep predicting the next possible word.

2. Visual Language Models (VLMs)

Accepts text and images as input and predicts the next text tokens and, optionally, images.


### ChatGPT is now a VLM. When it first came out, it was just an LLM. You can upload a picture to it and it'll understand it.

### A "visual backbone" (an image-specific model) is added to the LLM and the images are "tokenized" so they can be inputs to the LLM.
3. Visual Language Action models (VLAs)

Accepts text, images and robot state as inputs, and predicts robot actions


### Nothing new conceptually. Transformer is extended or "fine-tuned" to output action tokens, representing what a robot can do. No text tokens anymore (but still pretty much a bunch of string arrays).
Action head


### An action head is added to the end of the transformer so it turns the action token into actual robot actions over time (i.e. joint deltas over the next 100 control steps).

### Diffusion transformers treat action generation as denoising. Start from a noisy action sequence and keep refining until you have a clean trajectory based on observations and instruction.
This is a training "trick" to generate better trajectories.


> **⚠️ Note:** ⚠️ Not all VLAs are like this; this is a design decision and an active research field. This is just to explain, and we take Isaac GR00T's design.
Training a VLA

All of these machine learning algorithms that involve neural networks require training. Looking back at what we've trained:


### RL gait and motion tracking are trained by a PPO algorithm: actor/critic, rewards/penalties system. That teaches the robot to keep balance or follow a certain motion.

### So how do you train a VLA? Same way as ChatGPT and with datasets that come from robot demonstrations. VLAs use imitation learning to "fine-tune" the actions they are supposed to perform.
The robot demonstrations often come from human teleoperation.


### So the VLA is trained with a specific task you want the robot to perform. In theory, the datasets can increase to do everything you can imagine.
🏁 This "fine tuning" training produces what is called a model checkpoint, a VLA that knows how to perform the task you tried to teach it with the dataset.


### Later, we'll see how to create these robot demonstration datasets and even generate synthetic datasets (1000 demonstrations from 10 you actually recorded) using Isaac Lab Mimic.
So, you want to demonstrate a task that the robot will be encountering live:

Executing VLA actions


### This part is what all the AI people don't tell you, because they assume it's easy. It's not. It's hard.

### You can't move a robot with a dictionary. A controller must be used to parse the VLA action and actually execute it in the robot.
Why is the controller implementation hard in the case of G1?


### Because you want the robot to walk around and perform actions with its hands. That means that the controller must run the actual gait.onnx policy, accept the action coming from the vla, and somehow merge it into the gait policy so the robot doesn't fall and accepts a "joystick" velocity command at the same time.
The promise of VLAs

So why all the buzz? Because this structure is very promising! That means that the demonstration datasets can increase, and the VLA will be able to perform many tasks!!

For example, autonomous navigation without having to develop the classic ROS Nav2 process!! (No mapping software, no localization software, no path planning software, no path planning to controller software. Only "go to chair" and the VLA does it!

BUT! This is very early stage still. If you expect your humanoid to replace a auto-factory worker and perform all tasks perfectly tomorrow, you're


# 5. Unitree G1 Course: GR00T Part 1 - Data Generation

---

V7


## Data collection in Mujoco using decoupled_wbc from GR00T-WholeBodyControl

### Launching the Docker container
Open a terminal by right clicking on the desktop, and run this command to start the GR00T-WholeBodyControl docker container:

cd ~/Projects/GR00T-WholeBodyControl/decoupled_wbc

./docker/run_docker.sh --install


### The docker container may take up to ~30 seconds to start. In the meantime, let's start the OpenCV handtracking script.

### Starting the hand-tracking script
Click the "Camera Stream" button (next to the GPU button) at the bottom of the screen.

Click the dropdown menu and select your camera, then click "Start Stream".

Open another separate terminal by right clicking on the desktop. Run these commands to start the hand-tracking script:

cd ~/opencv_handtracking

conda activate opencv_handtracking

python handtracking.py


### Competition Time: Let's split into two teams!
Team LEFT: The left side of the room will push the block to the left

python decoupled_wbc/scripts/deploy_g1.py \

--interface sim \

--camera_host localhost \

--sim_in_single_process \

--simulator robocasa \

--image-publish \

--enable-offscreen \

--env_name ManipBlockToZoneLeftDC \

--hand_control_device=opencv \

--body_control_device=opencv \

--no-wrist \

--no-add_stereo_camera \

--camera-port 5557 \

--no-view_camera

Team RIGHT: The right side of the room will push the block to the right

python decoupled_wbc/scripts/deploy_g1.py \

--interface sim \

--camera_host localhost \

--sim_in_single_process \

--simulator robocasa \

--image-publish \

--enable-offscreen \

--env_name ManipBlockToZoneRightDC \

--hand_control_device=opencv \

--body_control_device=opencv \

--no-wrist \

--no-add_stereo_camera \

--camera-port 5557 \

--no-view_camera

After a few seconds, you should see your terminal split into three windows:


### Hand-tracking gestures
These are the hand-tracking gestures that you will use to record data.

Let's test it out first to get used to it!


### Verify recorded videos

### After recording your demonstrations, a new dataset will appear in the directory ~/Projects/GR00T-WholeBodyControl/outputs/<Date>_<Time>-G1-sim.
Let's view the videos that your recorded. They are located in: ~/Projects/GR00T-WholeBodyControl/outputs/<Date>_<Time>-G1-sim/videos/chunk-000/observation.images.ego_view

Right click on the desktop and open with VLC:


### Check all of your videos to make sure the recordings are good. If you have any bad recordings, we can discard them.

### Discarding bad episodes
If there is a bad demonstration in your videos, open the info.json in your dataset. Find the discarded_episode_indices tag in the json:

# ...

"discarded_episode_indices": [], # <-- Add your discarded episode indices here, e.g., [0, 1, 2, ...]

# ...


## Creating HuggingFace Repo and Uploading

### HuggingFace is a platform for storing and sharing models, datasets, etc. It is like GitHub but for large files.
Let's create an account and Access Token first:

After saving your Access Token, we can use it to login to HuggingFace in the terminal.

First logout of our account:

hf auth logout

Press Ctrl + Shift + V to paste your Access Token and press Enter

Make sure to not add token as Git credential: press n and Enter

hf auth login


### Create a Repo on HuggingFace
There are 2 options for creating a new repo on HuggingFace:

From the CLI (replace USER_NAME and REPO_NAME)

hf repo create <USER_NAME>/<REPO_NAME> --repo-type dataset


### Uploading files to HuggingFace
cd ~/Projects/GR00T-WholeBodyControl/outputs/

hf upload <USER_NAME>/<REPO_NAME> . --repo-type dataset

Here we can inspect the dataset and the specific files


### Last Step
Paste your dataset name in our Google Spreadsheet that we will send in Discord!


## Real robot data collection using decoupled_wbc from GR00T-WholeBodyControl
The most successful way of obtaining real robot demonstrations to generate datasets in our experience was using the data collection stack from decoupled_wbc. However, this is still in active development and it only worked for the simulation. We had to do some changes in order to be able to run the stack in the real robot. Check here for a summary of the changes: https://github.com/royito55/GR00T-WholeBodyControl/tree/main/decoupled_wbc

To generate real datasets, we need:

Control loop: runs the gait policy as well as the ability to control the arms while walking.

Camera driver: default realsense2 ROS 2 launch provides a simple way to obtain images

ROS-ZMQ bridge for camera: the decoupled_wb stack (and GR00T inference) requires ZMQ image publishing. A bridge was created to provide images coming from ROS 2 in ZQM


### PICO teleop: allows for teleoperation through PICO VR headset. This is NOT the same as the teleoperation with GEAR-SONIC.
Data exporter: a program that records the episodes and saves them in the corract format.


### Control loop
cd ~/git-repo/GR00T-WholeBodyControl && source .venv_teleop/bin/activate

python decoupled_wbc/control/main/teleop/run_g1_control_loop.py --interface real --robot-variant g1_23dof_compat --no-with-hands --zmq-control-goal-host 192.168.123.222 --zmq-control-goal-port 5556


### Note the robot variant and the --no-with-hands flags. These are particular to the robot we have. --zmq-control-goal-host and --zmq-control-goal-port are there because an external PC will be the one receiving the VR teleoperation commands, and forwarding to the robot through ZMQ.

### Camera driver
source /opt/ros/humble/setup.bash && ros2 launch realsense2_camera rs_launch.py


### Camera ROS2-ZMQ bridge
cd ~/git-repo/GR00T-WholeBodyControl && source .venv_teleop/bin/activate

python decoupled_wbc/control/sensor/ros2_zmq_camera_bridge.py

This bridge forwards a single ROS image topic as ego_view.


### Camera viewer (optional)
Needs an ssh -X session to visualize.

cd ~/git-repo/GR00T-WholeBodyControl && source .venv_teleop/bin/activate

python decoupled_wbc/control/main/teleop/run_camera_viewer.py --camera_host localhost --camera_port 5555 --fps 20.0


### PICO teleop
In this setup, the teleop loop is ran in an external PC.

Start the XRoboToolkit PC service:

bash /opt/apps/roboticsservice/runService.sh

Run teleop loop:

cd ~/git-repo/GR00T-WholeBodyControl && source .venv_teleop/bin/activate

python decoupled_wbc/control/main/teleop/run_teleop_policy_loop.py --hand_control_device=pico --body_control_device=pico --zmq-publish-port 5556

In PICO, run XRobotics App.

Select robot IP in popup.

Toggle Head and Controller.

Toggle SEND

You should be able to move the robot (lower body) by moving controller joysticks.


### To teleop arms, copy arm position and push menu + right trigger. Arms should start moving immediately.

### Data exporter
cd ~/git-repo/GR00T-WholeBodyControl && source .venv_teleop/bin/activate

python decoupled_wbc/control/main/teleop/run_g1_data_exporter.py --data_collection_frequency 20 --root_output_dir outputs --lower_body_policy gear_wbc --wbc_model_path policy/GR00T-WholeBodyControl-Balance.onnx,policy/GR00T-WholeBodyControl-Walk.onnx --camera_host localhost --camera_port 5555 --no-add_stereo_camera

Enter task prompt.

Select whether to add recording to existing dataset.

Recording does not start automatically.


### With the control-loop terminal focused, press c once to start recording and press c again to stop and save the episode.

### Pressing Ctrl+C in the exporter process is treated as an interruption. If an episode is in progress, it is marked as discarded rather than cleanly closed.
Press x while recording to discard the current episode.


## 5.1: Isaac Mimic Pipeline

## 5.2: Let's start

### Lets access again to the GPU NVIDIA cloud computer that will allow you to train your policies during the workshop.
Open the GPU instance by clicking on the following icon in the bottom menu bar:

🔍 A new window should open and the instance starts loading. When it's ready, you can login as user and a desktop like this should appear:

In this new GPU desktop, open a terminal Right Click -> Open Terminal Here.

You can also open VSCode for editing files. Right Click -> Applications -> Developement - VSCode

In this new GPU desktop, open a terminal MIDDLE Click -> See all the windows oppened

Very useful for finding the windows you have minimised.

1) The first step is to generate our dataset of the robot doing a certain task, where we save the robot joints values and the RGB cameras during the process of performing the task.


## 5.3: Let's create a single task example dataset
For training Isaac-GR00T, we need a dataset of examples of the task to be performed.

Let's create a single one to understand the process.


### We will create a task of just throwing the object of the table out of table. We will call it "clean the table task".

## NOW EXECUTE IN THE REMOTE GPU INSTANCE PLEASE
Execute in REMOTE INSTANCE GPU Terminal #1

cd ~/isaaclab

git pull

conda activate env_isaaclab_51

./isaaclab.sh -p scripts/tools/record_demos.py \

--device cpu \

--task Isaac-PickPlace-Camera-G1-v0 \

--teleop_device opencv_handtracking \

--dataset_file ./datasets/steering_wheel_student.hdf5 \

--num_demos 2 \

--enable_pinocchio


### The first start of IsaacSim takes around 10 minutes, so let's walk through the hand tracking script installation.

## 5.4: Setting up Hand-tracking for Tele-operation
In order to tele-operate the robot, we will have: 1) The simulation running in the cloud system GPU instance 2) The hand tracking running on our local computer, which sends wrist pose and finger data to the instance via UDP


### 5.4.1: Miniconda3 Installation (Windows)
Download the Miniconda installer from: https://www.anaconda.com/download/success

Double-click the installer and continue clicking Next with the default settings:

After installing, you should now have a program called Anaconda Prompt in Windows search or MacOS spotlight:

Now, we can install Git in Anaconda Prompt:

conda install -c anaconda git

Accept the Anaconda Terms of Service by pressing a and then Enter:

Press y and then Enter to proceed with the installation:


### Now that we have Git, we can clone our opencv_handtracking repo. Feel free to use cd to navigate to another directory, but the default location will also work.
git clone https://github.com/RGroza/opencv_handtracking.git

Now, we can cd into opencv_handtracking and create the conda environment:

cd opencv_handtracking

conda env create -f environment.yml

Now, we activate the opencv_handtracking conda environment:

conda activate opencv_handtracking


### 5.4.2: Miniconda3 Installation (Mac)

## 5.4.3: Hand-tracking Script Setup (Linux)
Execute the following commands in the GPU Instance terminal


### You will have to use the copy icon on the top left corner of the GPU instance window to be able to copy commands back and forth form inside the GPU instance.

## NOW EXECUTE IN YOUR LOCAL COMPUTER PLEASE
Execute in LOCAL COMPUTER Terminal #1

cd ~

mkdir ~/g1_puppet

cd ~/g1_puppet

git clone https://github.com/RGroza/opencv_handtracking.git

cd ~/g1_puppet/opencv_handtracking

# We deactivate any conda env you might have already connected

conda deactivate

# We create the new environment

conda env create -f environment.yml

Lets wait until you have it installed:

Activate the environment

Execute in LOCAL COMPUTER Terminal #1

cd ~/g1_puppet/opencv_handtracking

conda activate opencv-handtracking

You should see something like that in the terminal prompt, with the (opencv-handtracking):

Veify that its working:

Execute in LOCAL COMPUTER Terminal #1

python -c "import cv2, mediapipe, numpy, scipy; print('Imports OK')"

Output should be:

Imports OK

Now you can launch the script python handtracking.py, that will record your movements and send them to the remote instance simulation:


## 5.5: Start Hand-tracking
Execute in LOCAL COMPUTER Terminal #1

cd ~/g1_puppet/opencv_handtracking

python handtracking.py

You should now see your WebCam feed and the hand tracking working:


### 5.5.1: Calibration & Gestures
Click on the OpenCV window to focus on it:

Hold your hand with palm facing the camera ~20cm away --> Press '4'

Then, hold hand ~50cm away from camera --> Press '5'

USE THE LEFT HAND FOR CALIBRATING, NOT THE RIGHT HAND. SHOW the LEFT HAND TO THE SCREEN

You can use gestures to start and stop the demonstration recording in IsaacSim:

Hold hands palms facing each other like the G1 robot in the sim --> START

Hold hands up high and far apart with palms facing the camera --> STOP and RESET

[ PENDING... couldnt start it START or STOP gestures]

If gestures are not responding you can manually prompt them using keypresses while focussed on OpenCV window:

Press '1' --> START

Press '2' --> STOP

Press '3' --> RESET

In the terminal you shoudl see the message:

Sending callback number: 1/2 or 3

It's really fast but you should see it.

This means that the keys for replacing gestures shoudl work.


### 5.5.2: Connect Hand-tracking to GPU Instance
Now you can start the opencv_handtracking script locally on your machine.

But before, we need to find the IP of the GPU instance using:

Execute in REMOTE INSTANCE GPU Terminal #1

curl api.ipify.org

Get the Ip , and us ethe paste icon to extract it form the GPU instance to your local setup.

In this case its 34.240.220.32 yours will be different.

Copy this IPv4 address. Then in the Anaconda Prompt window, start the hand-tracking script and paste the IP address in the command:

Execute in LOCAL COMPUTER Terminal #1

cd ~/g1_puppet/opencv_handtracking

conda activate opencv-handtracking

export REMOTE_IP=34.240.220.32

python handtracking.py --udp_ip $REMOTE_IP

You should now:

Calibrate with 4, and 5

Press 1 to start moving the arms

Press 3 to reset

Press 2 to STOP.


## REMINDER
Remember to calibrate:

Hold your hand with palm facing the camera ~20cm away --> Press '4'

Then, hold hand ~50cm away from camera --> Press '5'

If gestures are not responding you can manually prompt them using keypresses while focussed on OpenCV window:

Press '1' --> START

Press '2' --> STOP

Press '3' --> RESET


### No Go the simulation aand see that when you press 1 in the Webcam capture windo in your local computer, the robot arm starts moving.
Add these arguments to the commmand to enable camera recording in IsaacSim (only for tasks with "Camera" in the name):

--enable_cameras \ --rendering_mode balanced \

Execute in REMOTE INSTANCE GPU Terminal #1

cd ~/isaaclab

conda activate env_isaaclab_51

./isaaclab.sh -p scripts/tools/record_demos.py \

--device cpu \

--task Isaac-PickPlace-Camera-G1-v0 \

--teleop_device opencv_handtracking \

--dataset_file ./datasets/steering_wheel_student.hdf5 \

--num_demos 2 \

--enable_pinocchio

So lets record 5 examples, that we state --num_demos 5.

Successful examples in this task means:

Place the steering wheel inside the basket on the right

Some indications and tips:

Do slow movements.


### Try to never place the hands out of frame, otherwise the robot will do sudden movements and its not good at all.
Move your torso to turn, it helps.


### Try extreme hand positions like tips facing the camera, becaus ethat is very dificult to track. Try always palms facing the camera or facing you, or any other hand position that the camera can see clearly your hand.
Close the fingers by making a fist.

The recording has finished if you get this message and the simulation closes:

Success condition met! Recording completed.

Recorded 5 successful demonstrations.

All 5 demonstrations recorded.

Exiting the app.

Recording session completed with 5 successful demonstrations

Demonstrations saved to: ./datasets/dataset_pick_place_g1.hdf5

[503.459s] Simulation App Shutting Down


## 5.6: Replay Demonstrations

#### Replay demos
Let's check that the demos were recorded:

Execute in REMOTE INSTANCE GPU Terminal #1

./isaaclab.sh -p scripts/tools/replay_demos.py \

--device cpu \

--task Isaac-PickPlace-Camera-G1-v0 \

--dataset_file \

./datasets/steering_wheel_student.hdf5 \

--enable_pinocchio

ALTERNATIVE: If you don't record your demonstrations, you can use our steering_wheel.hdf5 instead:

./isaaclab.sh -p scripts/tools/replay_demos.py \

--device cpu \

--task Isaac-PickPlace-Camera-G1-v0 \

--dataset_file \

./datasets/steering_wheel.hdf5 \

--enable_pinocchio


## 5.7: Anotate Demonstrations
Now we need to annotate, which is in essence to divide the main task examples into smaller tasks.

This has to be done manually.

Execute in REMOTE INSTANCE GPU Terminal #1

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \

--device cpu \

--task Isaac-PickPlace-Camera-G1-Mimic-v0 \

--input_file ./datasets/steering_wheel_student.hdf5 \

--output_file ./datasets/steering_wheel_student_annotated.hdf5 \

--enable_pinocchio

ALTERNATIVE: If you don't record your demonstrations, you can use our steering_wheel.hdf5 instead:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \

--device cpu \

--task Isaac-PickPlace-Camera-G1-Mimic-v0 \

--input_file ./datasets/steering_wheel.hdf5 \

--output_file ./datasets/steering_wheel_annotated.hdf5 \

--enable_pinocchio

You should get something like this in the terminal, where it states:

Lets analize the output of the script:

[INFO]: Time taken for simulation start : 3.810307 seconds

[INFO] Command Manager:  <CommandManager> contains 0 active terms.

+------------------------+

|  Active Command Terms  |

+--------+-------+-------+

| Index  | Name  |  Type |

+--------+-------+-------+

+--------+-------+-------+

[INFO] Event Manager:  <EventManager> contains 1 active terms.

+-------------------------------------+

| Active Event Terms in Mode: 'reset' |

+--------+----------------------------+

| Index  | Name                       |

+--------+----------------------------+

|   0    | reset_scene_to_default     |

+--------+----------------------------+

[INFO] Recorder Manager:  <RecorderManager> contains 6 active terms.

+--------------------------------------------------+

|              Active Recorder Terms               |

+-------+------------------------------------------+

| Index | Name                                     |

+-------+------------------------------------------+

|   0   | record_initial_state                     |

|   1   | record_post_step_states                  |

|   2   | record_pre_step_actions                  |

|   3   | record_pre_step_flat_policy_observations |

|   4   | record_post_step_processed_actions       |

|   5   | record_pre_step_datagen_info             |

+-------+------------------------------------------+

[INFO] Action Manager:  <ActionManager> contains 1 active terms.

+-----------------------------------+

|  Active Action Terms (shape: 28)  |

+-------+---------------+-----------+

| Index | Name          | Dimension |

+-------+---------------+-----------+

|   0   | upper_body_ik |        28 |

+-------+---------------+-----------+

[INFO] Observation Manager: <ObservationManager> contains 1 groups.

+-----------------------------------------------+

|  Active Observation Terms in Group: 'policy'  |

+---------+------------------------+------------+

|  Index  | Name                   |   Shape    |

+---------+------------------------+------------+

|    0    | actions                |   (28,)    |

|    1    | robot_joint_pos        |   (43,)    |

|    2    | robot_root_pos         |    (3,)    |

|    3    | robot_root_rot         |    (4,)    |

|    4    | object_pos             |    (3,)    |

|    5    | object_rot             |    (4,)    |

|    6    | robot_links_state      |  (46, 13)  |

|    7    | left_eef_pos           |    (3,)    |

|    8    | left_eef_quat          |    (4,)    |

|    9    | right_eef_pos          |    (3,)    |

|    10   | right_eef_quat         |    (4,)    |

|    11   | hand_joint_state       |   (14,)    |

|    12   | object                 |   (13,)    |

+---------+------------------------+------------+

[INFO] Termination Manager:  <TerminationManager> contains 0 active terms.

+----------------------------+

|  Active Termination Terms  |

+--------+-------+-----------+

| Index  | Name  |  Time Out |

+--------+-------+-----------+

+--------+-------+-----------+

[INFO] Reward Manager:  <RewardManager> contains 0 active terms.

+-----------------------+

|  Active Reward Terms  |

+-------+------+--------+

| Index | Name | Weight |

+-------+------+--------+

+-------+------+--------+

[INFO] Curriculum Manager:  <CurriculumManager> contains 0 active terms.

+----------------------+

| Active Curriculum Terms |

+-----------+----------+

|   Index   | Name     |

+-----------+----------+

+-----------+----------+

Creating window for environment.

[INFO]: Completed setting up the environment...

Annotating episode #0 (demo_0)

Playing the episode for subtask annotations for eef "right".

Subtask signals to annotate:

- Termination:	['idle_right']

Press "N" to begin.

Press "B" to pause.

Press "S" to annotate subtask signals.

Press "Q" to skip the episode.


#### What Is “Annotation” Here?

### In this context, annotation means labeling parts of a demonstration episode with meaningful semantic signals.
You already have:

States (joint positions, root pose, object pose, etc.)

Actions (28D upper_body_ik)

Observations (EEF pose, object pose, etc.)

Full trajectory recorded

But raw trajectories are just numbers.

Annotation adds structure and meaning on top of that data.


#### What Is the Purpose?
Annotation is used to:

Segment the Demonstration Into Subtasks

For example, a pick-and-place demo might internally contain:

Move to object

Grasp

Lift

Move to target

Release

Return to idle

Without annotation, your model only sees:

state_t → action_t → state_t+1

With annotation, you tell it:

Frames 0–120 → “approach”

Frames 121–150 → “grasp”

Frames 151–260 → “transport”

Frames 261–280 → “release”


#### This is extremely useful for:
Hierarchical policies

Subgoal learning

Skill discovery

Conditioning VLA models

Behavior cloning with structured labels


### In our Case: What Is Being Annotated?
If you see the output you can see:

Subtask signals to annotate:

Termination: ['idle_right']


### So this environment wants us to annotate when the right end-effector reaches idle_right termination condition.

### That means: We are manually marking when a specific subtask is completed, in this case, placing the wheel in the basket.

### What we have to do in this case, is anotate when the right arm finishes the task by placing the wheel in the basket or above it.
When you finish the annotation, you will get something like this:

Exported 4 (out of 5) annotated episodes.

Successful task completions: 4

Exiting the app.

[1237.162s] Simulation App Shutting Down

(env_isaaclab_51) user@ip-172-31-35-197:~/isaaclab$


### Note that not all the apisodes were annotated, we only did that whithc the ones that performaed the task correctly of placing the wheel in the basket more or less.
Note that the sequence to make the annotations is:

1) Press N after CLICKING ON THE SIMULATION WINDOW

2) When you see that the task has been performed, press B to pause, and the S to record the annotation`

3) Then continue by pressing N again.


## 5.8: Generate the Dataset

### Now we need to generate SYNTHETIC EXAMPLES, by randomizing the examples we have slightly to be able to generate 1000 or whatever we want without having to do them by hand.

### This consumes A LOT of GPU and processing power so in the --generation_num_trials 1000 we will use --generation_num_trials 20, just to make it faster.
As for the --num_envs 20 are the multiple robot simulations that will be launched simulatneously.

Execute in REMOTE INSTANCE GPU Terminal #1

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \

--device cuda:0 \

--headless \

--num_envs 4 \

--generation_num_trials 20 \

--enable_pinocchio \

--input_file ./datasets/steering_wheel_student_annotated.hdf5 \

--output_file ./datasets/steering_wheel_student_generated.hdf5

ALTERNATIVE: If you don't record your demonstrations, you can use our steering_wheel.hdf5 instead:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \

--device cuda:0 \

--headless \

--num_envs 4 \

--generation_num_trials 20 \

--enable_pinocchio \

--input_file ./datasets/steering_wheel_annotated.hdf5 \

--output_file ./datasets/steering_wheel_generated.hdf5

This will generate 30 more examples syntheticaly.


## 5.9: Permanently Save the Dataset

### The GPU instances when closed, you will loose all the files generated, so its a good idea that we place those files in a permanent folder.
In TheConstruct platform case, there is a folder shared by both the GPU instance an dthe normal platform file system:

Execute in REMOTE INSTANCE GPU Terminal #1

ls ~/__REMOTE_WORKSPACE__

You should see the folders inside the TheConstruct platform system files /home/user.

Lets copy the dataset folder into the ~/__REMOTE_WORKSPACE__/policies_ws/

Execute in REMOTE INSTANCE GPU Terminal #1

cp -r ~/isaaclab/datasets ~/__REMOTE_WORKSPACE__/policies_ws

Now all the files inside that datasets folder should be TheConstruct Main platform.

From here you can right click on the folder and hit download to save it in your local system.

Now we are ready for the next unit: Dataset conversion.


# EXTRA: You can also Train an Isaac Mimic policy and validate it

## Training
./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \

--task Isaac-PickPlace-G1-v0 --algo bc \

--normalize_training_actions \

--dataset ./datasets/generated_dataset_pick_place_g1.hdf5


## Validating
./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \

--device cpu \

--enable_pinocchio \

--enable_cameras \

--rendering_mode balanced \

--task Isaac-PickPlace-G1-v0 \

--num_rollouts 50 \

--horizon 350 \

--norm_factor_min <NORM_FACTOR_MIN> \

--norm_factor_max <NORM_FACTOR_MAX> \

--checkpoint /PATH/TO/desired_model_checkpoint.pth


# 5. Unitree G1 Course: GR00T Part 2 - Data Conversion

## 5.1: Data Conversion in the Pipeline

### Once we have a .hdf5 file containing the demonstrations generated by Isaac Mimic, we need to convert this file into a LeRobot V2 dataset that can be used to finetune the GR00T model using Isaac-GR00T.

---

V3


### We will be using the IsaacLabEvalTasks repo to do this conversion. The goal is to have a LeRobot dataset that we can upload to HuggingFace. This dataset can then be used to fine-tune a GR00T model.

## 5.2: Let's try an example
Let's open VSCode to see the datasets:

Open the isaaclabevaltasks folder:

Open the terminal in VSCode (shortcut: Ctrl + ~) and activate the conda environment that we used previously:

conda activate env_isaaclab_51

pip install tyro pyarrow fastparquet av

git pull

Let's test the conversion script with a small dataset of 5 demonstrations:

python3 scripts/convert_hdf5_to_lerobot.py --task_name apple_5 --data_root ~/isaaclabevaltasks/datasets

episodes.jsonl: One line per episode: episode id + length + associated task strings

info.json: This is the dataset “manifest”. It tells the training code

Where to find per-episode tables and videos via templates like data_path and video_path

What features exist (state, action, video stream names, timestamps, rewards/dones, annotations) and their shapes/dtypes

modality.json: This tells GR00T how to assign the data to each robot joint (“how to slice arrays” from the parquet files)

task.jsonl: Contains the human prompt for the task

Now, we can see our demonstration videos! For this example apple_5 task, there are only 5 demonstrations done by a human (me!)

Let's convert a dataset that has some demonstrations generated by Isaac Mimic domain randomization:

cd ~/isaaclabevaltasks

python3 scripts/convert_hdf5_to_lerobot.py --task_name apple_20 --data_root ~/isaaclabevaltasks/datasets


### Now, you can see 20 demonstration videos. Notice how the robot hands are shaky and the movements are not as smooth as the human demonstrations.

## 5.3: Exercise: Convert your dataset from Isaac Mimic

### If you have a dataset that you generation in the Data Generation unit, then the first step is to copy that dataset over to isaaclabevaltasks.
ALTERNATIVE: If you don't have a dataset, you can use our's called steering_wheel_generated.hdf5

cp ~/isaaclab/datasets/steering_wheel_student_generated.hdf5 ~/isaaclabevaltasks/datasets/

Let's add a new task definition to isaaclabevaltasks to convert your dataset.

In VSCode, navigate to scripts/config/args.py, and define a new task:

class EvalTaskConfig(Enum):

# ...

# Pick and place apple 5 teleop demonstrations


## APPLE_5 = (
"Isaac-Apple-PickPlace-G1-v0",

"~/isaaclabevaltasks/datasets",

"Pick up the apple and place it on the plate.",

"apple_pick_place_annotated.hdf5",

5

)

# Pick and place apple 20 generated demonstrations

APPLE_20 = (                                            # Specified by: --task_name apple_20

"Isaac-Apple-PickPlace-G1-v0",

"~/isaaclabevaltasks/datasets",                     # Specified by: --root_dir <DIR>

"Pick up the apple and place it on the plate.",

"apple_pick_place_generated_small.hdf5",

5

)

# ...

# === COPY and PASTE this new task ===


## STEERING_WHEEL = (
"Isaac-PickPlace-Camera-G1-Mimic-v0",

"~/isaaclabevaltasks/datasets",

"Pick up the steering wheel and place it in the basket.",

"steering_wheel_student_generated.hdf5",

6

)


### Your dataset will be located in ~/isaaclab/datasets, so we can set the --data_root to ~/isaaclab/datasets. Be sure to set the <DATASET_NAME>.hdf5 correctly or the script will not find the file.
cd ~/isaaclabevaltasks

python3 scripts/convert_hdf5_to_lerobot.py --task_name steering_wheel --data_root ~/isaaclabevaltasks/datasets


## 5.4: Uploading Dataset to HuggingFace

### HuggingFace is a platform for storing and sharing models, datasets, etc. It is like GitHub but for large files.

### 5.4.1: Creating an Account
Let's create an account and Access Token first:

After saving your Access Token, we can use it to login to HuggingFace in the terminal:

hf auth login

Press Ctrl + Shift + V to paste your Access Token and press Enter

Make sure to not add token as Git credential: press n and Enter


### 5.4.2: Create a Repo on HuggingFace
There are 2 options for creating a new repo on HuggingFace:

From the CLI (replace USER_NAME and REPO_NAME)

hf repo create <USER_NAME>/<REPO_NAME> --repo-type dataset

On the website


### 5.4.3: Upload dataset to HuggingFace
Before uploading to HuggingFace make sure you navigate to the lerobot root directory of the dataset:

If you are uploading your own dataset, then it will be: ~/isaaclab/datasets/<YOUR_DATASET_NAME>/lerobot

If you are uploading own of the examples, then it will be: ~/isaaclabevaltasks/datasets/apple_pick_place_generated_small/lerobot

Make sure you are in the lerobot sub-directory.

hf upload <USER_NAME>/<REPO_NAME> . --repo-type dataset

We can check our new dataset on HuggingFace:

Here we can inspect the dataset and the specific files


## 5.5: Converting LeRobot V2 to V3
First we need to convert from LeRobot V2 -> V2.1 and then from V2.1 -> V3.

For V2 -> V2.1, we need to use the older v21 branch of our lerobot forked repo:

cd ~/lerobot

git checkout v21

git pull

export PYTHONPATH="$PWD"

python lerobot/common/datasets/v21/convert_dataset_v20_to_v21.py --repo-id=<USER_NAME>/<REPO_NAME>

For V2 -> V2.1, we need to switch branches to main and pull the latest changes:

git checkout main

git pull

python src/lerobot/datasets/v30/convert_dataset_v21_to_v30.py --repo-id <USER_NAME>/<REPO_NAME>

After converting to LeRobot V3, we can check the meta/info.json file in the HuggingFace repo:


# 5. Unitree G1 Course: Gr00t Part2 TRaining groot with LeRobot structure

---

V1


## 5.1: LeRobot Structure

### For training our already converted dataset, one of the patsh to do so is using the LeRobot infraestructure.
But what is LeRobot exactly?


### LeRobot aims to provide models, datasets, and tools for real-world robotics in PyTorch. The goal is to lower the barrier to entry so that everyone can contribute to and benefit from shared datasets and pretrained models.
Fetures:


### A hardware-agnostic, Python-native interface that standardizes control across diverse platforms, from low-cost arms (SO-100) to humanoids.

### A standardized, scalable LeRobotDataset format (Parquet + MP4 or images) hosted on the Hugging Face Hub, enabling efficient storage, streaming and visualization of massive robotic datasets.

### State-of-the-art policies that have been shown to transfer to the real-world ready for training and deployment.
Comprehensive support for the open-source ecosystem to democratize physical AI.

SOURCE LeRobot GIT, Source LeRobot Hugging Face


### In simple terms: it makes our life easier and our trainings usable for others, even with different robots.

### But...What does this have to do with our G1 robot training?
Well you see, this training Gr00t path uses as input datasets with the LeRobot format.


### First thing is that, this training has to be done in very big instances with at least arund 20GB VRAM minimum to start.
Otherwise you will get this error:

hidden_states = F.scaled_dot_product_attention(

torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 108.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 76.38 MiB is free. Process 3132 has 401.16 MiB memory in use. Including non-PyTorch memory, this process has 13.75 GiB memory in use. Of the allocated memory 13.34 GiB is allocated by PyTorch, and 296.73 MiB is reserved by PyTorch but unallocated. If reserved but unallocated memory is large try setting PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True to avoid fragmentation.  See documentation for Memory Management  (https://pytorch.org/docs/stable/notes/cuda.html#environment-variables)

We can launch it for a SINGLE GPU or MULTIGPU


## Dataset used for training
We can use the Dataset Visualiser, to visualise the dataset that we are oing to use.

In this case, the dataset is this one theconstruct-ai/pick_place_g1.

We only have the input that name theconstruct-ai/pick_place_g1.


## SINGLE GPU COMMAND
Here we will deactivate:

tune_diffusion_model, this will reduce GPU resources necesary


### Note that we also login into huggingface. This is so that we can download an dupload data when its done.

### We also use WANDB, so you need to also fech your WANDB API key WANDB KEY GENERATION PAGE. This way we can monitor the training and have also the training files there.
The AMI base launched in AWS is: AMI Name: Deep Learning Base AMI with Single CUDA (Ubuntu 22.04)

Supports EC2 instances: G4dn, G5, G6, Gr6, G6e, P4d, P4de, P5, P5e, P5en, P6-B200, P6-B300

Some extra info:

NVIDIA driver version: 580.126.09

CUDA versions available: cuda-13.0

Default CUDA version is 13.0

We will execute the script form the LeRobot GIT.

Execute in GPU INSTANCE Window Terminal #1

conda deactivate

conda activate lerobot

cd ~/lerobot

# Before you nee dto update

huggingface-cli login


## # HUGGING_FACE_API_KEY , NO
# Tokens are generated here: https://huggingface.co/settings/tokens

# We reloging to force teh setting of our user wandb

wandb login --relogin

# PLace your API key from https://wandb.ai/authorize

# Clean any folders there might be there

rm -r outputs/groot_pick_place_g1

python src/lerobot/scripts/lerobot_train.py --output_dir="outputs/groot_pick_place_g1" \

--save_checkpoint=true \

--batch_size=24 \

--steps=100 \

--save_freq=100 \

--eval_freq=100 \

--log_freq=10 \

--policy.type=groot \

--policy.push_to_hub=true \

--policy.repo_id="theconstruct-ai/groot-pick-place-g1" \

--policy.tune_diffusion_model=false \

--dataset.repo_id="theconstruct-ai/pick_place_g1" \

--dataset.revision="main" \

--wandb.enable=true \

--job_name="groot_pick_place_g1" \

--dataset.video_backend=pyav


## Key Arguments – VLA Training Command (LeRobot + GROOT Policy)

### Output & Run Identification
--output_dir="outputs/groot_pick_place_g1"
Directory where all artifacts are stored (checkpoints, logs, configs, metrics).

--job_name="groot_pick_place_g1"
Human-readable identifier for the experiment (used in logging systems like W&B and local metadata).


### Training Length & Cadence
--steps=100
Total number of optimizer update steps.
(Very short → typically used for smoke testing or debugging.)

--batch_size=24
Number of samples per training step.
Impacts:

GPU memory usage

Training stability (gradient variance)

Throughput

--log_freq=10
Log metrics every 10 training steps.

--save_freq=100
Save model checkpoint every 100 steps.

--eval_freq=100
Run evaluation every 100 steps.


### Checkpointing
--save_checkpoint=true
Enables periodic checkpoint saving.
Critical for:

Resuming interrupted training

Capturing intermediate models

Debugging training instability


### Policy Configuration
--policy.type=groot
Selects the GROOT VLA policy architecture.
Determines:

Model structure

Loss functions

Training loop behavior

--policy.tune_diffusion_model=false
Freezes the diffusion component of the model.
Trade-offs:

Lower GPU memory usage

Faster training

Reduced risk of destabilizing pretrained generative components

Reduced adaptability to the specific task


### Dataset Configuration
--dataset.repo_id="theconstruct-ai/pick_place_g1"
Dataset source repository (typically hosted remotely, e.g., Hugging Face).

--dataset.revision="main"
Dataset version (branch/tag/commit).
For strict reproducibility, pin to a commit hash instead of "main".

--dataset.video_backend=pyav"
Uses PyAV for video decoding.
Impacts:

Codec compatibility

Stability

Video loading performance


### Model Publishing
--policy.push_to_hub=true
Automatically uploads trained model artifacts to a remote hub.

--policy.repo_id="theconstruct-ai/groot-pick-place-g1"
Target repository where the trained policy is published.


### Experiment Tracking
--wandb.enable=true
Enables Weights & Biases logging.
Tracks:

Training metrics

Hyperparameters

System stats

(Optionally) media & gradients

Execute in GPU INSTANCE Window Terminal #1

To monitor how your GPU load is, us the command nvtop:

nvtop

In this case we are using a G5.4xlarge with 64GBRAM and one GPU NVIDIA A10G.

After around 10-15 minutes, teh training should start an dthe GPU usage should spike, like so:

When it checks and saves, the GPU usage drops to 0.

And in the WANDB page of teh project (https://wandb.ai/YOUR_USER/lerobot), you should start to see the logs, like so ( the fisrt in teh list in cyan blue):


### In this case, because we deactivated the tune_diffusion_model, the update_s training value starts much higher.

### We have to monitor that it decreases through consecutive training steps, otherwise our model is not learning correctly.

### When the training finishes:
When the training steps are done ( 2000 or whatever you had set ), you shoudl get an output similar to this, whihc indicates that the trained model was uploaded to HUGGING face:

INFO 2026-02-13 15:26:39 ot_train.py:423 step:2K smpl:6M ep:10K epch:189.65 loss:0.008 grdn:0.091 lr:1.0e-05 updt_s:0.662 data_s:0.272

INFO 2026-02-13 15:26:39 ot_train.py:443 Checkpoint policy after step 2000

INFO 2026-02-13 15:27:07 ot_train.py:514 End of training

Processing Files (1 / 1)      : 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6.96GB / 6.96GB,  169MB/s

New Data Upload               : 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3.05GB / 3.05GB, 3.10MB/s

...lace-g1/model.safetensors: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6.96GB / 6.96GB

INFO 2026-02-13 15:28:16 etrained.py:246 Model pushed to https://huggingface.co/theconstruct-ai/groot-pick-place-g1

Processing Files (1 / 1)      : 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6.48kB / 6.48kB, 6.48kB/s

New Data Upload               : |                                                                                                                         |  0.00B /  0.00B,  0.00B/s

...ack_inputs_v3.safetensors: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6.48kB / 6.48kB

No files have been modified since last commit. Skipping to prevent empty commit.


> **⚠️ Note:** WARNING 2026-02-13 15:28:18 /hf_api.py:4298 No files have been modified since last commit. Skipping to prevent empty commit.
Processing Files (1 / 1)      : 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6.48kB / 6.48kB,  0.00B/s

New Data Upload               : |                                                                                                                         |  0.00B /  0.00B,  0.00B/s

...nnormalize_v1.safetensors: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6.48kB / 6.48kB

No files have been modified since last commit. Skipping to prevent empty commit.


> **⚠️ Note:** WARNING 2026-02-13 15:28:19 /hf_api.py:4298 No files have been modified since last commit. Skipping to prevent empty commit
And in the hugging face ( https://huggingface.co/YOUR_USER/groot-pick-place-g1 ) you should get something like so:

Total training time in a g5.4clarge instance with A10G GPU single:

start time: 11:34:55

end time: 11:54:32

Delta: 20 minutes.

Now you have a trained Gr00t model .


## MULTIGPU COMMAND
The ocmmands are similar , except for two distinct changes:

1) We use the --multi_gpu tag with --num_processes=$NUM_GPUS being NUM_GPUS=8 in case of a p4 instance. 2) We set --policy.tune_diffusion_model=true , imrpoving learning rates and quality.


### Diffusion, why is it so important?
Groot is diffusion-based.

If we don’t tune the diffusion model:

We are basically learning a thin adapter

We are not modifying the generative action dynamics

If we do tune it:

We are reshaping the full action distribution model

That’s a huge difference.

Following an analogy:

false = You fine-tune a steering wheel attached to a locked engine.

true = You open the engine and start modifying the pistons.

Much more powerful BUT, much easier to break.


### MultiGPU, why?
Multi-GPU does NOT make the model “smarter”.

It does:

Improve optimization dynamics

Reduce variance

Increase throughput

But if your learning rate is wrong, 8 GPUs can explode faster too


### So basically helps us train faster and reduce variance. Also alows us to train with much more data in teh same time.
Execute in SSH GPU COMPUTER Terminal #1

conda deactivate

conda activate lerobot

cd ~/lerobot

# Before you nee dto update

huggingface-cli login


## HUGGING_FACE_API_KEY

## # MAX
export NUM_GPUS=8

export OUTPUT_DIR="outputs/groot_pick_place_g1_mgpu_$(date +%Y%m%d_%H%M%S)"

export BATCH_SIZE=48

export NUM_STEPS=2000

export SAVE_FREQ=1000

export EVAL_FREQ=1000

export LOG_FREQ=50

export REPO_ID="theconstruct-ai/groot-pick-place-g1"

export DATASET_ID="theconstruct-ai/pick_place_g1"

export JOB_NAME="groot_pick_place_g1"

accelerate launch \

--multi_gpu \

--num_processes=$NUM_GPUS \

--mixed_precision=bf16 \

$(which lerobot-train) \

--output_dir="$OUTPUT_DIR" \

--save_checkpoint=true \

--batch_size=$BATCH_SIZE \

--steps=$NUM_STEPS \

--save_freq=$SAVE_FREQ \

--eval_freq=$EVAL_FREQ \

--log_freq=$LOG_FREQ \

--policy.type=groot \

--policy.push_to_hub=true \

--policy.repo_id="$REPO_ID" \

--policy.tune_diffusion_model=true \

--dataset.repo_id="$DATASET_ID" \

--dataset.revision="main" \

--dataset.video_backend=pyav \

--wandb.enable=true \

--wandb.disable_artifact=true \

--job_name="$JOB_NAME"

With huge training:

conda deactivate

conda activate lerobot

cd ~/lerobot

# Before you nee dto update

huggingface-cli login


## HUGGING_FACE_API_KEY

## # MAX
export NUM_GPUS=8

export OUTPUT_DIR="outputs/groot_pick_place_g1_mgpu_$(date +%Y%m%d_%H%M%S)"

export BATCH_SIZE=48

export NUM_STEPS=200000

export SAVE_FREQ=1000

export EVAL_FREQ=1000

export LOG_FREQ=50

export REPO_ID="theconstruct-ai/groot-pick-place-g1"

export DATASET_ID="theconstruct-ai/pick_place_g1"

export JOB_NAME="groot_pick_place_g1"

accelerate launch \

--multi_gpu \

--num_processes=$NUM_GPUS \

--mixed_precision=bf16 \

$(which lerobot-train) \

--output_dir="$OUTPUT_DIR" \

--save_checkpoint=true \

--batch_size=$BATCH_SIZE \

--steps=$NUM_STEPS \

--save_freq=$SAVE_FREQ \

--eval_freq=$EVAL_FREQ \

--log_freq=$LOG_FREQ \

--policy.type=groot \

--policy.push_to_hub=true \

--policy.repo_id="$REPO_ID" \

--policy.tune_diffusion_model=true \

--dataset.repo_id="$DATASET_ID" \

--dataset.revision="main" \

--dataset.video_backend=pyav \

--wandb.enable=true \

--wandb.disable_artifact=true \

--job_name="$JOB_NAME"


# Setup Localy
It might change your local setup, due to GPU models and drivers, but this is a very good starting point:

mkdir -p ~/miniconda3

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh

bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3

rm ~/miniconda3/miniconda.sh

# Bashrc

source ~/miniconda3/bin/activate

conda init --all

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

conda create -y -n lerobot python=3.10

conda activate lerobot

rm -rf lerobot/

git clone https://github.com/huggingface/lerobot.git

pip install "torch>=2.2.1,<2.8.0" "torchvision>=0.21.0,<0.23.0"

pip install ninja "packaging>=24.2,<26.0"

# This might failed, https://flashattn.dev/

pip install "flash-attn>=2.5.9,<3.0.0" --no-build-isolation

pip install https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.8.3%2Bcu126torch2.7-cp310-cp310-linux_x86_64.whl

python -c "import flash_attn; print(f'Flash Attention {flash_attn.__version__} imported successfully')"

cd ~/lerobot

pip install lerobot[groot]

curl -LsSf https://hf.co/cli/install.sh | bash

hf auth login

# YOUR_HUGGING_FACE_API, no

pip uninstall torchcodec -y

pip install torchcodec==0.10.0

conda remove ffmpeg

conda install ffmpeg=7 -c conda-forge --force-reinstall

export LEROBOT_VIDEO_BACKEND=decord

pip install decord

pip uninstall -y torchcodec

pip install -U torchcodec

pip install -U av


# Unitree G1 Reinforcement Learning Course


---

V3


## Isaac-GR00T
> **Duration:** Estimated time to completion for the whole unit: 90 min
> **Objective:** eploy Isaac-GR00T on the Unitree G1

## Introduction

### Isaac-GR00T is NVIDIA's foundation model for humanoid robots. It combines a Visual Language Model (VLM) with a robot action head to produce joint commands from camera images and natural language instructions.
In this unit, you will run the full GR00T pipeline on the Unitree G1:

A GR00T inference server processes images and language to produce actions.

A MuJoCo simulation (RoboCasa) provides images and acts as the robot environment.

The GR00T-WholeBodyControl policy translates GR00T actions into low-level joint commands.

A closed-loop bridge connects the inference server, simulation, and controller.


# Why GR00T?

### Traditional RL policies (gait, motion tracking) require hand-crafted reward functions and are hard to generalize. GR00T addresses this by training directly on robot demonstration videos, enabling instruction-following behavior from natural language.
GR00T sits at the top of the control stack:

It does not send low-level motor commands.

It does not replace the gait or WBC controller.

It outputs arm and hand joint targets that the WholeBodyControl policy executes.


## Workflows
The full GR00T pipeline involves four processes running simultaneously:


# Installation

## Install uv
uv is the package manager used by Isaac-GR00T for fast, reproducible dependency management. uv v0.8.4+ is required.

Install uv:

Execute in Terminal #1

curl -LsSf https://astral.sh/uv/install.sh | sh

Execute in Terminal #1

source $HOME/.local/bin/env  # or restart your shell


## Clone Isaac-GR00T
Clone the repository with submodules:

Execute in Terminal #1

git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T

cd ~/Isaac-GR00T

If you already cloned without submodules, initialize them separately:

git submodule update --init --recursive


## Set up the environment
Create the virtual environment and install GR00T:


> **⚠️ Note:** ⚠️ CUDA 12.4 is recommended. For RTX-5090 (CUDA 12.8) ensure flash-attn==2.8.0.post2 is installed.
Execute in Terminal #1

cd ~/Isaac-GR00T && uv sync --python 3.10

Execute in Terminal #1

uv pip install -e .

🔍 The installation may take several minutes due to flash-attn compilation. Once complete, the ~/Isaac-GR00T/.venv virtual environment is ready.


### flash-attn

### The dependency package flash-attn often gives problems because the wheel that you install has to match the Pytorch + CUDA version installed in your system.
To check your versions:

Execute in Terminal #1

cd ~/Isaac-GR00T && uv run python -c "import torch; print('torch', torch.__version__); print('torch.version.cuda', torch.version.cuda); print('cap', torch.cuda.get_device_capability()); print('cuda available', torch.cuda.is_available())"


# Running GR00T

## Server architecture

### The GR00T server loads the pretrained model (nvidia/GR00T-N1.6-G1-PnPAppleToPlate) and exposes it over a network port. The closed-loop bridge sends camera images and language instructions to it and receives joint action predictions in return.

### Run GR00T + WBC - exercise
Activate the GR00T virtual environment and start the inference server:

Execute in Terminal #1

cd ~/Isaac-GR00T && source .venv/bin/activate

Execute in Terminal #1

uv run python gr00t/eval/run_gr00t_server.py \

--embodiment-tag UNITREE_G1 \

--model-path theconstruct-ai/push_box_mujoco \

--device cuda:0 \

--host 0.0.0.0 \

--port 5556

🔍 For this demo we are using our own dataset theconstruct-ai/push_box_mujoco. Wait until you see the server ready message before proceeding to the next steps.

Server is ready and listening on tcp://0.0.0.0:5556


# GR00T-WholeBodyControl

## Walk policy executor

### GR00T-WholeBodyControl (WBC) is a separate policy that takes the high-level joint targets produced by GR00T and combines them with a balance/walk policy to produce safe, coordinated whole-body motion on the G1.
It runs inside a Docker container in ~/Projects/gr00t-wholebodycontrol.


### InterpolationPolicy?

### InterpolationPolicy is the component inside WBC that smoothly interpolates between successive GR00T action chunks, preventing jerky movements that would arise from directly applying discrete action outputs at the full control frequency.

### Exercise - run WBC simulation & control
Start the MuJoCo simulation (RoboCasa environment). This pulls the remote Docker image; add --build if you want the latest local build:


### Simulation
Execute in Terminal #2

cd ~/Projects/GR00T-WholeBodyControl && ./docker/run_docker.sh --install

Execute in Terminal #2

python decoupled_wbc/control/main/teleop/run_sim_loop.py \

--wbc_version gear_wbc \

--interface lo \

--simulator robocasa \

--sim_frequency 200 \

--camera_port 5557 \

--no-enable_waist \

--with_hands \

--enable_image_publish \

--enable_offscreen \

--enable_onscreen \

--env_name ManipCubeToZoneDC

🔍 You should see a mujoco simulation appear. It's not using any controllers yet. Try changing the view with + key:

In a new terminal, start the GR00T-WholeBodyControl[ler] inside Docker:


### Control
Execute in Terminal #3

cd ~/Projects/GR00T-WholeBodyControl && ./docker/run_docker.sh

Execute in Terminal #3

python decoupled_wbc/control/main/teleop/run_g1_control_loop.py \

--wbc_version gear_wbc \

--wbc_model_path policy/GR00T-WholeBodyControl-Balance.onnx,policy/GR00T-WholeBodyControl-Walk.onnx \

--wbc_policy_class G1DecoupledWholeBodyPolicy \

--interface lo \

--simulator None \

--control_frequency 50 \

--no-enable_waist \

--with_hands \

--no-high_elbow_pose \

--no-enable_gravity_compensation \

--enable-upper-body-operation \

--upper-body-operation-mode inference

🔍⚠️ Once the controller is running, press alt + ] with focus on the control loop terminal so the robot stands up:


### Once you see the control loop start, you can focus on the control terminal again and use keys W, A, S, D, to confirm that the gait policy is working. Use Z to stop.
- ✅ With the GR00T server, the simulation and the WBC controller, we can now call the server through the closed loop bridge program.

## Open loop evaluation

### In open loop evaluation, GR00T generates a fixed sequence of actions without receiving feedback from the environment mid-sequence. This is useful for initial testing of the model checkpoint before running the full closed-loop setup.

## Isaac-GR00T eval

### The Isaac-GR00T repository provides evaluation scripts (gr00t/eval/) to test the model in both open and closed loop configurations. Refer to the repository README for additional evaluation flags.

# Closed loop evaluation bridge

## Exercise - run GR00T + Sim + Control loop + bridge
The closed-loop bridge ties everything together:

Reads camera images from the simulation (port 5555).

Sends them along with a language instruction to the GR00T server (port 5556).

Receives joint action predictions and forwards them to the WBC controller.

Make sure you have the file ~/cyclonedds.xml for DDS communication between the bridge and the simulation:

cyclonedds.xml

<?xml version="1.0" encoding="UTF-8"?>

<CycloneDDS xmlns="https://cdds.io/config" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://cdds.io/config https://cdds.io/config/cyclonedds.xsd">

<Domain id="any">

<General>

<NetworkInterfaceAddress>lo</NetworkInterfaceAddress>

</General>

</Domain>

</CycloneDDS>

With Terminals #1, #2, and #3 running, start the bridge:

Execute in Terminal #4

cd ~/Projects/GR00T-WholeBodyControl && source ~/Isaac-GR00T/.venv/bin/activate

Execute in Terminal #4

export PYTHONPATH="$PWD"

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

export CYCLONEDDS_URI=~/cyclonedds.xml

source /opt/ros/humble/setup.bash

python decoupled_wbc/control/main/teleop/run_groot_closed_loop_bridge.py \

--camera-host localhost \

--camera-port 5557 \

--policy-host localhost \

--policy-port 5556 \

--rate-hz 10 \

--with_hands \

--lang-instruction "push the red box to the blue zone." \

--no-arms-action-is-delta \

--debug-joint-mapping \

--debug-print-server-action-reps

🔍 You should see the robot in the simulation responding to the language instruction. During model inference, the GR00T server is receiving the current state of the robot from the sim and outputting action chunks in real-time.

It takes some time for GR00T to process the current state and produce the next action chunk, so the task is performed in slow-motion. This animation running at 4x speed!

If you want to reset the robot and retry the inference:

(1) Stop the controller (run_g1_control_loop.py) and the closed-loop evaluation bridge (run_groot_closed_loop_bridge.py) using Ctrl + C. The robot will fall the to ground.

(2) Restart the controller. The robot joints will move to the ready position.

(3) Press ] (or Alt GR + ]) in the controller to start the lower body policy.

(4) Click on the Mujoco sim window and press Backspace multiple times to reset until the robot is standing still.

(5) Restart the closed-loop evaluation bridge. This will start the task inference again.

Change --lang-instruction to try different tasks.


> **⚠️ Note:** ⚠️ This is not perfect and it struggles with different tasks. But you can see here the whole skeleton of the pipeline actually executing on a DDS mujoco simulation!

# Unitree G1 Reinforcement Learning Course


## 3.1   G1 ROS Environment
> **Duration:** Estimated time to completion for the whole unit: 60 min
> **Objective:** nderstand the G1 EDU PC's ROS/ROS 2 multi-version environment.
> **Topics:**
> - 3.1.1 G1 EDU PC Architecture Overview
> - 3.1.2 ROS Noetic
> - 3.1.3 ROS 2 Foxy
> - 3.1.4 CycloneDDS Workspace
> - 3.1.5 Simulation environment

## 3.1.1 PC2 Architecture Overview
The G1 EDU PC runs a multi-version ROS environment:

Key Components:

ROS Noetic

ROS 2 Foxy

CycloneDDS: DDS implementation


## 3.1.2 ROS Noetic

### Installation and Configuration
ROS Noetic is pre-installed on the EDU PC.

# Check ROS Noetic installation

source /opt/ros/noetic/setup.bash


## 3.1.3 ROS 2 Foxy

### ROS 2 Foxy Setup
# Source ROS 2 Foxy

source /opt/ros/foxy/setup.bash


### ROS 2 DDS Configuration

### The G1 uses CycloneDDS as its default communication system, from the locomotion client down to the individual joints.
# Set RMW implementation to CycloneDDS

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Configure domain ID (must match SDK2 or your process)

export ROS_DOMAIN_ID=0

# Add to bashrc for persistence (optional)

echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc

echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc


## 3.1.4 CycloneDDS Workspace

### The customized cyclonedds_ws that comes preinstalled in the robot (~), as well as the workspace that comes in the unitree_ros2 repo, is a compiled implementation of the CycloneDDS protocol. It is done this way (instead of a simple deb installation), because the developers at unitree wanted to make sure that the protocol they built their code against will be static. That way, if there is an upgrade in the way CycloneDDS works (as in Humble - Jazzy transition), the internals of the robot (which remember, travel through DDS) will still work.

### 🔥 Exercise

Exercise: ROS 2 introspection
Source Foxy installation.

Check topics.

Error! That't because the specific build of CycloneDDS, inside cyclonedds_ws, has not been sourced.

Source cyclonedds_ws (will automatically also source Foxy installation.

Check topics.

You can see them!

Who's publishing them?

There are no ROS 2 processes running in PC2. Check with pgrep -f -a ros

There is a node ros_bridge coming from PC1. Is that one in charge of publishing the ROS 2 topics we see, or are those bare DDS topics that the ROS 2 introspection happens to pick up?


## 3.1.5 Simulation environment
For the simulation, we will us ethe Sentinel Simulator version for the G1 robot.

Sentinel simulator is a simulation created by TheConstruct, totally web-based.

This G1 Version is meant only for navigation and basic perception tasks.

At the top it should say: CONNECTED and have a GREEN BOX


## Make the Sentinel G1 move:

### You can move the robot around focusing on the simulation window and pressing the keyboard keys w,a,s,d .
Move the camera with the RIGHT mouse CLICK AND DRAG on the simulation window.

Increase Linear speed pressing q, decrease with e. See in the UI display the numbers changing.

Increase turning speed pressing z, decrease with x. See in the UI display the numbers changing.

Increase acceleration pressing 1, decrease with 2. See in the UI display the numbers changing.


### When you want to reset the positions of the robot to the initial state, just CLICK on the RESET BUTTONon the simulation UI.
The simulations environment works in ROS2 HUMBLE.

This means that we can do:

Execute in Terminal #1

ros2 topic list

Output

/clock

/cmd_vel

/livox/imu

/livox/lidar

/parameter_events

/rosout

We will introduce the use of each of these topics when we need them.


# Unitree G1 Reinforcement Learning Course


## 3.2   G1 Sensor Configuration - LiDAR and Camera
> **Duration:** Estimated time to completion for the whole unit: 45 min
> **Objective:** onfigure and integrate the two primary sensors for G1 perception - the Livox MID-360 LiDAR and Intel RealSense D435/D455 depth camera. Learn to launch drivers, visualize data, and integrate with ROS 2 navigation and perception stacks.
> **Topics:**
> - 3.2.1 Sensor Overview and Specifications
> - 3.2.2 Livox MID-360 LiDAR Setup
> - 3.2.3 Building Livox ROS 2 Driver
> - 3.2.4 Configuring and Launching Livox
> - 3.2.5 Intel RealSense
> - 3.2.6 Visualizing ROS 2 nodes in PC2

## 3.2.1 Sensor Overview and Specifications

### G1 Sensor Suite
Primary Sensors:

Livox MID-360 LiDAR: 360° mechanical scanning, 200m range

Intel RealSense D435: RGB-D camera with depth sensing


### Sensor Specifications

### Luckily, there are ROS 2 drivers available for both the LiDAR and the camera. Let's see how to launch them.

## 3.2.2 Livox MID-360 LiDAR Setup

### Hardware Connection
The Livox MID-360 connects to the G1 via Ethernet. Default IP configuration:

LiDAR IP: 192.168.123.120

Host IP: 192.168.123.164

Connection: Ethernet cable to G1 EDU PC


### Repository Structure
~/ws_livox_ros2/

└── src/

└── livox_ros_driver2/

├── config/

│   ├── MID360_config.json

├── launch/

│   ├── msg_MID360_launch.py

├── msg/

│   └── CustomMsg.msg, CustomPoint.msg

└── src/

└── livox_ros_driver2.cpp


## 3.2.3 Building Livox ROS 2 Driver

### Clone and Build Process
# Create workspace

mkdir -p ~/ws_livox_ros2/src

cd ~/ws_livox_ros2/src

# Clone Livox ROS 2 driver

git clone https://bitbucket.org/theconstructcore/livox_ros_driver2/src/master/

# Install dependencies

cd ..

rosdep install --from-paths src --ignore-src -r -y

# Build workspace

colcon build --symlink-install

# Source workspace

source install/setup.bash


### Dependencies
Required Dependencies:

Livox SDK2

PCL (Point Cloud Library)

Eigen3

ROS 2 Foxy or newer


### Our repository of the Livox driver is modified so that the data of the G1 LiDAR, which is flipped, outputs the data right-side-up and also changes the gravity acceleration from negative to positive due to this orientation. This will be helful when localizing the robot.

## 3.2.4 Configuring and Launching Livox

### Configuration File
MID360_config.json

The Livox LiDAR communicates through ethernet, so IPs must be defined in the configuration file, for the lidar (192.168.123.120) and for the PC2 that it connects to (192.168.123.164):

{

"lidar_summary_info" : {

"lidar_type": 8

},


## "MID360": {
"lidar_net_info" : {

"cmd_data_port": 56100,

"push_msg_port": 56200,

"point_data_port": 56300,

"imu_data_port": 56400,

"log_data_port": 56500

},

"host_net_info" : {

"cmd_data_ip" : "192.168.123.164",

"cmd_data_port": 56101,

"push_msg_ip": "192.168.123.164",

"push_msg_port": 56201,

"point_data_ip": "192.168.123.164",

"point_data_port": 56301,

"imu_data_ip" : "192.168.123.164",

"imu_data_port": 56401,

"log_data_ip" : "",

"log_data_port": 56501

}

},

"lidar_configs" : [

{

"ip" : "192.168.123.120",

"pcl_data_type" : 1,

"pattern_mode" : 0,

"extrinsic_parameter" : {

"roll": 180.0,

"pitch": 0.0,

"yaw": 0.0,

"x": 0,

"y": 0,

"z": 0

}

}Image

]

}


### Launch Scripts

### In order to simplify the launching of several ROS 2 processes, I've created helpful .sh scripts that source everything needed before launching. I recommend doing the same thing.
# launch_livox_ros2.sh

#!/bin/bash

source ~/ws_livox_ros2/install/setup.bash

ros2 launch livox_ros_driver2 msg_MID360_launch.py

Check for /livox/lidar and /livox/imu topics.


### Launch File Parameters: Use Livox custom msg or standard Pointcloud2
msg_MID360_launch.py

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription

from launch_ros.actions import Node

import launch

################### user configure parameters for ros2 start ###################

xfer_format   = 0    # 0-Pointcloud2(PointXYZRTL), 1-customized pointcloud format

multi_topic   = 0    # 0-All LiDARs share the same topic, 1-One LiDAR one topic

data_src      = 0    # 0-lidar, others-Invalid data src

publish_freq  = 10.0 # freqency of publish, 5.0, 10.0, 20.0, 50.0, etc.

output_type   = 0

frame_id      = 'livox_frame'

lvx_file_path = '/home/livox/livox_test.lvx'

cmdline_bd_code = 'livox0000000001'

cur_path = os.path.split(os.path.realpath(__file__))[0] + '/'

cur_config_path = cur_path + '../config'

user_config_path = os.path.join(cur_config_path, 'MID360_config.json')

################### user configure parameters for ros2 end #####################

livox_ros2_params = [

{"xfer_format": xfer_format},

{"multi_topic": multi_topic},

{"data_src": data_src},

{"publish_freq": publish_freq},

{"output_data_type": output_type},

{"frame_id": frame_id},

{"lvx_file_path": lvx_file_path},

{"user_config_path": user_config_path},

{"cmdline_input_bd_code": cmdline_bd_code}

]

def generate_launch_description():

livox_driver = Node(

package='livox_ros_driver2',

executable='livox_ros_driver2_node',

name='livox_lidar_publisher',

output='screen',

parameters=livox_ros2_params

)

return LaunchDescription([

livox_driver,

# launch.actions.RegisterEventHandler(

#     event_handler=launch.event_handlers.OnProcessExit(

#         target_action=livox_rviz,

#         on_exit=[

#             launch.actions.EmitEvent(event=launch.events.Shutdown()),

#         ]

#     )

# )

])

Things to pay attention to:

xfer_format - If you are using ROS 2, just go with 0 for PointCloud2

frame_id - The frame that the poincloud data will be published under.

user_config_path - Configuration file used.


## 3.2.5 Intel RealSense

### Installation
Binary Installation

# Install ROS 2 wrapper

sudo apt install ros-foxy-realsense2-camera ros-foxy-realsense2-camera-msgs

The sandard realsense2_camera_node is enough for most applications:

# launch_realsense_camera.sh

#!/bin/bash

source /opt/ros/foxy/setup.bash

source ~/cyclonedds_ws/install/setup.bash

ros2 run realsense2_camera realsense2_camera_node

Check for /image topics being published.


## 3.2.6 Visualizing data from ROS 2 nodes in PC2
After running the LiDAR and camera drivers, the obvious question arises: How to visualize these processes in RViZ?


### ROS 2 is notoriously faulty when it comes to the default over the wire communication, so we have used Zenoh to be able to visualize things like images and pointclouds.

### Zenoh Bridge Container
Zenoh bridges all ROS 2 communications using DDS over Zenoh communication protocol:

Zenoh bridge 1 captures all local DDS data in robot.

Zenoh converts this data to Zenoh protocol and sends it over the wire.

Zenoh bridge 2 converts data back to DDS and dumps it in the other robot/PC.


### In my experience, it's the best and most reliable way to date to communicate wirelessly. In the newer distributions, it's even been made into a RMW implementation rmw_zenoh see this for more. We'll use the Zenoh bridge container that works in all distributions (that I've tested).
You can clone this repo (g1_training branch) to deploy in your own G1.

git clone -b g1_training https://bitbucket.org/theconstructcore/zenoh_g1/src/g1_training/

Follow the repo's README to deploy one bridge in your G1, one in your PC:


## # G1
cd zenoh_g1/docker

docker-compose -f docker-compose-g1.yaml up -d

# Your PC

cd zenoh_g1/docker

docker-compose -f docker-compose-local.yaml up -d

In your PC, you should see the G1 topics (for the drivers launched in the PC2, not the PC1 topics.

Open RViZ and add whatever you want to visualize:

Note that the Fixed Frame is livox_frame, the frame we set in the livox launch as frame_id. You can do the same for the image:


## 3.2.7 Visualising lidar in Simulation
In the Sentinel Simulation, becuase its working directly with Humble ROS2, we just have to:

Open the RVIZ2

Set the fixed frame ( typing ) livox_frame

Add the element Pointlcoud topic /livox/lidar

Execute in Terminal #1

rviz2

Now you ca move teh robot around and see teh lidar readings

Remember that you can change the linear and angular speeds with q/e and z/x respectively.

Note that the simulation has MUCH LESS points in its pointcloud.


# Motor States and Robot State Publisher
Arguably, the most important sensors to obtain clear information from are the motor positions.


### As seen throughout the course, this information can be obtained from /lowstate. However, the clarity of the motor states would be improved by visualizing it through ROS 2 and rviz, with a clear TF tree representing the real time state of the robot.

### In order to achieve this, the ROS 2 robot state publisher can be used. This requires a robot URDF, which is available, and a subscription to /joint_states, which can be obtained from /lowstate.
The result will be a viewable real-time robot model:


## Publish /joint_states
The position (q) field of /lowstate is extracted and published through /joint_states.

In the G1, source cyclonedds_ws and echo /lowstate:

source ~/cyclonedds_ws/install/setup.bash && ros2 topic echo /lowstate

Each message provides information about all 29 motors in the G1.

Each one must be extracted and assigned to a joint name. We will use the names provided by Unitree's URDF:

left_hip_pitch_joint

left_hip_roll_joint

left_hip_yaw_joint

left_knee_joint

left_ankle_pitch_joint

left_ankle_roll_joint

right_hip_pitch_joint

right_hip_roll_joint

right_hip_yaw_joint

right_knee_joint

right_ankle_pitch_joint

right_ankle_roll_joint

waist_yaw_joint

waist_roll_joint

waist_pitch_joint

left_shoulder_pitch_joint

left_shoulder_roll_joint

left_shoulder_yaw_joint

left_elbow_joint

left_wrist_roll_joint

left_wrist_pitch_joint

left_wrist_yaw_joint

right_shoulder_pitch_joint

right_shoulder_roll_joint

right_shoulder_yaw_joint

right_elbow_joint

right_wrist_roll_joint

right_wrist_pitch_joint

right_wrist_yaw_joint

Since /lowstate is accesible through ROS 2 introspection, a simple ROS 2 subscriber/publisher node will do:

lowstate_jointstate_bridge.py

#!/usr/bin/env python3

import rclpy

from rclpy.node import Node

from unitree_hg.msg import LowState # Unitree messages are provided by unitree_ros2 packages in GitHub

from sensor_msgs.msg import JointState

from rclpy.qos import QoSProfile, QoSReliabilityPolicy

class G1JointStateBridge(Node):

def __init__(self):

super().__init__('g1_joint_state_bridge')

qos = QoSProfile(

depth=10,

reliability=QoSReliabilityPolicy.BEST_EFFORT # Use BEST_EFFORT to match rviz subscription to /joint_states

)

self.sub = self.create_subscription(LowState, 'lf/lowstate', self.callback, 10)

self.pub = self.create_publisher(JointState, '/joint_states', qos)

self.joint_names = [

"left_hip_pitch_joint",

"left_hip_roll_joint",

"left_hip_yaw_joint",

"left_knee_joint",

"left_ankle_pitch_joint",

"left_ankle_roll_joint",

"right_hip_pitch_joint",

"right_hip_roll_joint",

"right_hip_yaw_joint",

"right_knee_joint",

"right_ankle_pitch_joint",

"right_ankle_roll_joint",

"waist_yaw_joint",

"waist_roll_joint",

"waist_pitch_joint",

"left_shoulder_pitch_joint",

"left_shoulder_roll_joint",

"left_shoulder_yaw_joint",

"left_elbow_joint",

"left_wrist_roll_joint",

"left_wrist_pitch_joint",

"left_wrist_yaw_joint",

"right_shoulder_pitch_joint",

"right_shoulder_roll_joint",

"right_shoulder_yaw_joint",

"right_elbow_joint",

"right_wrist_roll_joint",

"right_wrist_pitch_joint",

"right_wrist_yaw_joint"

]

def callback(self, msg: LowState):

positions = [m.q for m in msg.motor_state[:29]]

js = JointState()

js.header.stamp = self.get_clock().now().to_msg()

js.name = self.joint_names

js.position = positions

self.pub.publish(js)

def main(args=None):

rclpy.init(args=args)

node = G1JointStateBridge()

rclpy.spin(node)

node.destroy_node()

rclpy.shutdown()

if __name__ == '__main__':

main()


### Once this node is running, the default ROS 2 robot_state_publisher can be launched with the G1 URDF loaded.
This will result in robot_state_publisher publishing the real-time joint positions through TF transforms on /tf and /tf_static:

In order to simplify and standardize the programs, they are launched within a docker container. This can be ran in any G1 robot:

docker-compose.yaml

services:

lowstate_bridge:

image: theconstructai/g1_description

container_name: lowstate_bridge

privileged: true

network_mode: host

restart: always

entrypoint: /ros_entrypoint.sh

command: ["/bin/bash", "-lc", "source /ros2_ws/install/setup.bash && source /unitree_ros2/cyclonedds_ws/install/setup.bash && ros2 run g1_description lowstate_jointstate_bridge"]

robot_state_publisher:

image: theconstructai/g1_description

container_name: robot_state_publisher

privileged: true

network_mode: host

restart: always

entrypoint: /ros_entrypoint.sh

command: ["/bin/bash", "-lc", "source /ros2_ws/install/setup.bash && ros2 launch g1_description robot_state_publisher.launch.py"]

Run it with:

docker compose -f /path/to/docker-compose.yaml up -d

Check /joint_states:

ros2 topic echo /joint_states

Open rviz

Select a valid Fixed Frame (like pelvis)

Add TF, Effort (/joint_states) and RobotModel elements, and see your robot state in real time!


### Congratulations! You have successfully configured the Livox MID-360 LiDAR and Intel RealSense camera for the G1 robot. These sensors provide the essential perception capabilities for navigation, obstacle avoidance, and environmental mapping.

### What's next? In the next unit, you will learn how to use these sensors with SLAM algorithms for mapping and localization.

---

**Next:** Unit 4 — Subsection 1: SLAM with G1

# Unitree G1 Reinforcement Learning Course


## 3.3   Fast-LIO
> **Duration:** Estimated time to completion for the whole unit: 45–60 min
> **Objective:** et up and run Fast-LIO (Lidar-Inertial Odometry) on the G1 using the Livox MID-360 and IMU. Learn the repository layout, configuration files, how to launch, and how to visualize outputs.
> **Topics:**
> - 3.3.1 What is Fast-LIO?
> - 3.3.2 Repositories Used
> - 3.3.3 Workspace and Dependencies
> - 3.3.4 Configuration Files (g1_mid360.yaml)
> - 3.3.5 Launching Fast-LIO on G1
> - 3.3.6 Visualization in RViz
> - 3.3.7 Log Files and Maps
> - 3.3.8 Troubleshooting

## 3.3.1 What is Fast-LIO?

### Fast-LIO is a tightly coupled LiDAR-Inertial Odometry system that fuses Livox LiDAR and IMU data to estimate the robot pose in real-time. It provides high-frequency, low-drift localization suitable for navigation and mapping.

## 3.3.2 Repositories Used
~/git-repo/fast_lio_ros2 — ROS 2 wrapper and launch files

~/git-repo/g1_scripts/launch_fastlio_ros2.sh — Launch script used on the PC2:

# launch_fastlio_ros2.sh

#!/bin/bash

source /opt/ros/foxy/setup.bash

source ~/cyclonedds_ws/install/setup.bash

source ~/ros2_ws/install/setup.bash

ros2 launch fast_lio mapping.launch.py config_file:=g1_mid360.yaml rviz:=false


## 3.3.4 Configuration Files (g1_mid360.yaml)
Fast-LIO uses a configuration YAML file to specify LiDAR topics, IMU topics, extrinsics, and noise parameters. On the G1, we launch with:

ros2 launch fast_lio mapping.launch.py config_file:=g1_mid360.yaml rviz:=false

g1_mid360.yaml

/**:

ros__parameters:

feature_extract_enable: false

point_filter_num: 3

max_iteration: 3

filter_size_surf: 0.5

filter_size_map: 0.5

cube_side_length: 1000.0

runtime_pos_log_enable: true

map_file_path: "./g1_map.pcd" # name of map to be saved (pcd_save_en must be true)

common:

lid_topic:  "/livox/lidar"

imu_topic:  "/livox/imu"

time_sync_en: false          # ENABLE time sync for rotation

time_offset_lidar_to_imu: 0.0

preprocess:

lidar_type: 4       # 1 for Livox serials LiDAR, 2 for Velodyne LiDAR, 3 for ouster LiDAR, 4 for any other pointcloud input

scan_line: 4

blind: 0.5

timestamp_unit: 3

scan_rate: 10

mapping:

# Critical parameters for rotation stability

acc_cov: 0.1

gyr_cov: 0.001              # Very low - trust gyroscope

b_acc_cov: 0.0001

b_gyr_cov: 0.0000001        # Extremely low - prevent gyro drift

fov_degree: 360.0

det_range: 50.0

extrinsic_est_en: False      # ENABLE to auto-calibrate

# Initial guess for upside-down mounting

# Will be refined by extrinsic estimation

extrinsic_T: [ 0.0, 0.0, 0.0 ]

extrinsic_R: [ 1.0,  0.0,  0.0,

0.0, 1.0,  0.0,

0.0,  0.0, 1.0]

publish:

path_en: true

effect_map_en: false

map_en: true

scan_publish_en: true

dense_publish_en: false

scan_bodyframe_pub_en: true

pcd_save:

pcd_save_en: true # whether to save the map or not

interval: -1


## Simulation files setup

### Because this si NOT a Navigation in ROS2 course, we won't be creating from scratch all the navigation files.

### Also, making G1 navigate needs quite a few packages; some of them had to be extensively modified or rebuilt to make them work in ROS2.
So we will provide you with a ready-to-compile stack of packages that you are going to copy to the courses environment ~/ros2_ws/src:

Execute in Terminal #1

cd ~/ros2_ws/src

git clone -b remote https://bitbucket.org/theconstructcore/g1_theconstruct_navigation_stack.git

mv -- g1_theconstruct_navigation_stack/* . && rm -rf -- g1_theconstruct_navigation_stack

cd ~/ros2_ws

touch /home/user/ros2_ws/src/unitree_rl_lab/COLCON_IGNORE

colcon build

source install/setup.bash

Final build output

You should get something like so without erros ( just warnings):

Finished <<< fast_lio [1min 21s]

Summary: 9 packages finished [2min 34s]


## 6 packages had stderr output: fast_lio livox_interfaces livox_ros_driver2 open3d_conversions open3d_global_localization open3d_registration
GREAT, now its time to start with the first step: MAPPING!


## Mapping in simulation
For mapping we will use Fastlio package to be able to generate a PointCloud map.

Fastlio will generate an Odometry based on the point cloud matching form the lidar sensor.

This will allow us to create a map while we walk with the robot.

First lets create the PpointCloud Map using fastlio.


## REDUSE SPEED TO MINIMUM
I order to have a successful map an that it doesn't loose track, the speeds of movement and turning have to be low, value **0.1**

To do that juts press repeatedly E for the linear speed, and X for the angular speed until they are 0.1

Execute in Terminal #1

ros2 launch fast_lio mapping.launch.py use_sim_time:=true

When done in a second terminal WITHOUT CLOSING TH EMAPPING COMMAND, execute teh call to the service /map_save, an dit will generate the g1_map.pcd wherever you executed the command for the mapping

Execute in Terminal #1

ros2 service call /map_save std_srvs/srv/Trigger {}

We can visualise the pointcloud map using this open3d program:

Execute in Terminal #1

# View pcd map

pip install "numpy==1.26.4" "scipy>=1.10,<1.12" "open3d>=0.17,<0.19"

python3 /home/user/ros2_ws/src/open3d_tests/pcd_viewer.py /home/user/ros2_ws/g1_map.pcd


> **⚠️ Note:** WARNING

### Sometimes you might get the following error. Just relaunch the script, and it will work the second time.
X Error of failed request:  BadValue (integer parameter out of range for operation)

Major opcode of failed request:  130 (MIT-SHM)

Minor opcode of failed request:  3 (X_ShmPutImage)

Value in failed request:  0x500

Serial number of failed request:  150

Current serial number in output stream:  151


## Remove floor from PointCloud

### We need to remove the floor from the point cloud because for localization it will force the matching system to match with more distinct features, like walls, objects. Otherwise, most of the matching will be the same.
We will remove the points from -0.8 height downwards.

Execute in Terminal #1

python3 /home/user/ros2_ws/src/open3d_tests/pcd_height_filter.py /home/user/ros2_ws/g1_map.pcd --z-threshold -0.8

This should have generated a file named /home/user/ros2_ws/g1_map_z-0.80_filtered.pcd

It should also pop up the visualization of this new point cloud.

Now we need to generate a flat 2D map from the pcd so that we can use it in the navigation stage.

For that, execute the script

Execute in Terminal #1

cd /home/user/ros2_ws/src/g1_nav2/pcd_to_pgm/

python3 pcd2pgm_v2.py /home/user/ros2_ws/g1_map_z-0.80_filtered.pcd \

--out-dir /home/user/ros2_ws/src/g1_nav2/map_server/config \

--name map_dec1 \

--resolution 0.05 \

--z-thresh 0.2

Have a look in the /home/user/ros2_ws/src/g1_nav2/map_server/config/map_dec1.pgm. Juts download it to your computer and visualise it. If you can't, you can alsws use an ONLINE PGM VIEWER


## 3.3.8 Troubleshooting

#### No PointCloud Output
Verify Livox driver is running and /livox/lidar is active

Check g1_mid360.yaml topic names match actual topics


#### Odometry Drifts Quickly
Refine extrinsic calibration between LiDAR and IMU

Tune IMU noise parameters

Ensure IMU data rate and timestamps are correct


# Localization with Open3D

### Now that we have an odometry output in a ROS 2 topic (can anyone tell me another way to get one?) and an odom to base_link TF (in this case, camera_init to body), we can use this in order to localize the robot in the map we have created.

### For this we will use our implementation of Open3d SLAM in ROS 2. You can find the original work here.

### Open3D takes in the /Odometry and the map.pcd produced by fast lio in order to match the G1's point cloud with the map.
Open3D publishes the required map to odom TF for the default Nav2 stack.

Think of Open3D as a replacement of Nav2's amcl, but for PointCloud2 data instead of LaserScan.

Now we have to configure the localization and the fastlio to use OUR PCD map, not the 2d:


### We copy the no-floor point cloud with the name g1_map_remote.pcd to simplify the files to be used after.
# Copy the pcd to a location

cp /home/user/ros2_ws/g1_map_z-0.80_filtered.pcd /home/user/ros2_ws/src/open3d_tests/pcds/g1_map_remote.pcd

And now we add the new path inside the config file for the fast_lio odometry_only.launch.py, /home/user/ros2_ws/src/fast_lio_ros2/config/g1_mid360_odom_only.yaml:

ros__parameters:

feature_extract_enable: false

point_filter_num: 3

max_iteration: 3

filter_size_surf: 0.5

filter_size_map: 0.5

cube_side_length: 1000.0

runtime_pos_log_enable: true

map_file_path: "/home/user/ros2_ws/src/open3d_tests/pcds/g1_map_remote.pcd"

And also for the global localization /home/user/ros2_ws/src/open3d_global_localization/open3d_global_localization/config/loc_param_g1.yaml

open3d_global_localization:

ros__parameters:

# --- Map & time ---

path_map: "/home/user/ros2_ws/src/open3d_tests/pcds/g1_map_remote.pcd"

use_sim_time: True   # keep if you run in sim


## RESET THE SIMULATION

## PRESS THE RESET SIM BUTTON IN THE SIMULATION UI

### This will position the robot in the initial pose, that is, where you should have started the creation of the map.
Execute in Terminal #1

cd ~/ros2_ws

colcon build

Launch Odometry generation ( odom to camera init )

Execute in Terminal #1

cd ~/ros2_ws

source install/setup.bash

ros2 launch fast_lio odometry_only.launch.py use_sim_time:=true rviz:=true

Launch Localization ( map -> odom )

Execute in Terminal #2

cd ~/ros2_ws

source install/setup.bash

ros2 launch open3d_global_localization global_localization_g1.launch.py


## WARING: Sometimes the pintcloud map is not shown. If so , just close this launch and relaunch it, eventually ROS2 will catch it. Also check in rviz that the map topic is Transient local.
You will probably need to set the initial pose so that the robot is localised using RVIZ 2dPose Estimate on the map

And then when you move the robot with the WASD keys, the frame should be localised.

Try to move slowly, because this localization doesn't work well at high speeds.


### TF frames wired structure:

### In the global_localization_g1.launch.py, we are publishing some Static transforms. The main reason for that is that Fastlio generates the odometry tf frames named camera_init -> body.
While normally in ROS we generate the odometry with frames odom -> base_link/base_footprint.


### Because of this and that we don't really care about the internal kinematic structure of the sensors for navigation, we publish some dummy static transforms to have all the tfs connected.

### Also , note the `base_link_nav'. We set this becuase we can use it in the navigation fase to have a frame rotated 180º in Z so that the planner sends correct goals.
from launch import LaunchDescription

from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os

def generate_launch_description():

pkg = 'open3d_global_localization'

pkg_share = get_package_share_directory(pkg)

cfg_path = os.path.join(pkg_share, 'config', 'loc_param_g1.yaml')

return LaunchDescription([

# --- Static TFs (identity) ---

# odom -> camera_init

Node(

package='tf2_ros',

executable='static_transform_publisher',

name='camera_init2odom',

arguments=['0', '0', '0',  # x y z

'0', '0', '0', '1',  # qx qy qz qw

'odom', 'camera_init'],

output='screen',

),

# base_link -> imu_link

Node(

package='tf2_ros',

executable='static_transform_publisher',

name='imulink2baselink',

arguments=['0', '0', '0',

'0', '0', '0', '1',

'base_link', 'imu_link'],

output='screen',

),

# motion_link -> base_link

Node(

package='tf2_ros',

executable='static_transform_publisher',

name='base_center_broadcaster',

arguments=['0', '0', '0',

'0', '0', '0', '1',

'motion_link', 'base_link'],

output='screen',

),

Node(

package='tf2_ros',

executable='static_transform_publisher',

name='baselink_to_navbase',

arguments=[

'0', '0', '0',       # x y z

'0', '0', '1', '0',  # qx qy qz qw  -> 180° around Z

'base_link', 'base_link_nav'   # parent, child

],

output='screen',

),

# MIG Added to connect everything body -> motion_link

Node(

package='tf2_ros',

executable='static_transform_publisher',

name='base_center_broadcaster',

arguments=['0', '0', '0',

'0', '0', '0', '1',

'body', 'motion_link'],

output='screen',

),

Node(

package='tf2_ros',

executable='static_transform_publisher',

name='base_center_broadcaster',

arguments=['0', '0', '0',

'0', '0', '0', '1',

'imu_link', 'livox_frame'],

output='screen',

),

# --- Global localization node ---

Node(

package=pkg,

executable='global_localization_node',

name='open3d_global_localization',

parameters=[

cfg_path,

# keep explicit here for clarity; also present in YAML

{'use_sim_time': True},

],

output='screen',

),

])


# Unitree G1 Reinforcement Learning Course


## 3.4   CMD_VEL Driver for G1 Sport Mode
> **Duration:** Estimated time to completion: 30 min
> **Objective:** earn how to control the Unitree G1 robot using standard ROS2 velocity commands through a custom cmd_vel driver that interfaces with the robot's Sport Mode API.
> **Topics:**
> - 3.4.1 Overview of the CMD_VEL Driver
> - 3.4.2 Architecture and Design
> - 3.4.3 Implementation Details
> - 3.4.4 DDS Domain Separation
> - 3.4.5 Running the Driver
> - 3.4.6 Testing and Troubleshooting

## 3.4.1 Overview of the CMD_VEL Driver

### The g1_sport_mode_ros package provides a ROS2 bridge between standard navigation commands (cmd_vel) and the Unitree G1's SDK. This eliminates the need for a remote controller and enables integration with ROS2 Nav2 stack.
Key Features:

Standard ROS2 /cmdvel interface

Direct Sport Mode API integration

Real-time control with low latency

Full mobility support (forward/backward, strafe, rotation)

Compatible with Nav2 and teleoperation tools


## 3.4.2 Architecture and Design

### Node Structure
The driver is implemented as a Python ROS2 node (g1_sport_ros.py) with the following architecture:

┌─────────────────┐    cmd_vel    ┌──────────────────┐

│  ROS2 Apps      │──────────────>│  g1_sport_ros    │

│  (Nav2, Teleop) │               │     Node         │

└─────────────────┘               └──────────────────┘

│

SDK2 Commands

│

▼

┌──────────────────┐

│   G1 Robot       │

│  (Sport Mode)    │

└──────────────────┘


### Message Mapping
The node maps geometry_msgs/Twist to G1 movement commands:


## 3.4.3 Implementation Details

### Core Implementation
The driver implementation at ~/git-repo/g1_sport_mode_ros/src/g1_sport_ros.py includes:

class G1SportRosNode(Node):

def __init__(self):

# Initialize ROS2 node

super().__init__('g1_sport_ros_node')

# Declare network interface parameter

self.declare_parameter('interface', 'eth0')

# Initialize SDK2 LocoClient

ChannelFactoryInitialize(0, self.interface)

self.client = LocoClient()

self.client.SetTimeout(10.0)

self.client.Init()

# Subscribe to cmd_vel

self.cmd_vel_subscription = self.create_subscription(

Twist, 'cmd_vel', self.cmd_vel_callback, 10)


### Velocity Threshold Management
The G1 robot has minimum velocity constraints. The driver automatically applies thresholds:

def apply_min_threshold(vel, min_threshold=0.2):

if abs(vel) > 0.0 and abs(vel) < min_threshold:

# Scale to minimum while preserving direction

return math.copysign(min_threshold, vel)

return vel


### Important: The G1 requires minimum velocities of 0.2 m/s for linear motion. The driver automatically adjusts small velocities to meet this requirement while preserving direction.

### Performance Optimization
Throttled Logging: Logs every 100 messages to reduce overhead

Graceful Shutdown: Ensures robot stops on exit

Error Handling: Robust exception handling for SDK failures


## 3.4.4 DDS Domain Separation

### Critical Configuration Requirement
CRITICAL: The driver MUST run in a separate ROS domain to avoid DDS conflicts with the Unitree SDK!

The G1 system uses multiple DDS domains:

Domain 0: Used by Unitree SDK2 for robot communication

Domain 1: Used for ROS2 cmd_vel driver (to avoid conflicts)


### Domain Architecture
┌─────────────────────────────────────────────────┐

│                 ROS Domain 1                    │

│  ┌──────────┐        ┌────────────────┐       │

│  │  Teleop  │───────>│  g1_sport_ros  │       │

│  └──────────┘        └────────────────┘       │

└─────────────────────────────────────────────────┘

│

SDK2 Interface

│

┌─────────────────────────────────────────────────┐

│                 DDS Domain 0                    │

│          (Unitree SDK2 ↔ G1 Robot)            │

└─────────────────────────────────────────────────┘


### CycloneDDS Configuration
Before running the driver, unset the manufacturer's CycloneDDS configuration:

# REQUIRED: Unset CYCLONEDDS_HOME to avoid conflicts

unset CYCLONEDDS_HOME


## 3.4.5 Running the Driver

### Building the Package
# Navigate to workspace

cd ~/ros2_ws

# Build the package

colcon build --packages-select g1_sport_mode_ros

# Source the workspace

source install/setup.bash


### Launching the Driver
Step 1: Start the driver node (Terminal 1)

# Unset CycloneDDS configuration

unset CYCLONEDDS_HOME

# Run in domain 1 with network interface

ROS_DOMAIN_ID=1 ros2 run g1_sport_mode_ros g1_sport_ros.py \

--ros-args -p interface:=enx00e04c696fc1

Step 2: Control the robot (Terminal 2)

Option A - Keyboard teleoperation:

ROS_DOMAIN_ID=1 ros2 run teleop_twist_keyboard teleop_twist_keyboard

Option B - Direct command publishing:

ROS_DOMAIN_ID=1 ros2 topic pub /cmd_vel geometry_msgs/Twist \

"{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.2}}"

Option C - Nav2 integration:

# Launch Nav2 in domain 1

ROS_DOMAIN_ID=1 ros2 launch nav2_bringup navigation_launch.py


### Verifying Operation
Check topics in the correct domain:

ROS_DOMAIN_ID=1 ros2 topic list

# Should show: /cmd_vel

ROS_DOMAIN_ID=1 ros2 topic echo /cmd_vel

# Monitor commands being sent


## 3.4.6 Testing and Troubleshooting

### Common Issues and Solutions
Issue 1: DDS_RETCODE_BAD_PARAMETER Error

Cause: CYCLONEDDS_HOME environment variable conflict

Solution: RununsetCYCLONEDDSHOMEbefore starting the node

Issue 2: ChannelFactory Domain Error

Cause: DDS domain conflict between ROS2 and SDK2

Solution: Always run with ROSDOMAINID=1

Issue 3: Robot Not Responding

Verify robot is in Sport Mode

Check network interface parameter matches your setup

Confirm SDK2 Python is properly installed


### Safety Guidelines
Safety First!

Always test in a safe, open environment

Start with small velocity values (0.2 m/s)

Keep emergency stop accessible

Monitor robot behavior closely during initial tests


### Integration Examples
The driver enables seamless integration with:

Nav2: Autonomous navigation with path planning

MoveIt2: Coordinated whole-body motion

SLAM: Mapping while moving with LiDAR

Behavior Trees: Complex behavior orchestration

Custom Controllers: Any ROS2 node publishing Twist messages


### Complete Workflow Example
# Terminal 1: Launch driver

unset CYCLONEDDS_HOME

ROS_DOMAIN_ID=1 ros2 run g1_sport_mode_ros g1_sport_ros.py \

--ros-args -p interface:=enx00e04c696fc1

# Terminal 2: Launch sensors (in domain 1)

ROS_DOMAIN_ID=1 ros2 launch livox_ros2_driver livox_lidar_launch.py

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py

# Terminal 3: Launch navigation

ROS_DOMAIN_ID=1 ros2 launch nav2_bringup navigation_launch.py

# Terminal 4: Send navigation goals

ROS_DOMAIN_ID=1 ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose ...


## Solution to ROS_DOMAIN_ID=1: Use multiprocess

### The Problem
The DDS domain separation issue arises because both the Unitree SDK2 and ROS 2 use DDS for communication:

Unitree SDK2 initializes its own DDS participant in Domain 0 via ChannelFactoryInitialize()

ROS 2 nodes also create DDS participants in the domain specified by ROS_DOMAIN_ID (default is 0)

When both run in the same process with different domain requirements, DDS conflicts occur


### The Multiprocess Solution
The g1_sport_multiprocess.py implementation solves this by isolating the SDK initialization in a separate process. This allows:

SDK Process: Handles Unitree SDK2 operations

ROS 2 Process: Manages ROS 2 node and topics

Each process has its own DDS participant in its respective domain, avoiding conflicts.


### Architecture Overview
┌──────────────────────────────────────────────┐

│         Main Process                         │

│  ┌────────────────────────────────┐          │

│  │   G1SportRosNode (ROS 2)       │          │

│  │   - Subscribes to /cmd_vel     │          │

│  │   - Handles ROS 2 callbacks    │          │

│  └────────────────────────────────┘          │

│              │                               │

│         command_queue                        │

│         status_queue                         │

│              │                               │

└──────────────┼───────────────────────────────┘

│ Inter-Process Communication

┌──────────────┼───────────────────────────────┐

│              ▼                               │

│  ┌────────────────────────────────┐          │

│  │   sdk_process                  │          │

│  │   - ChannelFactoryInitialize() │          │

│  │   - LocoClient.Move()          │          │

│  │   - SDK communication with G1  │          │

│  └────────────────────────────────┘          │

│     Separate Process                         │

└──────────────────────────────────────────────┘


### Key Implementation Details

#### 1. Process Separation at Startup
if __name__ == '__main__':

# CRITICAL: Use 'spawn' method to create clean process

mp.set_start_method('spawn', force=True)

main()


### The spawn method creates a completely new Python interpreter process, ensuring no DDS state is inherited.

#### 2. SDK Process Function
def sdk_process(interface, command_queue, status_queue):

"""Runs in a separate process - Domain 0"""

from unitree_sdk2py.core.channel import ChannelFactoryInitialize

from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

# Initialize SDK in THIS process (Domain 0)

ChannelFactoryInitialize(0, interface)

client = LocoClient()

client.Init()

# Listen for commands from ROS 2 process

while running:

cmd = command_queue.get(timeout=0.1)

if cmd[0] == 'move':

_, vx, vy, omega = cmd

client.Move(vx, vy, omega)

Key Points:

SDK imports happen inside the function (not at module level)

ChannelFactoryInitialize() creates a DDS participant in Domain 0

This process has no ROS 2 initialization - only SDK


#### 3. ROS 2 Node in Main Process
class G1SportRosNode(Node):

def __init__(self):

super().__init__('g1_sport_ros_node')

# Create inter-process queues

self.command_queue = Queue()

self.status_queue = Queue()

# Start SDK in separate process

self.sdk_process = Process(

target=sdk_process,

args=(self.interface, self.command_queue, self.status_queue)

)

self.sdk_process.start()


#### 4. Inter-Process Communication
The two processes communicate using multiprocessing Queues:

ROS 2 → SDK (Command Queue):

def cmd_vel_callback(self, msg):

vx = msg.linear.x

vy = msg.linear.y

omega = msg.angular.z

# Send to SDK process

self.command_queue.put(('move', vx, vy, omega))

SDK → ROS 2 (Status Queue):

# In SDK process

status_queue.put(('initialized', True))

status_queue.put(('error', str(e)))

# In ROS 2 process

def check_sdk_status(self):

status_type, data = self.status_queue.get_nowait()

if status_type == 'initialized':

self.sdk_ready = True


### Benefits of This Approach
Advantages:

Clean DDS Separation: Each process has its own DDS participant in the correct domain

No Domain Conflicts: SDK and ROS 2 never interfere with each other

Robust Error Handling: Processes can crash independently

Flexible Domain Configuration: Can run ROS 2 in any domain ID

Standard ROS 2 Tools: All ROS 2 tools work normally in Domain 1

After (Multiprocess):

Process A (SDK):                  Process B (ROS 2):

- ChannelFactoryInitialize(0)     - rclpy.init()

- DDS Domain 0                    - DDS Domain 0

- ✅ NO CONFLICT                    ✅ NO CONFLICT
Communication via Queue ←───────→ Communication via Queue


### This multiprocess architecture enables seamless integration of the Unitree SDK with ROS 2 navigation and control stacks.

# Sentinel Simulation

### In the sentinel simulation, moving the robot is just a matter of publishing the cmd_vel, nothing more.
Execute in Terminal #1

ros2 run teleop_twist_keyboard teleop_twist_keyboard

We will use this same topic for the navigation.

BE CAREFUL because the real robot might not have the same one once you implement the cmd_vel node.


# Unitree G1 Reinforcement Learning Course


## 3.5   Nav2 Docker Setup for G1 Navigation
> **Duration:** Estimated time to completion: 45 min
> **Objective:** earn how to deploy and configure Nav2 navigation stack for the Unitree G1 using a containerized Docker approach, including costmap configuration, planner setup, and controller tuning.
> **Topics:**
> - 3.5.1 Overview of the Nav2 Docker Architecture
> - 3.5.2 Docker Compose Configuration
> - 3.5.3 Nav2 Components and Configuration Files
> - 3.5.4 Costmap Configuration for G1
> - 3.5.5 Controller and Planner Setup
> - 3.5.6 Launching and Testing Navigation

## 3.5.1 Overview of the Nav2 Docker Architecture
The G1 Nav2 setup uses a containerized approach to ensure consistent deployment and easy management of the navigation stack. The architecture is located at ~/git-repo/g1_nav2/docker/ and consists of:

Key Components:

Docker Image: Custom image based on ROS Humble with Nav2 packages

Volume Mounts: Configuration files mounted from host for easy editing

Network Mode: Host networking for direct hardware access

Domain Separation: Runs in ROS_DOMAIN_ID=1 to avoid SDK conflicts


### Architecture Diagram
┌──────────────────────────────────────────────────┐

│             Docker Container (ROS Humble)        │

│  ┌────────────────────────────────────────────┐  │

│  │           Nav2 Stack Components            │  │

│  ├────────────────────────────────────────────┤  │

│  │  • Map Server (Static Map)                 │  │

│  │  • Planner Server (NavFn)                  │  │

│  │  • Controller Server (DWB)                 │  │

│  │  • BT Navigator (Behavior Trees)           │  │

│  │  • Recovery Behaviors                      │  │

│  │  • Lifecycle Manager                       │  │

│  └────────────────────────────────────────────┘  │

└──────────────────────────────────────────────────┘

│

Volume Mounts

│

┌──────────────────────────────────────────────────┐

│              Host Configuration Files            │

│  • behavior.xml    • controller.yaml             │

│  • planner.yaml    • recovery.yaml               │

│  • bt_navigator.yaml • map.yaml & map.pgm        │

└──────────────────────────────────────────────────┘


## 3.5.2 Docker Compose Configuration

### Docker Compose File
The docker-compose.yaml defines the Nav2 service:

name: g1_nav2_humble

services:

g1_nav2_humble:

image: theconstructai/g1_nav2:latest

privileged: true

network_mode: host  # Direct hardware access

container_name: g1_nav2_humble

environment:


## - ROS_DOMAIN_ID=0
volumes:

# Mount configuration files from host

- ./volumes/behavior.xml:/root/ros2_ws/.../behavior.xml

- ./volumes/controller.yaml:/root/ros2_ws/.../controller.yaml

- ./volumes/planner_server.yaml:/root/ros2_ws/.../planner_server.yaml

- ./volumes/recovery.yaml:/root/ros2_ws/.../recovery.yaml

- ./volumes/bt_navigator.yaml:/root/ros2_ws/.../bt_navigator.yaml

- ./volumes/map.yaml:/root/ros2_ws/.../map.yaml

- ./volumes/map_2.pgm:/root/ros2_ws/.../map_2.pgm


### Dockerfile Structure
The multi-stage Dockerfile optimizes the image:

# Stage 1: Build Stage

FROM ros:humble-ros-core AS build_stage

# Clone and build g1_nav2 packages

# Stage 2: Runtime Stage

FROM ros:humble-ros-core

# Install Nav2 runtime dependencies

RUN apt-get install ros-humble-nav2*

# Copy built artifacts from build stage


### Important: The container runs in privileged mode with host networking to access hardware devices and communicate with other ROS nodes.

## 3.5.3 Nav2 Components and Configuration Files

### Launch Architecture
The Nav2 stack is launched in two stages:

Map Server: Provides the static map

Path Planner Stack: All navigation components

# Launch sequence in container

ros2 launch map_server map_server.launch.py &

sleep 3  # Allow map server to initialize

ros2 launch path_planner_server pathplanner.launch.py


### Component Overview

### Launch File Structure
The pathplanner.launch.py coordinates all components:

def generate_launch_description():

return LaunchDescription([

Node(

package='nav2_controller',

executable='controller_server',

parameters=[controller_yaml]),

Node(

package='nav2_planner',

executable='planner_server',

parameters=[planner_yaml]),

# ... other nodes

Node(

package='nav2_lifecycle_manager',

executable='lifecycle_manager',

parameters=[{

'autostart': True,

'node_names': [

'planner_server',

'controller_server',

'behavior_server',

'bt_navigator'

]

}])

])


## 3.5.4 Costmap Configuration for G1

### Local Costmap (controller.yaml)
The local costmap is used for obstacle avoidance and local planning:

local_costmap:

local_costmap:

ros__parameters:

update_frequency: 10.0    # 10 Hz updates

publish_frequency: 10.0

global_frame: odom

robot_base_frame: base_link

rolling_window: True      # Moves with robot

width: 5                  # 5m x 5m window

height: 5

resolution: 0.10          # 10cm per cell

robot_radius: 0.25        # G1 robot radius

transform_tolerance: 3.0  # Increased for stability

plugins: ["obstacle_layer", "inflation_layer"]

obstacle_layer:

observation_sources: livox_lidar

livox_lidar:

topic: /livox/lidar

data_type: "PointCloud2"

clearing: True

marking: True

obstacle_max_range: 2.5

obstacle_min_range: 0.3  # Ignore close points


### Global Costmap (planner_server.yaml)
The global costmap combines the static map with sensor data:

global_costmap:

global_costmap:

ros__parameters:

update_frequency: 1.0     # Slower updates for global

publish_frequency: 0.5

global_frame: map

robot_base_frame: base_link

robot_radius: 0.25

transform_tolerance: 3.0

plugins: ["static_layer", "obstacle_layer", "inflation_layer"]

static_layer:

map_subscribe_transient_local: True

inflation_layer:

cost_scaling_factor: 3.0

inflation_radius: 0.3

Optimization Notes:

Voxel layer disabled for performance on G1's limited compute

Transform tolerance increased to 3.0s for network delays

Update frequencies tuned for balance between responsiveness and CPU usage


## 3.5.5 Controller and Planner Setup

### DWB Local Planner Configuration
The Dynamic Window Approach (DWB) controller is configured for the G1's motion capabilities:

FollowPath:

plugin: "dwb_core::DWBLocalPlanner"

# Velocity limits (matching G1 capabilities)

min_vel_x: -0.3

max_vel_x: 0.3

min_vel_y: -0.3    # Omnidirectional support

max_vel_y: 0.3

max_vel_theta: 2.0  # Rotation speed

# Acceleration limits

acc_lim_x: 2.5

acc_lim_y: 2.5

acc_lim_theta: 3.2

# Trajectory generation

vx_samples: 12

vy_samples: 8

vtheta_samples: 20

sim_time: 2.0  # Look-ahead time

# Critics (scoring functions)

critics: [

"RotateToGoal",    # Final orientation

"Oscillation",     # Prevent stuck behavior

"BaseObstacle",    # Obstacle avoidance

"GoalAlign",       # Goal direction

"PathAlign",       # Path following

"PathDist",        # Distance to path

"GoalDist"         # Distance to goal

]


### NavFn Global Planner
GridBased:

plugin: "nav2_navfn_planner/NavfnPlanner"

tolerance: 0.8      # Goal tolerance

use_astar: False    # Use Dijkstra for completeness

allow_unknown: True # Navigate through unknown areas


### Goal and Progress Checkers
# Goal checker - when to consider goal reached

general_goal_checker:

xy_goal_tolerance: 0.3     # 30cm position tolerance

yaw_goal_tolerance: 0.3    # ~17 degrees

# Progress checker - detect if robot is stuck

progress_checker:

required_movement_radius: 0.3

movement_time_allowance: 20.0

Tuning Tips:

Adjust velocity limits based on your safety requirements

Increase sim_time for smoother paths but higher CPU usage

Tune critic scales to balance path following vs obstacle avoidance


## 3.5.6 Launching Navigation in Sentinel simulation
And now we have to start the navigation systems.


### The first step is to check if the 2D map ( only used for the path planner, the localization uses the PointCloud ).

### Let's change the maps used by the map_server so that it loads the 2D map we generated in the mapping phase.
For that, check the file /home/user/ros2_ws/src/g1_nav2/map_server/launch/map_server.launch.py.

# Inside the `map_server.launch.py

def generate_launch_description():

map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'map_dec1.yaml')


### Now check that the /home/user/ros2_ws/src/g1_nav2/map_server/config/map_dec1.yaml has the correct PGM, and we will edit this file to adjust the orientation and position of the map, because it might be completely different from the real thing.
The best way is to restart the simulation with the RESET sim button

And then launch the following commands and see how it appears in RViz

Execute in Terminal #1

rviz2 -d /home/user/ros2_ws/src/g1_nav2/path_planner_server/rviz/g1_nav2.rviz

Execute in Terminal #2

cd ~/ros2_ws

colcon build --packages-select map_server

source install/setup.bash

ros2 launch map_server map_server.launch.py

Data:

origin:

- -4.646178245544434 # X position

- -3.969349670410157 # Y position

- 0.0 # yaw

# Depending on the way tou created the map , you might need to reorient the map, but this depends on you

# adjustements in map_dec1.yaml

origin:

- -4.646178245544434

- -3.969349670410157

- -0.1

In Other terminals now launch the rest of the systems:

Execute in Terminal #3

cd ~/ros2_ws/

source install/setup.bash

ros2 launch fast_lio odometry_only.launch.py use_sim_time:=true rviz:=false

Execute in Terminal #4

cd ~/ros2_ws/

source install/setup.bash

ros2 launch open3d_global_localization global_localization_g1.launch.py


## REMEMBER TO SET THE CORRECT 2D ESTIMATED POSE
Execute in Terminal #5

cd ~/ros2_ws/

source install/setup.bash

ros2 launch path_planner_server pathplanner.launch.py


## 3.5.7 Launching and Testing Navigation

### Starting the Nav2 Stack
Step 1: Navigate to Docker directory

cd ~/git-repo/g1_nav2/docker

Step 2: Build/Pull the Docker image

# Option A: Pull pre-built image

docker compose pull

# Option B: Build locally

docker compose build

Step 3: Start Nav2 container

docker compose up -d

Step 4: Monitor logs

docker compose logs -f


### Complete System Integration
To run the complete navigation system:

# Terminal 1: Start cmd_vel driver (from Unit 3.4)

unset CYCLONEDDS_HOME

ros2 run g1_sport_mode_ros g1_sport_multiprocess.py \

--ros-args -p interface:=eth0

# Terminal 2: Start Livox LiDAR

ros2 launch livox_ros_driver2 pointcloud2_MID360_launch.py

# Terminal 3: Open3D localization

# Terminal 4: Start Nav2 Docker container

cd ~/git-repo/g1_nav2/docker

docker compose up

# Terminal 4: Send navigation goals

ros2 topic pub /goal_pose geometry_msgs/PoseStamped \

'{header: {frame_id: "map"},

pose: {position: {x: 2.0, y: 1.0, z: 0.0},

orientation: {w: 1.0}}}'


### Configuration Adjustments
To modify navigation behavior, edit the configuration files in docker/volumes/:

# Edit controller parameters

nano ~/git-repo/g1_nav2/docker/volumes/controller.yaml

# Restart container to apply changes

docker compose down/up

Success Indicators:

All Nav2 nodes report as "active" in lifecycle state

Robot navigates to goals while avoiding obstacles

cmd_vel commands published continuously during navigation


# Unitree G1 Reinforcement Learning Course


## 4.1   RealSense2 Camera Integration for G1 Perception
> **Duration:** Estimated time to completion: 30 min
> **Objective:** earn how to integrate and configure the Intel RealSense D435i camera on the Unitree G1 robot using the official ROS 2 packages for depth perception, RGB imaging, and IMU data collection.
> **Topics:**
> - 4.1.1 RealSense2 Camera Hardware Overview
> - 4.1.2 Installing RealSense2 ROS 2 Packages
> - 4.1.3 Camera Configuration and Parameters
> - 4.1.4 Launch Files and Node Configuration
> - 4.1.5 Data Streams and Topic Structure
> - 4.1.6 Testing and Validation
> - 4.1.7 Integration with Nav2 and Perception Pipeline

## 4.1.1 RealSense2 Camera Hardware Overview

### The Intel RealSense D435i is a stereo depth camera commonly integrated with the Unitree G1 robot for advanced perception capabilities. It provides multiple data streams essential for autonomous navigation and manipulation.
RealSense D435i Capabilities:

Depth Stream: Up to 1280x720 at 30 FPS

RGB Stream: Up to 1920x1080 at 30 FPS

Infrared Streams: Stereo IR cameras for depth calculation

IMU Data: 6-DOF accelerometer and gyroscope

Range: 0.11m to 10m depth detection


### Camera Position on G1
The RealSense camera is typically mounted on the G1's head assembly:

G1 Robot Head Assembly

┌─────────────────────────────────────┐

│              Head Unit              │

│  ┌───────────────────────────────┐  │

│  │     RealSense D435i Camera    │  │

│  │                               │  │

│  │  [IR1] [RGB] [IR2]  [Proj]    │  │

│  │   ●     ●     ●       ●       │  │

│  └───────────────────────────────┘  │

└─────────────────────────────────────┘

│

Base Link Frame


### Frame Conventions
The RealSense camera follows standard ROS conventions:

camera_link: Base camera frame (center of depth sensor)

camera_color_frame: RGB camera optical frame

camera_depth_frame: Depth camera optical frame

camera_imu_frame: IMU sensor frame


## 4.1.2 Installing RealSense2 ROS 2 Packages

### Prerequisites
Before installing the ROS 2 packages, ensure your system is properly configured:

# Update system packages

sudo apt update && sudo apt upgrade -y

# Install USB development libraries (required for camera access)

sudo apt install -y libusb-1.0-0-dev pkg-config


### ROS 2 Package Installation
Install the official Intel RealSense ROS 2 package for ROS 2 Humble/Jazzy:

# For ROS 2 Humble (adjust for your ROS distribution)

sudo apt install -y ros-humble-realsense2-camera

sudo apt install -y ros-humble-realsense2-description

# For ROS 2 Jazzy

sudo apt install -y ros-jazzy-realsense2-camera

sudo apt install -y ros-jazzy-realsense2-description


### Verify Installation
Check that the packages are properly installed:

# Source ROS 2 environment

source /opt/ros/jazzy/setup.bash

# Check package installation

ros2 pkg list | grep realsense

# Should show:

# realsense2_camera

# realsense2_description

# List available launch files

ros2 pkg executables realsense2_camera


### Hardware Detection
Verify the camera is detected by the system:

# Check USB device detection

lsusb | grep Intel

# Should show: Intel Corp. RealSense D435i

# Check camera device nodes

ls /dev/video* | head -10

# Should show multiple video devices (typically /dev/video0, /dev/video1, etc.)


### USB Permissions: If you encounter permission issues, add your user to the video group: sudo usermod -a -G video $USER Then logout and login again.

## 4.1.3 Camera Configuration and Parameters

### Default Configuration Parameters
The RealSense2 ROS 2 package provides extensive configuration options. Key parameters for G1 integration:

# realsense_config.yaml

realsense2_camera:

ros__parameters:

# Camera resolution and frame rates

depth_module.profile: "640x480x30"

rgb_camera.profile: "640x480x30"

# Enable/disable streams

enable_depth: true

enable_color: true

enable_infra1: true

enable_infra2: true

enable_gyro: true

enable_accel: true

# Frame alignment

align_depth.enable: true

# Point cloud generation

pointcloud.enable: true

pointcloud.stream_filter: 2  # RS2_STREAM_COLOR

pointcloud.ordered_pc: false

# IMU settings

gyro_fps: 200

accel_fps: 250

unite_imu_method: 1  # copy

# Frame IDs (customize for G1)

base_frame_id: "camera_link"

depth_optical_frame_id: "camera_depth_optical_frame"

color_optical_frame_id: "camera_color_optical_frame"

# Performance tuning for G1

clip_distance: 4.0  # Clip depth beyond 4m

linear_accel_cov: 0.01

angular_velocity_cov: 0.01


### Optimized Settings for G1
For optimal performance on the G1's computational resources:

# Reduced resolution for better performance

depth_module.profile: "424x240x30"  # Lower resolution

rgb_camera.profile: "424x240x30"

# Disable unnecessary streams

enable_infra1: false

enable_infra2: false

# Optimize point cloud

pointcloud.allow_no_texture_points: false

pointcloud.ordered_pc: true  # Faster processing

# Quality vs Performance

depth_module.emitter_enabled: 1  # Enable laser projector

depth_module.enable_auto_exposure: true


### Custom Launch Configuration
Create a custom launch file for G1-specific settings:

# g1_realsense.launch.py

from launch import LaunchDescription

from launch_ros.actions import Node

from launch.actions import DeclareLaunchArgument

from launch.substitutions import LaunchConfiguration

def generate_launch_description():

return LaunchDescription([

DeclareLaunchArgument(

'camera_name',

default_value='camera',

description='Camera namespace'),

Node(

package='realsense2_camera',

executable='realsense2_camera_node',

name='realsense2_camera',

namespace=LaunchConfiguration('camera_name'),

parameters=[{

'depth_module.profile': '640x480x30',

'rgb_camera.profile': '640x480x30',

'enable_depth': True,

'enable_color': True,

'enable_gyro': True,

'enable_accel': True,

'align_depth.enable': True,

'pointcloud.enable': True,

'base_frame_id': 'camera_link',

'clip_distance': 4.0

}],

output='screen'

)

])


## 4.1.4 Launch Files and Node Configuration

### Basic Launch Commands
Simple camera launch:

# Launch with default parameters

ros2 launch realsense2_camera rs_launch.py

Launch with custom parameters:

# Launch with specific resolution and streams

ros2 launch realsense2_camera rs_launch.py \

depth_module.profile:=640x480x30 \

rgb_camera.profile:=640x480x30 \

pointcloud.enable:=true \

align_depth.enable:=true

Launch for G1 with ROS domain:

# Launch in G1's ROS domain (typically domain 1)

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

depth_module.profile:=640x480x30 \

rgb_camera.profile:=640x480x30 \

pointcloud.enable:=true \

base_frame_id:=camera_link


### Multiple Camera Setup
If using multiple RealSense cameras on G1:

# Camera 1 (head mounted)

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

camera_name:=head_camera \

device_type:=d435i \

serial_no:=f0123456  # Use actual serial number

# Camera 2 (chest mounted)

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

camera_name:=chest_camera \

device_type:=d435i \

serial_no:=f0654321


### Launch File Integration
Create a comprehensive G1 perception launch file:

# g1_perception.launch.py

from launch import LaunchDescription

from launch_ros.actions import Node

from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

import os

def generate_launch_description():

realsense_launch = IncludeLaunchDescription(

PythonLaunchDescriptionSource([

os.path.join(

get_package_share_directory('realsense2_camera'),

'launch', 'rs_launch.py'

)

]),

launch_arguments={

'depth_module.profile': '640x480x30',

'rgb_camera.profile': '640x480x30',

'pointcloud.enable': 'true',

'align_depth.enable': 'true',

'base_frame_id': 'camera_link'

}.items()

)

# Add static transform from base_link to camera_link

camera_tf = Node(

package='tf2_ros',

executable='static_transform_publisher',

arguments=['0', '0', '1.2', '0', '0', '0', 'base_link', 'camera_link']

)

return LaunchDescription([

realsense_launch,

camera_tf

])


### Service and Action Interfaces
The RealSense node provides several services for runtime configuration:

# List available services

ROS_DOMAIN_ID=1 ros2 service list | grep camera

# Common services:

# /camera/set_parameters - Runtime parameter changes

# /camera/get_device_info - Device information

# /camera/hardware_reset - Hardware reset


## 4.1.5 Data Streams and Topic Structure

### Available ROS 2 Topics
The RealSense2 camera publishes multiple data streams:


### Topic Inspection Commands
Check topic rates:

# Monitor image publication rates

ROS_DOMAIN_ID=1 ros2 topic hz /camera/color/image_raw

ROS_DOMAIN_ID=1 ros2 topic hz /camera/depth/image_rect_raw

ROS_DOMAIN_ID=1 ros2 topic hz /camera/depth/color/points

Inspect message contents:

# View single messages

ROS_DOMAIN_ID=1 ros2 topic echo /camera/color/camera_info --once

ROS_DOMAIN_ID=1 ros2 topic echo /camera/imu --once

# Check point cloud structure

ROS_DOMAIN_ID=1 ros2 topic echo /camera/depth/color/points --once | head -50


### Data Stream Configuration
Enable specific streams only:

# Depth and color only (no IMU)

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

enable_depth:=true \

enable_color:=true \

enable_gyro:=false \

enable_accel:=false

Point cloud customization:

# RGB point cloud with texture filtering

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

pointcloud.enable:=true \

pointcloud.stream_filter:=2 \

pointcloud.allow_no_texture_points:=false


### Frame Synchronization
For applications requiring synchronized RGB and depth data:

# Example Python subscriber for synchronized data

import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Image, PointCloud2

from message_filters import ApproximateTimeSynchronizer, Subscriber

class SynchronizedCameraSubscriber(Node):

def __init__(self):

super().__init__('synced_camera_subscriber')

# Create synchronized subscribers

self.color_sub = Subscriber(self, Image, '/camera/color/image_raw')

self.depth_sub = Subscriber(self, Image, '/camera/aligned_depth_to_color/image_raw')

# Synchronize messages

self.sync = ApproximateTimeSynchronizer(

[self.color_sub, self.depth_sub],

queue_size=10,

slop=0.1)

self.sync.registerCallback(self.synchronized_callback)

def synchronized_callback(self, color_msg, depth_msg):

# Process synchronized RGB and depth data

self.get_logger().info('Received synchronized images')


## 4.1.6 Testing and Validation

### Basic Functionality Tests
Step 1: Launch the camera

# Terminal 1: Start RealSense camera

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

depth_module.profile:=640x480x30 \

rgb_camera.profile:=640x480x30 \

pointcloud.enable:=true

Step 2: Verify node status

# Terminal 2: Check if camera node is running

ROS_DOMAIN_ID=1 ros2 node list | grep camera

# Should show: /camera/realsense2_camera

# Check topics are being published

ROS_DOMAIN_ID=1 ros2 topic list | grep camera

Step 3: Validate data streams

# Test RGB stream

ROS_DOMAIN_ID=1 ros2 topic hz /camera/color/image_raw

# Expected: ~30 Hz

# Test depth stream

ROS_DOMAIN_ID=1 ros2 topic hz /camera/depth/image_rect_raw

# Expected: ~30 Hz

# Test point cloud

ROS_DOMAIN_ID=1 ros2 topic hz /camera/depth/color/points

# Expected: ~15-30 Hz (depending on processing power)

# Test IMU data

ROS_DOMAIN_ID=1 ros2 topic hz /camera/imu

# Expected: ~200 Hz


### Visual Validation
Using RViz2 for visualization:

# Terminal 3: Launch RViz2

ROS_DOMAIN_ID=1 rviz2

RViz2 Configuration:

Set Fixed Frame to camera_link

Add displays:

Image: /camera/color/image_raw

Image: /camera/depth/image_rect_raw (use depth visualization)

PointCloud2: /camera/depth/color/points

Image viewing with ros2 tools:

# View RGB image

ROS_DOMAIN_ID=1 ros2 run rqt_image_view rqt_image_view /camera/color/image_raw

# View depth image

ROS_DOMAIN_ID=1 ros2 run rqt_image_view rqt_image_view /camera/depth/image_rect_raw


### Performance Monitoring
Check system resource usage:

# Monitor CPU and memory usage

top -p $(pgrep realsense2_camera)

# Check USB bandwidth usage

lsusb -t

# Look for RealSense device and bandwidth allocation

Network bandwidth monitoring:

# Monitor topic bandwidth

ROS_DOMAIN_ID=1 ros2 topic bw /camera/color/image_raw

ROS_DOMAIN_ID=1 ros2 topic bw /camera/depth/color/points


### Calibration Verification
Check camera calibration parameters:

# View RGB camera calibration

ROS_DOMAIN_ID=1 ros2 topic echo /camera/color/camera_info --once

# View depth camera calibration

ROS_DOMAIN_ID=1 ros2 topic echo /camera/depth/camera_info --once

Expected calibration parameters:

# camera_info typical values for D435i

width: 640

height: 480

distortion_model: plumb_bob

k: [fx, 0, cx, 0, fy, cy, 0, 0, 1]  # Intrinsic matrix

d: [k1, k2, t1, t2, k3]             # Distortion coefficients


### Troubleshooting Common Issues
Common Problems and Solutions:

Issue 1: Camera not detected

Check USB connection: lsusb | grep Intel

Verify device permissions: sudo chmod 666 /dev/video*

Try different USB port (preferably USB 3.0)

Issue 2: Low frame rates

Reduce resolution: depth_module.profile:=424x240x30

Disable unnecessary streams: enable_infra1:=false enable_infra2:=false

Check CPU usage: htop

Issue 3: Point cloud not publishing

Verify both depth and color streams are enabled

Check alignment: align_depth.enable:=true

Monitor topic: ros2 topic echo /camera/depth/color/points --once

Issue 4: IMU data missing

Enable IMU explicitly: enable_gyro:=true enable_accel:=true

Check IMU fusion method: unite_imu_method:=1

Verify topic: ros2 topic echo /camera/imu --once


## 4.1.7 Integration with Nav2 and Perception Pipeline

### TF Tree Integration
Properly integrate the camera into G1's transform tree:

# Add static transform from G1's base to camera

ROS_DOMAIN_ID=1 ros2 run tf2_ros static_transform_publisher \


### 0.05 0 1.2 0 0.1745 0 base_link camera_link
# Translation: 5cm forward, 1.2m up

# Rotation: 10 degrees downward tilt

Verify transform chain:

# Check complete transform chain

ROS_DOMAIN_ID=1 ros2 run tf2_ros tf2_echo base_link camera_color_optical_frame

ROS_DOMAIN_ID=1 ros2 run tf2_ros tf2_echo base_link camera_depth_optical_frame

# View transform tree

ROS_DOMAIN_ID=1 ros2 run tf2_tools view_frames

# Creates frames.pdf showing complete TF tree


### Obstacle Detection for Nav2
Configure the RealSense point cloud as an obstacle source:

# In Nav2 costmap configuration (controller.yaml)

local_costmap:

local_costmap:

ros__parameters:

plugins: ["obstacle_layer", "inflation_layer"]

obstacle_layer:

plugin: "nav2_costmap_2d::ObstacleLayer"

enabled: True

observation_sources: livox_lidar realsense_camera

# Existing LiDAR source

livox_lidar:

topic: /livox/lidar

data_type: "PointCloud2"

clearing: True

marking: True

# Add RealSense camera

realsense_camera:

topic: /camera/depth/color/points

data_type: "PointCloud2"

clearing: True

marking: True

obstacle_max_range: 3.0

obstacle_min_range: 0.3

raytrace_max_range: 4.0

raytrace_min_range: 0.0


### Point Cloud Filtering
Create a filtered point cloud for better obstacle detection:

# filtered_pointcloud.py

import rclpy

from rclpy.node import Node

from sensor_msgs.msg import PointCloud2

import sensor_msgs_py.point_cloud2 as pc2

import numpy as np

class PointCloudFilter(Node):

def __init__(self):

super().__init__('pointcloud_filter')

self.subscription = self.create_subscription(

PointCloud2,

'/camera/depth/color/points',

self.pointcloud_callback,

10)

self.publisher = self.create_publisher(

PointCloud2,

'/camera/depth/color/points_filtered',

10)

def pointcloud_callback(self, msg):

# Convert to numpy array

points = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)

points_array = np.array(list(points))

if len(points_array) == 0:

return

# Filter points (remove floor, ceiling, and far objects)

mask = (

(points_array[:, 2] > -0.5) &  # Above floor

(points_array[:, 2] < 2.0) &   # Below ceiling

(points_array[:, 0] < 3.0) &   # Within forward range

(points_array[:, 0] > 0.3)     # Beyond robot body

)

filtered_points = points_array[mask]

# Create filtered point cloud message

filtered_msg = pc2.create_cloud_xyz32(msg.header, filtered_points.tolist())

self.publisher.publish(filtered_msg)

# Launch with:

# ROS_DOMAIN_ID=1 ros2 run your_package filtered_pointcloud.py


### Complete G1 Perception Launch
Comprehensive launch file combining all perception components:

# g1_full_perception.launch.py

from launch import LaunchDescription

from launch_ros.actions import Node

from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

import os

def generate_launch_description():

# RealSense camera

realsense = IncludeLaunchDescription(

PythonLaunchDescriptionSource([

os.path.join(

get_package_share_directory('realsense2_camera'),

'launch', 'rs_launch.py'

)

]),

launch_arguments={

'depth_module.profile': '640x480x30',

'rgb_camera.profile': '640x480x30',

'pointcloud.enable': 'true',

'align_depth.enable': 'true'

}.items()

)

# Livox LiDAR

livox = IncludeLaunchDescription(

PythonLaunchDescriptionSource([

os.path.join(

get_package_share_directory('livox_ros_driver2'),

'launch', 'pointcloud2_MID360_launch.py'

)

])

)

# Static transforms

camera_tf = Node(

package='tf2_ros',

executable='static_transform_publisher',

arguments=['0.05', '0', '1.2', '0', '0.1745', '0', 'base_link', 'camera_link']

)

return LaunchDescription([

realsense,

livox,

camera_tf

])


### Launch Sequence for Complete System
# Terminal 1: Start G1 sport mode driver

unset CYCLONEDX_HOME

ROS_DOMAIN_ID=1 ros2 run g1_sport_mode_ros g1_sport_ros.py \

--ros-args -p interface:=enx00e04c696fc1

# Terminal 2: Start complete perception stack

ROS_DOMAIN_ID=1 ros2 launch your_package g1_full_perception.launch.py

# Terminal 3: Start Nav2 with camera integration

cd ~/git-repo/g1_nav2/docker

docker compose up

# Terminal 4: Verify integration

ROS_DOMAIN_ID=1 ros2 topic list | grep -E "(camera|costmap)"

ROS_DOMAIN_ID=1 ros2 topic hz /local_costmap/costmap

Integration Success Indicators:

RealSense point cloud visible in RViz2

Costmaps show obstacles detected by camera

Nav2 avoids obstacles seen by RealSense

Transform chain complete from base_link to camera frames


### Next Steps
With RealSense2 camera successfully integrated, you can now:

Add object detection using computer vision pipelines

Implement SLAM combining LiDAR and visual odometry

Create manipulation behaviors using RGB-D data

Develop advanced perception for human-robot interaction


### Continue to Unit 4 Sub 2: Advanced Perception Pipeline to learn about implementing computer vision algorithms and object detection on the G1.

# Unitree G1 Reinforcement Learning Course


## 4.2   Computer Vision Bag Detection with G1 Perception
> **Duration:** Estimated time to completion: 40 min
> **Objective:** earn how to implement computer vision algorithms on the Unitree G1 robot using RealSense camera data to detect red bags, calculate their 3D position, and broadcast transform frames for autonomous manipulation tasks.
> **Topics:**
> - 4.2.1 G1 Perception Package Overview
> - 4.2.2 Computer Vision Pipeline Architecture
> - 4.2.3 HSV Color Detection and Contour Analysis
> - 4.2.4 RGB-D Data Fusion and 3D Positioning
> - 4.2.5 Transform Broadcasting and Coordinate Systems
> - 4.2.6 Debug Visualization and Troubleshooting
> - 4.2.7 Running the Complete Detection System

## 4.2.1 G1 Perception Package Overview

### The g1_perception package provides computer vision capabilities for the Unitree G1 robot, specifically designed to work with the RealSense camera system configured in the previous unit. The package focuses on detecting and localizing objects for autonomous manipulation tasks.
Package Components:

reflex_bag_detection.py: Main detection node for red bag identification

Computer Vision Pipeline: HSV color filtering and contour analysis

3D Localization: RGB-D fusion for spatial positioning

Transform Broadcasting: Integration with ROS TF system


### Package Structure
~/git-repo/g1_perception/

├── g1_perception/

│   ├── __init__.py

│   └── reflex_bag_detection.py    # Main detection node

├── package.xml                    # Package metadata

├── setup.py                      # Installation configuration

└── test/                         # Unit tests


### Node Architecture
The BagDetectorViz node integrates multiple data streams:

┌─────────────────────────────────────────────┐

│             BagDetectorViz Node             │

├─────────────────────────────────────────────┤

│ Subscriptions:                              │

│  • /color/image_raw/compressed    (RGB)     │

│  • /depth/image_rect_raw          (Depth)   │

│  • /color/camera_info            (Calib)   │

├─────────────────────────────────────────────┤

│ Publications:                               │

│  • bag_debug_image               (Debug)    │

│  • depth_debug_image            (Viz)      │

│  • /tf                          (Transform) │

└─────────────────────────────────────────────┘


### Dependencies and Requirements
The detection system requires several key dependencies:

# Computer vision libraries

sudo apt install python3-opencv

pip3 install opencv-python

# ROS 2 CV bridge

sudo apt install ros-jazzy-cv-bridge

# Image processing utilities

sudo apt install ros-jazzy-image-transport

sudo apt install ros-jazzy-compressed-image-transport


## 4.2.2 Computer Vision Pipeline Architecture

### Processing Flow Overview
The bag detection system follows a structured computer vision pipeline:

RGB Image Input → HSV Conversion → Color Filtering → Contour Detection

↓                ↓                ↓                ↓

Depth Image ← Coordinate Mapping ← Bounding Box ← Largest Contour

↓

3D Position Calculation → Transform Broadcasting


### Core Processing Components
1. Image Synchronization

# Node maintains latest messages from all streams

self.color_msg = None    # Compressed RGB image

self.depth_msg = None    # Aligned depth image

self.camera_info = None  # Camera calibration parameters

# Processing triggered by timer at 1 Hz

self.create_timer(1.0, self.process)

2. Data Validation

def process(self):

if self.color_msg is None or self.depth_msg is None or self.camera_info is None:

return  # Wait for all data streams

3. Image Format Conversion

# Convert ROS messages to OpenCV format

color = self.bridge.compressed_imgmsg_to_cv2(self.color_msg, 'bgr8')

depth = self.bridge.imgmsg_to_cv2(self.depth_msg, 'passthrough')


### Multi-Resolution Coordinate Mapping
One of the key challenges is handling different resolutions between RGB and depth streams:

def scale_coordinates(self, u, v, color_shape, depth_shape):

"""Scale coordinates from color image space to depth image space"""

color_h, color_w = color_shape[:2]

depth_h, depth_w = depth_shape[:2]

# Proportional scaling

u_scaled = int(u * depth_w / color_w)

v_scaled = int(v * depth_h / color_h)

# Bounds checking

u_scaled = max(0, min(u_scaled, depth_w - 1))

v_scaled = max(0, min(v_scaled, depth_h - 1))

return u_scaled, v_scaled


### Error Handling and Robustness
The system includes comprehensive error handling:

def safe_depth_access(self, depth, v, u):

"""Safely access depth array with bounds checking"""

h, w = depth.shape[:2]

if 0 <= v < h and 0 <= u < w:

return depth[v, u]

else:

self.get_logger().warn(f"Depth access out of bounds: ({v}, {u}) for shape ({h}, {w})")

return 0


### Resolution Considerations: RealSense cameras often provide different resolutions for RGB (e.g., 640x480) and depth (e.g., 424x240) streams. The coordinate scaling ensures accurate pixel-to-depth mapping.

## 4.2.3 HSV Color Detection and Contour Analysis

### HSV Color Space Advantages
The system uses HSV (Hue, Saturation, Value) color space for robust red detection:

Why HSV for Red Detection:

Lighting Independence: Hue remains consistent under varying illumination

Red Wrap-around: Red spans 0° and 360° in hue wheel

Saturation Control: Filter out washed-out or desaturated colors

Brightness Tolerance: Value channel handles shadow variations


### Red Color Detection Implementation
# Convert BGR to HSV color space

hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

# Define red color ranges (handling hue wrap-around)

# Lower red range: 0-10 degrees

mask1 = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255))

# Upper red range: 170-180 degrees

mask2 = cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))

# Combine both red ranges

mask = mask1 | mask2


### HSV Parameter Breakdown

### Contour Analysis and Selection
# Find contours in the binary mask

contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if not contours:

self.get_logger().info("No red bag detected")

return

# Select the largest contour (assumed to be the target bag)

largest_contour = max(contours, key=cv2.contourArea)

# Get bounding rectangle

x, y, w, h = cv2.boundingRect(largest_contour)

# Calculate centroid

centroid_x = x + w // 2

centroid_y = y + h // 2


### Contour Filtering Strategies
Area-based filtering:

# Filter contours by minimum area

MIN_CONTOUR_AREA = 500  # pixels

valid_contours = [c for c in contours if cv2.contourArea(c) > MIN_CONTOUR_AREA]

Aspect ratio filtering:

# Filter by aspect ratio (bags are typically not extremely elongated)

def is_valid_aspect_ratio(contour):

x, y, w, h = cv2.boundingRect(contour)

aspect_ratio = w / h

return 0.3 < aspect_ratio < 3.0  # Reasonable bag proportions


### Color Calibration Tips
Lighting adaptation:

# Monitor HSV values in different lighting conditions

ros2 run image_view image_view /camera/color/image_raw

# Use color picker tools to fine-tune HSV ranges

Dynamic thresholding:

# Adaptive HSV ranges based on lighting conditions

def adapt_hsv_ranges(self, image):

# Analyze image brightness

brightness = cv2.mean(image)[2]  # V channel mean

if brightness < 100:  # Dark conditions

return (0, 100, 50), (10, 255, 200)  # Relaxed ranges

else:  # Normal conditions

return (0, 120, 70), (10, 255, 255)  # Standard ranges


### Tuning Strategy: Start with conservative HSV ranges and gradually expand them while testing under different lighting conditions. Use debug visualization to verify detection accuracy.

## 4.2.4 RGB-D Data Fusion and 3D Positioning

### Camera Intrinsic Parameters
The system extracts calibration parameters from the RealSense camera info:

# Extract camera intrinsics from CameraInfo message

fx = self.camera_info.k[0]  # Focal length X

fy = self.camera_info.k[4]  # Focal length Y

cx = self.camera_info.k[2]  # Principal point X

cy = self.camera_info.k[5]  # Principal point Y

# K matrix layout:

# [fx  0  cx]

# [ 0 fy  cy]

# [ 0  0   1]


### Pixel-to-3D Coordinate Transformation
The core function converts 2D pixel coordinates plus depth to 3D camera coordinates:

def pixel_to_3d(self, u, v, depth, fx, fy, cx, cy):

"""Convert pixel (u,v) + depth to 3D point in camera frame"""

# RealSense depth values are in millimeters - convert to meters

Z = depth / 1000.0  # mm → m

if Z == 0:

return None  # Invalid depth

# Pinhole camera model equations

X = (u - cx) * Z / fx  # Horizontal position

Y = (v - cy) * Z / fy  # Vertical position

return (X, Y, Z)


### Mathematical Foundation
The transformation is based on the pinhole camera model:

Camera Projection Equations:

u = fx * (X/Z) + cx

v = fy * (Y/Z) + cy

Inverse Transformation:

X = (u - cx) * Z / fx

Y = (v - cy) * Z / fy

Z = depth_value / 1000.0  # mm to m conversion


### Robust Depth Sampling
To handle noisy depth data, the system samples multiple points around the detected centroid:

# Sample 5x5 grid around the bag location

depth_samples = []

for dy in [-2, -1, 0, 1, 2]:

for dx in [-2, -1, 0, 1, 2]:

sample_depth = self.safe_depth_access(depth, cy_depth + dy, cx_depth + dx)

depth_samples.append(sample_depth)

# Filter out invalid (zero) depth values

depth_nonzero = [d for d in depth_samples if d > 0]

if depth_nonzero:

depth_min = min(depth_nonzero)

depth_max = max(depth_nonzero)

depth_avg = sum(depth_nonzero) / len(depth_nonzero)

# Use average if center pixel has invalid depth

if center_depth == 0:

depth_val = depth_avg


### Coordinate System Considerations

### Depth Data Quality Assessment
# Log depth sampling statistics for debugging

self.get_logger().info(f"Depth at bag location: {depth_val}")

self.get_logger().info(f"Depth at image center: {depth_center}")

self.get_logger().info(f"5x5 grid - Min: {depth_min}, Max: {depth_max}, Avg: {depth_avg:.1f}")


### Common Depth Issues and Solutions
Issue 1: Invalid depth values (zeros)

Cause: Reflective surfaces, transparent objects, or out-of-range targets

Solution: Use neighboring pixel averaging or fallback strategies

Issue 2: Depth noise

Cause: Sensor noise, especially at longer distances

Solution: Temporal filtering or median filtering

Issue 3: Resolution mismatch

Cause: Different RGB and depth resolutions

Solution: Coordinate scaling as implemented in the system


### Depth Range Optimization: RealSense D435i works best between 0.3m and 3m. Beyond this range, depth accuracy decreases significantly.

## 4.2.5 Transform Broadcasting and Coordinate Systems

### TF2 Transform Broadcasting
The system broadcasts the detected bag position as a TF frame for integration with the robot's planning systems:

# Create transform from camera to bag

t = TransformStamped()

t.header.stamp = self.get_clock().now().to_msg()

t.header.frame_id = "camera_color_optical_frame"  # Parent frame

t.child_frame_id = "reflex_bag"                   # Child frame

# Set 3D position

t.transform.translation.x = centroid_cam[0]   # Right (+) / Left (-)

t.transform.translation.y = -centroid_cam[1]  # Up (+) / Down (-) - INVERTED

t.transform.translation.z = centroid_cam[2]   # Forward (+) / Backward (-)

# Set orientation (identity - no rotation)

t.transform.rotation.x = 0.0

t.transform.rotation.y = 0.0

t.transform.rotation.z = 0.0

t.transform.rotation.w = 1.0

# Broadcast transform

self.tf_broadcaster.sendTransform(t)


### Coordinate Frame Hierarchy
The complete transform chain for G1 bag detection:

Transform Chain:

base_link → camera_link → camera_color_optical_frame → reflex_bag

↑            ↑                    ↑                    ↑

Robot Base   Camera Mount       Optical Center        Target Bag


### Y-Axis Inversion Explanation
The system inverts the Y coordinate to match ROS/RViz conventions:

# Camera optical frame: Y points DOWN

# ROS standard frame:    Y points UP

# Therefore: ROS_Y = -Camera_Y

t.transform.translation.y = -centroid_cam[1]

Visualization of coordinate systems:

Camera Optical Frame:     ROS Standard Frame:

Z (forward)              X (forward)

↑                        ↑

|                        |

|                        |

+-----> X (right)        +-----> Y (left)

/                        /

/                        /

↓ Y (down)               ↓ Z (up)


### Transform Query Commands
Check transform availability:

# List all available transforms

ROS_DOMAIN_ID=1 ros2 run tf2_ros tf2_echo base_link reflex_bag

# View complete transform tree

ROS_DOMAIN_ID=1 ros2 run tf2_tools view_frames

Monitor transform updates:

# Real-time transform monitoring

ROS_DOMAIN_ID=1 ros2 topic echo /tf --field transforms


### Integration with G1 Planning
The broadcast transform enables G1's manipulation system to:

Plan approach trajectories to the detected bag

Calculate inverse kinematics for arm positioning

Coordinate whole-body motion for pickup tasks

Update perception as the robot moves

Example usage in manipulation node:

# Query bag position in robot base frame

try:

transform = self.tf_buffer.lookup_transform(

'base_link',      # Target frame

'reflex_bag',     # Source frame

rclpy.time.Time() # Latest available

)

bag_x = transform.transform.translation.x

bag_y = transform.transform.translation.y

bag_z = transform.transform.translation.z

# Plan manipulation approach

self.plan_bag_approach(bag_x, bag_y, bag_z)

except TransformException as e:

self.get_logger().warn(f"Could not get bag transform: {e}")


### Transform Broadcasting Rate
# Processing rate affects transform update frequency

self.create_timer(1.0, self.process)  # 1 Hz updates

# For real-time manipulation, consider faster rates:

# self.create_timer(0.1, self.process)  # 10 Hz updates


### Performance Consideration: Higher processing rates provide more responsive transforms but increase CPU usage. Balance detection frequency with system performance requirements.

## 4.2.6 Debug Visualization and Troubleshooting

### Debug Image Publications
The system provides comprehensive debug visualization through multiple image topics:

# Publishers for debug visualization

self.debug_pub = self.create_publisher(Image, 'bag_debug_image', 10)

self.depth_debug_pub = self.create_publisher(Image, 'depth_debug_image', 10)

RGB Debug Image:

# Overlay detection results on original image

cv2.rectangle(color, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green bounding box

cv2.circle(color, (cx, cy), 5, (255, 0, 0), -1)          # Blue centroid

# Publish annotated image

debug_msg = self.bridge.cv2_to_imgmsg(color, encoding='bgr8')

self.debug_pub.publish(debug_msg)

Depth Debug Visualization:

# Create colorized depth image

depth_viz = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)

depth_viz = depth_viz.astype(np.uint8)

depth_viz = cv2.applyColorMap(depth_viz, cv2.COLORMAP_JET)

# Mark bag location on depth image

cv2.circle(depth_viz, (cx_depth, cy_depth), 10, (255, 255, 255), 2)  # White circle

cv2.circle(depth_viz, (cx_depth, cy_depth), 3, (0, 0, 0), -1)        # Black center

cv2.putText(depth_viz, f"BAG({cx_depth},{cy_depth})",

(cx_depth+15, cy_depth), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

# Mark image center for reference

center_x, center_y = depth.shape[1]//2, depth.shape[0]//2

cv2.circle(depth_viz, (center_x, center_y), 5, (0, 255, 0), -1)  # Green center


### Comprehensive Logging System
The node provides detailed logging for troubleshooting:

Coordinate mapping logs:

self.get_logger().info(f"Color coords: ({cx}, {cy}) -> Depth coords: ({cx_depth}, {cy_depth})")

self.get_logger().info(f"Color shape: {color.shape}, Depth shape: {depth.shape}")

Depth sampling analysis:

self.get_logger().info(f"Depth at bag location: {depth_val}")

self.get_logger().info(f"5x5 grid - Min: {depth_min}, Max: {depth_max}, Avg: {depth_avg:.1f}")

Spatial reasoning logs:

self.get_logger().info(f"Bag is {'RIGHT' if cx > color_w//2 else 'LEFT'} of center")

self.get_logger().info(f"Bag is {'BELOW' if cy > color_h//2 else 'ABOVE'} center")


### Viewing Debug Images
Using image_view:

# View RGB debug image with detection overlays

ROS_DOMAIN_ID=1 ros2 run image_view image_view /bag_debug_image

# View depth debug visualization

ROS_DOMAIN_ID=1 ros2 run image_view image_view /depth_debug_image

Using RViz2:

# Launch RViz2 for comprehensive visualization

ROS_DOMAIN_ID=1 rviz2

RViz2 Configuration for debugging:

Add Image displays:

/bag_debug_image - RGB with detection overlays

/depth_debug_image - Colorized depth with markers

/camera/color/image_raw - Original RGB stream

Add TF display to visualize transform hierarchy

Add Axes display at reflex_bag frame


### Common Issues and Debug Strategies
Issue 1: No bag detected

# Debug: Check original image

ros2 run image_view image_view /camera/color/image_raw

# Debug: Verify HSV color ranges

# Adjust detection parameters in the code

Issue 2: Incorrect 3D position

# Check depth image quality

ros2 run image_view image_view /camera/depth/image_rect_raw

# Verify transform chain

ros2 run tf2_ros tf2_echo camera_color_optical_frame reflex_bag

Issue 3: Coordinate mapping errors

# Check image resolutions

ros2 topic echo /camera/color/camera_info --once

ros2 topic echo /camera/depth/camera_info --once


### Performance Monitoring
# Monitor processing rate

ros2 topic hz /bag_debug_image

# Check CPU usage

top -p $(pgrep -f reflex_bag_detection)

# Monitor memory usage

ros2 run ros2_introspection introspection_node


### Color Detection Tuning
Interactive HSV tuning tool:

# Create HSV trackbars for real-time tuning

cv2.namedWindow('HSV Tuning')

cv2.createTrackbar('H Min', 'HSV Tuning', 0, 179, lambda x: None)

cv2.createTrackbar('S Min', 'HSV Tuning', 120, 255, lambda x: None)

cv2.createTrackbar('V Min', 'HSV Tuning', 70, 255, lambda x: None)

cv2.createTrackbar('H Max', 'HSV Tuning', 10, 179, lambda x: None)

cv2.createTrackbar('S Max', 'HSV Tuning', 255, 255, lambda x: None)

cv2.createTrackbar('V Max', 'HSV Tuning', 255, 255, lambda x: None)


### Debug Workflow: Use the debug images to verify each stage of processing: color detection → contour analysis → depth lookup → 3D positioning → transform broadcasting.

## 4.2.7 Running the Complete Detection System

### Package Installation and Setup
Step 1: Navigate to the package and build

# Ensure you're in the correct workspace

cd ~/git-repo/g1_perception

# Build the package

colcon build --packages-select g1_perception

# Source the built package

source install/setup.bash

Step 2: Verify installation

# Check if the executable is available

ros2 pkg executables g1_perception

# Should show: g1_perception reflex_bag_detection

# Verify package contents

ros2 pkg list | grep g1_perception


### Complete System Launch Sequence
Terminal 1: Start RealSense Camera

# Launch RealSense with appropriate settings

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

depth_module.profile:=640x480x30 \

rgb_camera.profile:=640x480x30 \

pointcloud.enable:=true \

align_depth.enable:=true \

enable_compressed:=true

Terminal 2: Start the bag detection node

# Run the perception node

ROS_DOMAIN_ID=1 ros2 run g1_perception reflex_bag_detection

Terminal 3: Launch visualization (optional)

# Start RViz2 for 3D visualization

ROS_DOMAIN_ID=1 rviz2

Terminal 4: Monitor debug images

# View RGB debug image

ROS_DOMAIN_ID=1 ros2 run image_view image_view /bag_debug_image

# Or view depth debug image

ROS_DOMAIN_ID=1 ros2 run image_view image_view /depth_debug_image


### System Verification
Check active nodes:

ROS_DOMAIN_ID=1 ros2 node list

# Should include: /bag_detector_viz, /camera/realsense2_camera

Verify topic publications:

# Check detection debug topics

ROS_DOMAIN_ID=1 ros2 topic list | grep -E "(debug|bag)"

# Should show: /bag_debug_image, /depth_debug_image

# Monitor publication rates

ROS_DOMAIN_ID=1 ros2 topic hz /bag_debug_image

ROS_DOMAIN_ID=1 ros2 topic hz /tf

Test transform availability:

# Check if bag transform is being published

ROS_DOMAIN_ID=1 ros2 run tf2_ros tf2_echo camera_color_optical_frame reflex_bag

# List all transforms

ROS_DOMAIN_ID=1 ros2 topic echo /tf --field transforms.header.frame_id


### Integration with G1 Robot System
Complete G1 perception stack launch:

# Terminal 1: G1 Sport Mode Driver

unset CYCLONEDX_HOME

ROS_DOMAIN_ID=1 ros2 run g1_sport_mode_ros g1_sport_ros.py \

--ros-args -p interface:=enx00e04c696fc1

# Terminal 2: RealSense Camera

ROS_DOMAIN_ID=1 ros2 launch realsense2_camera rs_launch.py \

depth_module.profile:=640x480x30 \

rgb_camera.profile:=640x480x30 \

pointcloud.enable:=true \

align_depth.enable:=true \

enable_compressed:=true

# Terminal 3: Camera-to-Base Transform

ROS_DOMAIN_ID=1 ros2 run tf2_ros static_transform_publisher \


### 0.05 0 1.2 0 0.1745 0 base_link camera_link
# Terminal 4: Bag Detection

ROS_DOMAIN_ID=1 ros2 run g1_perception reflex_bag_detection

# Terminal 5: Nav2 (if needed for autonomous navigation)

cd ~/git-repo/g1_nav2/docker

docker compose up


### Testing with Physical Setup
Preparation:

Place a red bag in the camera's field of view

Ensure adequate lighting conditions

Position the bag at various distances (0.5m - 3m)

Validation steps:

# 1. Verify bag detection in logs

# Look for: "Bag detected at pixel: (x, y)"

# 2. Check 3D position makes sense

# Look for: "Broadcasting reflex_bag at: x=...m, y=...m, z=...m"

# 3. Visualize in RViz2

# Add TF display and look for 'reflex_bag' frame


### Performance Optimization
For real-time applications:

# Increase processing frequency

self.create_timer(0.2, self.process)  # 5 Hz instead of 1 Hz

# Reduce image resolution for faster processing

# In RealSense launch:

# depth_module.profile:=424x240x30

# rgb_camera.profile:=424x240x30

For computational efficiency:

# Process every N frames instead of every frame

self.frame_count = 0

if self.frame_count % 3 == 0:  # Process every 3rd frame

self.process_detection()

self.frame_count += 1


### Success Indicators
System Working Correctly When:

Debug images show green bounding boxes around red objects

Depth debug image shows white circles at detected bag locations

Console logs report reasonable 3D coordinates (e.g., 0.5-3m forward)

TF transforms are published at 1 Hz rate

RViz2 shows 'reflex_bag' frame moving with physical bag


### Next Steps
With the bag detection system running successfully, you can now:

Integrate with manipulation planning - Use the reflex_bag transform for arm control

Add multiple object detection - Extend the system to detect different colored objects

Implement tracking - Add temporal consistency for moving objects

Create manipulation behaviors - Plan approach and pickup sequences


### Continue to Unit 5: Autonomous Manipulation to learn about integrating this perception system with G1's manipulation capabilities for complete autonomous task execution.

import mujoco
import numpy as np
import pygame
import sys
import struct

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelPublisher

from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import WirelessController_
from unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitree_sdk2py.idl.default import unitree_go_msg_dds__WirelessController_
from unitree_sdk2py.utils.thread import RecurrentThread

import config
if config.ROBOT=="g1":
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowState_ as LowState_default
else:
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowCmd_
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_
    from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_ as LowState_default

TOPIC_LOWCMD = "rt/lowcmd"
TOPIC_LOWSTATE = "rt/lowstate"
TOPIC_HIGHSTATE = "rt/sportmodestate"
TOPIC_WIRELESS_CONTROLLER = "rt/wirelesscontroller"

MOTOR_SENSOR_NUM = 3
NUM_MOTOR_IDL_GO = 20
NUM_MOTOR_IDL_HG = 35

class UnitreeSdk2Bridge:

    def __init__(self, mj_model, mj_data):
        self.mj_model = mj_model
        self.mj_data = mj_data

        self.num_motor = self.mj_model.nu
        self.dim_motor_sensor = MOTOR_SENSOR_NUM * self.num_motor
        self.have_imu = False
        self.have_frame_sensor = False
        self.dt = self.mj_model.opt.timestep
        self.idl_type = (self.num_motor > NUM_MOTOR_IDL_GO) # 0: unitree_go, 1: unitree_hg

        self.joystick = None

        # Check sensor
        for i in range(self.dim_motor_sensor, self.mj_model.nsensor):
            name = mujoco.mj_id2name(
                self.mj_model, mujoco._enums.mjtObj.mjOBJ_SENSOR, i
            )
            if name == "imu_quat":
                self.have_imu_ = True
            if name == "frame_pos":
                self.have_frame_sensor_ = True

        # Unitree sdk2 message
        self.low_state = LowState_default()
        self.low_state_puber = ChannelPublisher(TOPIC_LOWSTATE, LowState_)
        self.low_state_puber.Init()
        self.lowStateThread = RecurrentThread(
            interval=self.dt, target=self.PublishLowState, name="sim_lowstate"
        )
        self.lowStateThread.Start()

        self.high_state = unitree_go_msg_dds__SportModeState_()
        self.high_state_puber = ChannelPublisher(TOPIC_HIGHSTATE, SportModeState_)
        self.high_state_puber.Init()
        self.HighStateThread = RecurrentThread(
            interval=self.dt, target=self.PublishHighState, name="sim_highstate"
        )
        self.HighStateThread.Start()

        self.wireless_controller = unitree_go_msg_dds__WirelessController_()
        self.wireless_controller_puber = ChannelPublisher(
            TOPIC_WIRELESS_CONTROLLER, WirelessController_
        )
        self.wireless_controller_puber.Init()
        self.WirelessControllerThread = RecurrentThread(
            interval=0.01,
            target=self.PublishWirelessController,
            name="sim_wireless_controller",
        )
        self.WirelessControllerThread.Start()

        self.low_cmd_suber = ChannelSubscriber(TOPIC_LOWCMD, LowCmd_)
        self.low_cmd_suber.Init(self.LowCmdHandler, 10)

        # joystick
        self.key_map = {
            "R1": 0,
            "L1": 1,
            "start": 2,
            "select": 3,
            "R2": 4,
            "L2": 5,
            "F1": 6,
            "F2": 7,
            "A": 8,
            "B": 9,
            "X": 10,
            "Y": 11,
            "up": 12,
            "right": 13,
            "down": 14,
            "left": 15,
        }

    def LowCmdHandler(self, msg: LowCmd_):
        """
        Apply LowCmd with deploy/local-runner parity:
          - If kp==kd==0 → pure tau (feedforward)
          - Else: ctrl = tau + kp*(q_des - q_meas) + kd*(dq_des - dq_meas)
          - Zero any actuators not covered by the message (keeps non-leg DoFs inert)
        """
        if self.mj_data is None:
            return

        # Bound by actual message length
        N = min(self.num_motor, len(msg.motor_cmd))

        # Prefer sensordata blocks: [q(0..nu-1), dq(nu..2nu-1), tau(2nu..3nu-1)]
        sd = self.mj_data.sensordata
        have_blocks = (sd.shape[0] >= 2 * self.num_motor)

        for i in range(N):
            mc = msg.motor_cmd[i]
            if mc.kp == 0.0 and mc.kd == 0.0:
                # No PD → pure torque
                self.mj_data.ctrl[i] = float(mc.tau)
            else:
                if have_blocks:
                    q_meas  = float(sd[i])
                    dq_meas = float(sd[self.num_motor + i])
                else:
                    # Fallback if blocks aren't present
                    q_meas  = 0.0
                    dq_meas = 0.0
                self.mj_data.ctrl[i] = (
                    float(mc.tau)
                    + float(mc.kp) * (float(mc.q)  - q_meas)
                    + float(mc.kd) * (float(mc.dq) - dq_meas)
                )

        # Zero any remaining actuators (e.g., arms/waist) to match deploy behavior
        for i in range(N, self.num_motor):
            self.mj_data.ctrl[i] = 0.0

    def PublishLowState(self):
        """
        Publish per-motor q/dq/tau_est. Layout preserved (motor_state[i].q, etc.)
        Falls back to state arrays if contiguous sensor blocks aren't present.
        """
        if self.mj_data is None:
            return

        sd = self.mj_data.sensordata
        nu = int(self.num_motor)
        have_blocks = (sd.shape[0] >= 3 * nu)

        for i in range(self.num_motor):
            if have_blocks:
                self.low_state.motor_state[i].q = sd[i]
                self.low_state.motor_state[i].dq = sd[i + nu]
                self.low_state.motor_state[i].tau_est = sd[i + 2 * nu]
            else:
                # Conservative fallback
                q = self.mj_data.qpos[7 + i] if (7 + i) < self.mj_data.qpos.shape[0] else 0.0
                dq = self.mj_data.qvel[6 + i] if (6 + i) < self.mj_data.qvel.shape[0] else 0.0
                self.low_state.motor_state[i].q = q
                self.low_state.motor_state[i].dq = dq
                self.low_state.motor_state[i].tau_est = 0.0

        # Keep existing optional joystick payload
        if self.joystick != None:
            pygame.event.get()
            # Buttons
            self.low_state.wireless_remote[2] = int(
                "".join(
                    [
                        f"{key}"
                        for key in [
                            0,
                            0,
                            int(self.joystick.get_axis(self.axis_id["LT"]) > 0),
                            int(self.joystick.get_axis(self.axis_id["RT"]) > 0),
                            int(self.joystick.get_button(self.button_id["SELECT"])),
                            int(self.joystick.get_button(self.button_id["START"])),
                            int(self.joystick.get_button(self.button_id["LB"])),
                            int(self.joystick.get_button(self.button_id["RB"])),
                        ]
                    ]
                ),
                2,
            )
            self.low_state.wireless_remote[3] = int(
                "".join(
                    [
                        f"{key}"
                        for key in [
                            int(self.joystick.get_hat(0)[0] < 0),  # left
                            int(self.joystick.get_hat(0)[1] < 0),  # down
                            int(self.joystick.get_hat(0)[0] > 0),  # right
                            int(self.joystick.get_hat(0)[1] > 0),  # up
                            int(self.joystick.get_button(self.button_id["Y"])),  # Y
                            int(self.joystick.get_button(self.button_id["X"])),  # X
                            int(self.joystick.get_button(self.button_id["B"])),  # B
                            int(self.joystick.get_button(self.button_id["A"])),  # A
                        ]
                    ]
                ),
                2,
            )
            # Axes
            sticks = [
                self.joystick.get_axis(self.axis_id["LX"]),
                self.joystick.get_axis(self.axis_id["RX"]),
                -self.joystick.get_axis(self.axis_id["RY"]),
                -self.joystick.get_axis(self.axis_id["LY"]),
            ]
            packs = list(map(lambda x: struct.pack("f", x), sticks))
            self.low_state.wireless_remote[4:8] = packs[0]
            self.low_state.wireless_remote[8:12] = packs[1]
            self.low_state.wireless_remote[12:16] = packs[2]
            self.low_state.wireless_remote[20:24] = packs[3]

        self.low_state_puber.Write(self.low_state)

    def PublishHighState(self):
        """
        Publish IMU/pose with deploy/local-runner parity:
          - imu_state.quaternion = qpos[3:7] (w,x,y,z)
          - imu_state.gyroscope  = qvel[3:6] (wx,wy,wz)
        Also keeps your existing position/velocity xyz fields.
        """
        if self.mj_data is None:
            return

        qpos = self.mj_data.qpos
        qvel = self.mj_data.qvel

        # Optional base position/linear velocity (not used by policy, harmless to publish)
        if qpos.shape[0] >= 3:
            self.high_state.position[0] = qpos[0]
            self.high_state.position[1] = qpos[1]
            self.high_state.position[2] = qpos[2]

        if qvel.shape[0] >= 3:
            self.high_state.velocity[0] = qvel[0]
            self.high_state.velocity[1] = qvel[1]
            self.high_state.velocity[2] = qvel[2]

        # IMU-parity with local runner
        if qpos.shape[0] >= 7 and qvel.shape[0] >= 6:
            self.high_state.imu_state.quaternion[0] = qpos[3]
            self.high_state.imu_state.quaternion[1] = qpos[4]
            self.high_state.imu_state.quaternion[2] = qpos[5]
            self.high_state.imu_state.quaternion[3] = qpos[6]
            self.high_state.imu_state.gyroscope[0]  = qvel[3]
            self.high_state.imu_state.gyroscope[1]  = qvel[4]
            self.high_state.imu_state.gyroscope[2]  = qvel[5]

        self.high_state_puber.Write(self.high_state)

    def PublishWirelessController(self):
        if self.joystick != None:
            pygame.event.get()
            key_state = [0] * 16
            key_state[self.key_map["R1"]] = self.joystick.get_button(
                self.button_id["RB"]
            )
            key_state[self.key_map["L1"]] = self.joystick.get_button(
                self.button_id["LB"]
            )
            key_state[self.key_map["start"]] = self.joystick.get_button(
                self.button_id["START"]
            )
            key_state[self.key_map["select"]] = self.joystick.get_button(
                self.button_id["SELECT"]
            )
            key_state[self.key_map["R2"]] = (
                self.joystick.get_axis(self.axis_id["RT"]) > 0
            )
            key_state[self.key_map["L2"]] = (
                self.joystick.get_axis(self.axis_id["LT"]) > 0
            )
            key_state[self.key_map["F1"]] = 0
            key_state[self.key_map["F2"]] = 0
            key_state[self.key_map["A"]] = self.joystick.get_button(self.button_id["A"])
            key_state[self.key_map["B"]] = self.joystick.get_button(self.button_id["B"])
            key_state[self.key_map["X"]] = self.joystick.get_button(self.button_id["X"])
            key_state[self.key_map["Y"]] = self.joystick.get_button(self.button_id["Y"])
            key_state[self.key_map["up"]] = self.joystick.get_hat(0)[1] > 0
            key_state[self.key_map["right"]] = self.joystick.get_hat(0)[0] > 0
            key_state[self.key_map["down"]] = self.joystick.get_hat(0)[1] < 0
            key_state[self.key_map["left"]] = self.joystick.get_hat(0)[0] < 0

            key_value = 0
            for i in range(16):
                key_value += key_state[i] << i

            self.wireless_controller.keys = key_value
            self.wireless_controller.lx = self.joystick.get_axis(self.axis_id["LX"])
            self.wireless_controller.ly = -self.joystick.get_axis(self.axis_id["LY"])
            self.wireless_controller.rx = self.joystick.get_axis(self.axis_id["RX"])
            self.wireless_controller.ry = -self.joystick.get_axis(self.axis_id["RY"])

            self.wireless_controller_puber.Write(self.wireless_controller)

    def SetupJoystick(self, device_id=0, js_type="xbox"):
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(device_id)
            self.joystick.init()
        else:
            print("No gamepad detected.")
            sys.exit()

        if js_type == "xbox":
            self.axis_id = {
                "LX": 0,  # Left stick axis x
                "LY": 1,  # Left stick axis y
                "RX": 3,  # Right stick axis x
                "RY": 4,  # Right stick axis y
                "LT": 2,  # Left trigger
                "RT": 5,  # Right trigger
                "DX": 6,  # Directional pad x
                "DY": 7,  # Directional pad y
            }

            self.button_id = {
                "X": 2,
                "Y": 3,
                "B": 1,
                "A": 0,
                "LB": 4,
                "RB": 5,
                "SELECT": 6,
                "START": 7,
            }

        elif js_type == "switch":
            self.axis_id = {
                "LX": 0,  # Left stick axis x
                "LY": 1,  # Left stick axis y
                "RX": 2,  # Right stick axis x
                "RY": 3,  # Right stick axis y
                "LT": 5,  # Left trigger
                "RT": 4,  # Right trigger
                "DX": 6,  # Directional pad x
                "DY": 7,  # Directional pad y
            }

            self.button_id = {
                "X": 3,
                "Y": 4,
                "B": 1,
                "A": 0,
                "LB": 6,
                "RB": 7,
                "SELECT": 10,
                "START": 11,
            }
        else:
            print("Unsupported gamepad. ")

    def PrintSceneInformation(self):
        print(" ")

        print("<<------------- Link ------------->> ")
        for i in range(self.mj_model.nbody):
            name = mujoco.mj_id2name(self.mj_model, mujoco._enums.mjtObj.mjOBJ_BODY, i)
            if name:
                print("link_index:", i, ", name:", name)
        print(" ")

        print("<<------------- Joint ------------->> ")
        for i in range(self.mj_model.njnt):
            name = mujoco.mj_id2name(self.mj_model, mujoco._enums.mjtObj.mjOBJ_JOINT, i)
            if name:
                print("joint_index:", i, ", name:", name)
        print(" ")

        print("<<------------- Actuator ------------->>")
        for i in range(self.mj_model.nu):
            name = mujoco.mj_id2name(
                self.mj_model, mujoco._enums.mjtObj.mjOBJ_ACTUATOR, i
            )
            if name:
                print("actuator_index:", i, ", name:", name)
        print(" ")

        print("<<------------- Sensor ------------->>")
        index = 0
        for i in range(self.mj_model.nsensor):
            name = mujoco.mj_id2name(
                self.mj_model, mujoco._enums.mjtObj.mjOBJ_SENSOR, i
            )
            if name:
                print(
                    "sensor_index:",
                    index,
                    ", name:",
                    name,
                    ", dim:",
                    self.mj_model.sensor_dim[i],
                )
            index = index + self.mj_model.sensor_dim[i]
        print(" ")


class ElasticBand:

    def __init__(self):
        self.stiffness = 200
        self.damping = 100
        self.point = np.array([0, 0, 3])
        self.length = 0
        self.enable = True

    def Advance(self, x, dx):
        """
        Args:
          δx: desired position - current position
          dx: current velocity
        """
        δx = self.point - x
        distance = np.linalg.norm(δx)
        direction = δx / distance
        v = np.dot(dx, direction)
        f = (self.stiffness * (distance - self.length) - self.damping * v) * direction
        return f

    def MujuocoKeyCallback(self, key):
        glfw = mujoco.glfw.glfw
        if key == glfw.KEY_7:
            self.length -= 0.1
        if key == glfw.KEY_8:
            self.length += 0.1
        if key == glfw.KEY_9:
            self.enable = not self.enable

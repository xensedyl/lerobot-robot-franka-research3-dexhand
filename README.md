# LeRobot Franka Research 3 + Revo2 Hand Robot

[中文版说明](./README.zh-CN.md)

Standalone LeRobot robot plugin for a Franka Research 3 arm with a Revo2
dexterous hand.

The package registers:

- `--robot.type=franka_research3_dexhand`

It composes two standalone robot plugins:

- `lerobot-robot-franka-research3`
- `lerobot-robot-revo2-hand`

The arm is controlled by the Franky-backed `FrankaResearch3` robot, and the
dexterous hand is controlled by the Revo2 SDK-backed `Revo2Hand` robot.

## Dependency Packages

Install the two dependency plugins first:

```bash
pip install -e ./lerobot-robot-franka-research3
pip install -e ./lerobot-robot-revo2-hand
```

The Franka package also requires `franky`. If you use a local checkout, first
initialize the `ruckig` submodule and install without pip build isolation:

```bash
cd franky
git submodule update --init --recursive
pip install -e . --no-build-isolation
```

The `ruckig` submodule is required by CMake; an empty `ruckig/` directory will
fail with `does not contain a CMakeLists.txt file`. `--no-build-isolation`
avoids pip isolated-build failures when `cmake` is installed from the Python
`cmake` package.

You can also install the fork directly:

```bash
pip install "franky-control @ git+ssh://git@github.com/xensedyl/franky.git"
```

The Revo2 package requires BrainCo's SDK module:

```text
bc_stark_sdk.main_mod
```

## Install This Plugin

```bash
cd lerobot-robot-franka-research3-dexhand
pip install -e .
```

## USB Serial Permissions

If Revo2 or an FTDI-based USB serial device cannot be opened, configure udev
permissions for the FTDI FT2232 device (`0403:6010`). This is the recommended
persistent fix.

```bash
sudo tee /etc/udev/rules.d/99-ftdi-ft2232.rules >/dev/null <<'EOF'
# FTDI FT2232C/D/H Dual UART/FIFO (0403:6010)
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", MODE:="0666", GROUP="dialout"
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", MODE:="0666", GROUP="dialout", ENV{ID_MM_DEVICE_IGNORE}="1"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and replug the USB device after reloading the rules if the permissions do
not update immediately.

For a temporary test, you can directly relax permissions on the current
`ttyUSB` nodes:

```bash
ls -l /dev/ttyUSB*
sudo chmod 666 /dev/ttyUSB*
```

The `chmod` method is not persistent. It must be repeated after unplugging the
device, rebooting, or if the device is assigned a new `/dev/ttyUSB*` path.

## Pico4 Hand Teleoperation

With `lerobot-teleoperator-pico4-hand` installed:

```bash
lerobot-teleoperate-pico4-hand \
  --robot.type=franka_research3_dexhand \
  --robot.fci_ip=192.168.99.111 \
  --robot.control_mode=cartesian_impedance \
  --robot.use_gripper=false \
  --robot.dexhand_hand_type=left \
  --robot.dexhand_auto_detect_quick=true \
  --teleop.type=pico4_hand \
  --teleop.hand_type=left \
  --teleop.robot_name=revo2 \
  --teleop.retargeting_type=vector \
  --fps=30 \
  --display_data=false
```

The combined action space includes the Franka TCP action keys and the Revo2
hand joint action keys, for example:

```text
tcp.x tcp.y tcp.z tcp.r1 ... tcp.r6
l_th_prox.pos l_th_mcp.pos l_idx_prox.pos l_mid_prox.pos l_ring_prox.pos l_pky_prox.pos
```

## Notes

This package disables the serial gripper on the Franka arm side and uses the
configured dexterous hand instead. The default dexhand type is `revo2_hand`.

Install and verify the arm-only and hand-only plugins before running the
combined robot on hardware.

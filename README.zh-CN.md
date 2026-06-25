# LeRobot Franka Research 3 + Revo2 Hand Robot

这是 Franka Research 3 机械臂 + Revo2 灵巧手的独立 LeRobot robot 插件包。

该包注册：

- `--robot.type=franka_research3_dexhand`

它依赖两个独立包：

- `lerobot-robot-franka-research3`
- `lerobot-robot-revo2-hand`

机械臂部分使用 Franky-backed `FrankaResearch3`，灵巧手部分使用
Revo2 SDK-backed `Revo2Hand`。

## 依赖包安装

先安装两个依赖插件：

```bash
pip install -e ./lerobot-robot-franka-research3
pip install -e ./lerobot-robot-revo2-hand
```

Franka 包还需要 `franky`。如果使用本地源码，先初始化 `ruckig` 子模块，
再关闭 pip build isolation 安装：

```bash
cd franky
git submodule update --init --recursive
pip install -e . --no-build-isolation
```

`ruckig` 是 CMake 必需的子模块；如果 `ruckig/` 是空目录，会报
`does not contain a CMakeLists.txt file`。如果当前环境里的 `cmake` 来自
Python `cmake` 包，`--no-build-isolation` 可以避免 pip 隔离构建环境里
`ModuleNotFoundError: No module named 'cmake'`。

也可以直接从 Git 安装：

```bash
pip install "franky-control @ git+ssh://git@github.com/xensedyl/franky.git"
```

Revo2 包需要 BrainCo SDK 模块：

```text
bc_stark_sdk.main_mod
```

## 安装本插件

```bash
cd lerobot-robot-franka-research3-dexhand
pip install -e .
```

## USB 串口权限配置

如果 Revo2 或基于 FTDI 的 USB 串口设备无法打开，可以为 FTDI FT2232 设备
`0403:6010` 配置 udev 权限。这是推荐的长期方案。

```bash
sudo tee /etc/udev/rules.d/99-ftdi-ft2232.rules >/dev/null <<'EOF'
# FTDI FT2232C/D/H Dual UART/FIFO (0403:6010)
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", MODE:="0666", GROUP="dialout"
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", MODE:="0666", GROUP="dialout", ENV{ID_MM_DEVICE_IGNORE}="1"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

如果权限没有立即更新，重新插拔 USB 设备。

临时测试时，也可以直接修改当前 `/dev/ttyUSB*` 节点权限：

```bash
ls -l /dev/ttyUSB*
sudo chmod 666 /dev/ttyUSB*
```

`chmod` 方法不是持久配置。设备重新插拔、系统重启，或者设备变成新的
`/dev/ttyUSB*` 路径后，都可能需要重新执行。

## Pico4 Hand 遥操作

配合 `lerobot-teleoperator-pico4-hand`：

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

组合 robot 的 action space 包含 Franka TCP action keys 和 Revo2 手指关节 keys：

```text
tcp.x tcp.y tcp.z tcp.r1 ... tcp.r6
l_th_prox.pos l_th_mcp.pos l_idx_prox.pos l_mid_prox.pos l_ring_prox.pos l_pky_prox.pos
```

## 说明

这个组合包会关闭 Franka arm 侧的串口夹爪，改用配置里的 dexhand。
默认 dexhand 类型是 `revo2_hand`。

上真机前，建议先分别验证 arm-only 和 hand-only 两个插件。

#!/usr/bin/env python

from dataclasses import dataclass
from typing import Any

from lerobot.robots.config import RobotConfig
from lerobot_robot_franka_research3.config_franka_research3 import FrankaResearch3Config
from lerobot_robot_revo2_hand.config_revo2_hand import Revo2HandConfig


@RobotConfig.register_subclass("franka_research3_dexhand")
@dataclass
class FrankaResearch3DexhandConfig(FrankaResearch3Config):
    """Franky-backed Franka Research3 arm with a pluggable dexterous hand."""

    use_gripper: bool = False
    connect_dexhand: bool = True
    # Annotated as Any to prevent draccus from recursively expanding RobotConfig
    # subclasses in the CLI parser. At runtime this holds a RobotConfig.
    dexhand: Any = None

    dexhand_type: str = "revo2_hand"
    dexhand_id: str | None = None
    dexhand_hand_type: str = "left"
    dexhand_port_name: str | None = None
    dexhand_slave_id: int | None = None
    dexhand_baudrate: int = 460800
    dexhand_auto_detect_quick: bool = True
    dexhand_connect_timeout_s: float = 10.0
    dexhand_finger_position_duration_ms: int = 1
    dexhand_enable_tactile_sensors: bool = False

    def __post_init__(self):
        super().__post_init__()
        if self.dexhand is not None:
            return
        if self.dexhand_type != "revo2_hand":
            raise ValueError(
                "Only dexhand_type='revo2_hand' can be built from flattened CLI fields. "
                "Pass dexhand=<RobotConfig> directly for other dexterous hands."
            )
        self.dexhand = Revo2HandConfig(
            id=self.dexhand_id,
            hand_type=self.dexhand_hand_type,
            hand_id=self.dexhand_id,
            port_name=self.dexhand_port_name,
            slave_id=self.dexhand_slave_id,
            baudrate=self.dexhand_baudrate,
            auto_detect_quick=self.dexhand_auto_detect_quick,
            connect_timeout_s=self.dexhand_connect_timeout_s,
            finger_position_duration_ms=self.dexhand_finger_position_duration_ms,
            enable_tactile_sensors=self.dexhand_enable_tactile_sensors,
        )

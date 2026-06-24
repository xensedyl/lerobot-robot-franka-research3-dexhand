from lerobot.robots.config import RobotConfig
from lerobot.robots.utils import make_robot_from_config
from lerobot_robot_franka_research3 import FrankaResearch3
from lerobot_robot_revo2_hand import Revo2Hand

from lerobot_robot_franka_research3_dexhand import (
    FrankaResearch3Dexhand,
    FrankaResearch3DexhandConfig,
)


def test_franka_research3_dexhand_config_registered():
    cfg = FrankaResearch3DexhandConfig(dexhand_hand_type="left")

    assert cfg.type == "franka_research3_dexhand"
    assert RobotConfig.get_choice_class("franka_research3_dexhand") is FrankaResearch3DexhandConfig
    assert cfg.use_gripper is False
    assert cfg.dexhand is not None
    assert cfg.dexhand.type == "revo2_hand"


def test_franka_research3_dexhand_can_be_instantiated():
    robot = make_robot_from_config(FrankaResearch3DexhandConfig(dexhand_hand_type="left"))

    assert isinstance(robot, FrankaResearch3Dexhand)
    assert isinstance(robot, FrankaResearch3)
    assert isinstance(robot.dexhand, Revo2Hand)
    assert robot.name == "franka_research3_dexhand"
    assert "tcp.x" in robot.action_features
    assert "l_idx_prox.pos" in robot.action_features

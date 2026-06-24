#!/usr/bin/env python

import logging
from functools import cached_property
from typing import Any

from lerobot.robots.robot import Robot
from lerobot.robots.utils import make_robot_from_config
from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError
from lerobot_robot_franka_research3.franka_research3 import FrankaResearch3

from .config_franka_research3_dexhand import FrankaResearch3DexhandConfig


logger = logging.getLogger(__name__)


class FrankaResearch3Dexhand(FrankaResearch3):
    """Franky-backed Franka Research3 plus a pluggable dexterous hand."""

    config_class = FrankaResearch3DexhandConfig
    name = "franka_research3_dexhand"

    def __init__(self, config: FrankaResearch3DexhandConfig):
        config.use_gripper = False
        if config.dexhand is not None and config.dexhand.id is None and config.id is not None:
            config.dexhand.id = f"{config.id}_dexhand"
        super().__init__(config)
        self.config = config
        self.dexhand: Robot | None = (
            make_robot_from_config(config.dexhand) if config.dexhand else None
        )

    @cached_property
    def observation_features(self) -> dict[str, type | tuple]:
        features = dict(super().observation_features)
        if self.dexhand is not None:
            features.update(self.dexhand.observation_features)
        return features

    @cached_property
    def action_features(self) -> dict[str, type]:
        features = dict(super().action_features)
        if self.dexhand is not None:
            features.update(self.dexhand.action_features)
        return features

    @property
    def is_connected(self) -> bool:
        arm_connected = FrankaResearch3.is_connected.fget(self)
        if self.dexhand is None or not self.config.connect_dexhand:
            return arm_connected
        return arm_connected and self.dexhand.is_connected

    @property
    def is_calibrated(self) -> bool:
        arm_calibrated = FrankaResearch3.is_calibrated.fget(self)
        if self.dexhand is None or not self.config.connect_dexhand:
            return arm_calibrated
        return arm_calibrated and self.dexhand.is_calibrated

    def connect(self, calibrate: bool = True, go_to_start: bool = True) -> None:
        if self.is_connected:
            raise DeviceAlreadyConnectedError(f"{self} already connected")

        try:
            super().connect(calibrate=calibrate, go_to_start=go_to_start)
            if self.dexhand is not None and self.config.connect_dexhand:
                self.dexhand.connect()
                self.dexhand.configure()
        except Exception:
            self.disconnect(raise_if_not_connected=False)
            raise

    def configure(self) -> None:
        arm_connected = FrankaResearch3.is_connected.fget(self)
        if not arm_connected:
            raise DeviceNotConnectedError(f"{self} arm is not connected")
        FrankaResearch3.configure(self)
        if self.dexhand is not None and self.config.connect_dexhand and self.dexhand.is_connected:
            self.dexhand.configure()

    def get_observation(self) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected")

        obs = dict(super().get_observation())
        if self.dexhand is not None and self.config.connect_dexhand:
            if hasattr(self.dexhand, "get_cached_observation"):
                obs.update(self.dexhand.get_cached_observation())
            else:
                obs.update(self.dexhand.get_observation())
        return obs

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected")

        arm_keys = set(super().action_features)
        arm_action = {key: value for key, value in action.items() if key in arm_keys}
        sent_action: dict[str, Any] = {}
        if arm_action:
            sent_arm_action = FrankaResearch3.send_action(self, arm_action)
            sent_action.update(sent_arm_action if sent_arm_action is not None else arm_action)

        if self.dexhand is not None and self.config.connect_dexhand:
            dexhand_keys = set(self.dexhand.action_features)
            dexhand_action = {
                key: value for key, value in action.items() if key in dexhand_keys
            }
            if dexhand_action:
                sent_dexhand_action = self.dexhand.send_action(dexhand_action)
                sent_action.update(
                    sent_dexhand_action if sent_dexhand_action is not None else dexhand_action
                )

        return sent_action

    def disconnect(
        self,
        raise_if_not_connected: bool = True,
        keep_cameras_connected: bool = False,
    ) -> None:
        arm_connected = bool(
            getattr(self, "_is_connected", False)
            or getattr(self, "_robot_connected", False)
        )
        dex_connected = bool(
            self.dexhand is not None
            and self.config.connect_dexhand
            and self.dexhand.is_connected
        )

        if not arm_connected and not dex_connected and raise_if_not_connected:
            raise DeviceNotConnectedError(f"{self} is not connected")

        arm_error: Exception | None = None
        try:
            if arm_connected:
                FrankaResearch3.disconnect(self)
        except DeviceNotConnectedError as exc:
            if raise_if_not_connected:
                arm_error = exc
        except Exception as exc:
            arm_error = exc

        if dex_connected:
            try:
                self.dexhand.disconnect()
            except Exception as exc:
                logger.exception("Failed to disconnect dex hand")
                if arm_error is None:
                    arm_error = exc

        if arm_error is not None:
            raise arm_error

    def __repr__(self) -> str:
        dexhand_name = self.dexhand.name if self.dexhand is not None else "none"
        return (
            f"FrankaResearch3Dexhand("
            f"fci_ip={self.config.fci_ip}, "
            f"dexhand={dexhand_name}, "
            f"connected={self.is_connected})"
        )

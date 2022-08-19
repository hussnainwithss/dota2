from abc import abstractmethod
from dataclasses import dataclass, field

from dota2.clock import Clock
from dota2.mixins import Attackable, Movable, Tickable
from dota2.utils import logger


@dataclass
class TimedDebuff(Tickable):

    duration: float
    duration_left: float = field(init=False)

    def __post_init__(self) -> None:

        self.duration_left = self.duration
        self.before_start()

    @abstractmethod
    def before_start(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def before_end(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def on_tick(self) -> None:
        raise NotImplementedError()

    def tick(self, clock: Clock) -> None:

        self.duration_left -= clock.elapsed()
        if self.is_expired():
            return self.before_end()

        self.on_tick()

    def is_expired(self) -> bool:
        return self.duration_left <= 0


@dataclass
class SpiritVesselDebuff(TimedDebuff):

    target: Attackable
    _health_regen_change: float = field(init=False, default=0)

    def before_start(self) -> None:
        logger.debug(f"Applied spirit vessel on {id(self.target)} for {self.duration}s")
        self.on_tick()

    def before_end(self) -> None:
        logger.debug(f"Spirit vessel ends on {id(self.target)} after {self.duration}s")
        self.target.effective_health_regen_rate += self._health_regen_change

    def on_tick(self) -> None:

        if self._health_regen_change != self.target.health_regeneration_rate * 0.25:
            self._health_regen_change = self.target.health_regeneration_rate * 0.25
            self.target.effective_health_regen_rate -= self._health_regen_change


@dataclass
class BlighStoneDebuff(TimedDebuff):

    target: Attackable
    _armour_change: float = field(init=False, default=2)

    def before_start(self) -> None:
        logger.debug(f"Applied blight stone to {id(self.target)} for {self.duration}s")
        self.target.armour -= self._armour_change

    def before_end(self) -> None:
        logger.debug(f"Blight stone ends on {id(self.target)} after {self.duration}s")
        self.target.armour += self._armour_change

    def on_tick(self) -> None:
        pass


@dataclass
class OrbOfVenomDebuff(TimedDebuff):

    target: Movable
    _move_speed_change: float = field(init=False)

    def before_start(self) -> None:
        self._move_speed_change = self.target.movement_speed * 0.13
        self.target.movement_speed -= self._move_speed_change

    def before_end(self) -> None:
        self.target.movement_speed += self._move_speed_change

    def on_tick(self) -> None:
        pass

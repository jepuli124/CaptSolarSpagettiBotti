from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class Coordinates:
    x: int
    y: int


class CompassDirection(Enum):
    North = 0
    NorthEast = 1
    East = 2
    SouthEast = 3
    South = 4
    SouthWest = 5
    West = 6
    NorthWest = 7


class CellType(Enum):
    Empty = "O",
    OutOfVision = "X",
    AudioSignature = "?",
    HitBox = "H",
    Ship = "S",
    Projectile = "P"


@dataclass
class HitBoxData:
    entity_id: str


@dataclass
class EntityData:
    id: str
    position: Coordinates
    direction: CompassDirection


@dataclass
class ShipData(EntityData):
    health: Optional[int]
    heat: Optional[int]


@dataclass
class ProjectileData(EntityData):
    velocity: int
    mass: int


@dataclass
class Cell:
    cell_type: CellType
    data: dict | HitBoxData | ShipData | ProjectileData


@dataclass
class GameState:
    turn_number: int
    game_map: list[list[Cell]]


class ActionType(Enum):
    Move = 0,
    Turn = 1,
    Shoot = 2


@dataclass
class MoveActionData:
    distance: int


@dataclass
class TurnActionData:
    direction: CompassDirection


@dataclass
class ShootActionData:
    mass: int
    speed: int


@dataclass
class Command:
    action: str
    payload: MoveActionData | TurnActionData | ShootActionData

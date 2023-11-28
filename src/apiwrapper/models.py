from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ClientContext:
    """The persistent context of the current game.

    You can either add data to this class ad-hoc, or if you want or need static type checking you can edit this class
    to include fields for the data you want to store between ticks.

    Attributes:
        tick_length_ms (int): The length of one game tick in milliseconds
        turn_rate (int): The maximum turn rate of a ship, given in 1/8ths of a circle
    """

    def __init__(self, tick_length_ms: int, turn_rate: int):
        self.tick_length_ms = tick_length_ms
        self.turn_rate = turn_rate


@dataclass
class Coordinates:
    """A class that represents coordinates in the game map, or a vector between two coordinates

    Attributes:
        x (int): the x (horizontal) value of the coordinate or vector
        y (int): the y (vertical) value of the coordinate or vector
    """
    x: int
    y: int


class CompassDirection(Enum):
    """An enum containing compass directions"""
    North = 0
    NorthEast = 1
    East = 2
    SouthEast = 3
    South = 4
    SouthWest = 5
    West = 6
    NorthWest = 7


class CellType(Enum):
    """An enum containing all possible cell types"""
    Empty = "O",
    OutOfVision = "X",
    AudioSignature = "?",
    HitBox = "H",
    Ship = "S",
    Projectile = "P"


@dataclass
class HitBoxData:
    """Data holder for the hit box cell type

    Attributes:
        entity_id (str): The id of the entity the hit box belongs to
    """
    entity_id: str


@dataclass
class EntityData:
    """Shared data for entity cells (Ship, Projectile)

    Attributes:
        id (str): the unique id of the entity
        position (Coordinates): the map position of the entity
        direction (CompassDirection): the direction the entity is facing
    """
    id: str
    position: Coordinates
    direction: CompassDirection


@dataclass
class ShipData(EntityData):
    """Data holder for the ship cell type

    Attributes:
        health (int): the amount of health the ship has left
        heat (int): the amount of heat the ship has accrued
    """
    health: Optional[int]
    heat: Optional[int]


@dataclass
class ProjectileData(EntityData):
    """Data holder for the projectile cell type

    Attributes:
        speed (int): the speed of the projectile. How many cells the projectile moves in one tick
        mass (int): the mass of the projectile. Main part of the projectile damage

    Note:
        projectile damage on hit is calculated as speed + mass * 2
    """
    speed: int
    mass: int


@dataclass
class Cell:
    """A dataclass representing a cell in the map

    Attributes:
        cell_type (CellType): The type of the cell, see `models.CellType`
        data (dict | HitBoxData | ShipData | ProjectileData): The cell data, type depends on cell type. If cell type has
            no data this is given as an empty dict ({})
    """
    cell_type: CellType
    data: dict | HitBoxData | ShipData | ProjectileData


@dataclass
class GameState:
    """A dataclass representing the state of the game at the start of a tick

    Attributes:
        turn_number (int): the current turn number
        game_map (list[list[Cell]]): an array of arrays (matrix) of cells representing the whole map
    """
    turn_number: int
    game_map: list[list[Cell]]


class ActionType(Enum):
    """An enum containing all possible bot action types"""
    Move = 0,
    Turn = 1,
    Shoot = 2


@dataclass
class MoveActionData:
    """Data holder for the move action

    Attributes:
        distance (int): the distance to move. Validated server-side, should be between 0 and 3
    """
    distance: int


@dataclass
class TurnActionData:
    """Data holder for the turn action

    Attributes:
        direction (CompassDirection): the direction the ship should be facing after turning. Validated server-side,
            should not turn more compass directions at a time than game max turn rate
            (see `models.ClientContext.turn_rate`)
    """
    direction: CompassDirection


@dataclass
class ShootActionData:
    """Data holder for the shoot action

    Attributes:
        mass (int): the mass of the projectile that should be shot
        speed (int): the speed of the projectile that should be shot
    """
    mass: int
    speed: int


@dataclass
class Command:
    """A class representing a command sent by the bot, consisting of an action and the action data.

    Attributes:
        action (ActionType): the action type to perform
        payload (MoveActionData | TurnActionData | ShootActionData): the action data payload, should be of a type
            corresponding to the action type given
    """
    action: ActionType
    payload: MoveActionData | TurnActionData | ShootActionData

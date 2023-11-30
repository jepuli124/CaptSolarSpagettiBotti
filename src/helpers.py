import json
import math
import os
from typing import cast

from apiwrapper.models import Coordinates, CompassDirection, Cell, CellType, ProjectileData, ShipData


def get_config(config_name: str) -> str:
    """Get a config value from environment, falls back to config.json if config is not found in environment.

    Arguments:
        config_name (str): the name of the config value to get

    Returns:
        (str): the config found
    """
    config = os.getenv(config_name, None)
    if config is None:
        file_path = os.path.join(os.path.dirname(__file__), "../config.json")
        with open(file_path, "r", encoding="utf-8") as config_file:
            config = json.loads(config_file.read())[config_name]
    return str(config)


def get_coordinate_difference(origin: Coordinates, target: Coordinates) -> Coordinates:
    """Get the difference between two coordinates

    Arguments:
        origin (Coordinates): the origin (source) coordinates for the calculation
        target (Coordinates): the target coordinates for the calculation

    Returns:
        (Coordinates): a vector representing the difference from origin to target
    """
    return Coordinates(target.x - origin.x, target.y - origin.y)


def _get_vector_angle_degrees(vector: Coordinates) -> float:
    return (math.atan2(vector.y, -vector.x) * 180 / math.pi) % 360


def get_approximate_direction(vector: Coordinates) -> CompassDirection:
    """Get a compass direction most closely representing the given vector

    Arguments:
        vector (Coordinates): the vector which should be converted to approximate compass direction

    Returns:
        (CompassDirection): the compass direction closest to the vector
    """
    angle = _get_vector_angle_degrees(vector)
    cutoff = 360 / 16
    if angle >= 15 * cutoff or angle < cutoff:
        return CompassDirection.North
    elif angle < 3 * cutoff:
        return CompassDirection.NorthEast
    elif angle < 5 * cutoff:
        return CompassDirection.East
    elif angle < 7 * cutoff:
        return CompassDirection.SouthEast
    elif angle < 9 * cutoff:
        return CompassDirection.South
    elif angle < 11 * cutoff:
        return CompassDirection.SouthWest
    elif angle < 13 * cutoff:
        return CompassDirection.West
    return CompassDirection.NorthWest


def get_entity_coordinates(entity_id: str, game_map: list[list[Cell]]) -> Coordinates | None:
    """Get coordinates for a given entity from the given game map

    Arguments:
        entity_id (str): the id of the entity to search for in the map
        game_map (list[list[Cell]]): the game map to search for the entity in

    Returns:
        (Coordinates | None): the entity coordinates if the entity exists, otherwise `None`
    """
    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell.cell_type in (CellType.Ship, CellType.Projectile):
                if cast(ShipData | ProjectileData, cell.data).id == entity_id:
                    return Coordinates(x, y)
    return None


def get_partial_turn(starting_direction: CompassDirection, target_direction: CompassDirection, turn_rate: int)\
        -> CompassDirection:
    """Get the compass direction that is the furthest one you are allowed to turn towards from the given starting
    direction, given the turn rate.

    Arguments:
        starting_direction (CompassDirection): the starting direction for the turn
        target_direction (CompassDirection): the target direction for the turn
        turn_rate (int): the turn rate for the game, see `models.ClientContext.turn_rate`

    Returns:
        (CompassDirection): the furthest direction between starting and target directions allowed by the turn rate

    Note:
        If performing a 180-degree turn, the function will always perform the partial turn clockwise
    """
    initial_turn = (target_direction.value - starting_direction.value) % 8
    if initial_turn > 4:  # turning counterclockwise
        initial_turn -= 8
        return CompassDirection((starting_direction.value + max(initial_turn, -turn_rate)) % 8)
    return CompassDirection((starting_direction.value + min(initial_turn, turn_rate)) % 8)


def get_own_ship_id() -> str:
    """Get the id of your ship

    Returns:
        The id of your ship as str
    """
    return f"ship:{get_config('token')}:{get_config('bot_name')}"

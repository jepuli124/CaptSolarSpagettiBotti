import json
import math
import os

from apiwrapper.models import Coordinates, CompassDirection, Cell, CellType


def get_config(config_name: str) -> str | int:
    config = os.getenv(config_name, None)
    if config is None:
        file_path = os.path.join(os.path.dirname(__file__), "../config.json")
        with open(file_path, "r", encoding="utf-8") as config_file:
            config = json.loads(config_file.read())[config_name]
    return config


def get_coordinate_difference(origin: Coordinates, target: Coordinates) -> Coordinates:
    return Coordinates(target.x - origin.x, target.y - origin.y)


def _get_vector_angle_degrees(vector: Coordinates) -> float:
    return (math.atan2(vector.y, -vector.x) * 180 / math.pi) % 360


def get_approximate_direction(vector: Coordinates) -> CompassDirection:
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


def get_entity_coordinates(entity_id: str, game_map: list[list[Cell]]) -> Coordinates:
    # y coordinates start at the bottom
    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell.cell_type in (CellType.Ship, CellType.Projectile):
                if cell.data.id == entity_id:
                    return Coordinates(x, y)


def get_partial_turn(starting_direction: CompassDirection, target_direction: CompassDirection) -> CompassDirection:
    max_turn_radius = int(get_config("max_turn_radius"))
    initial_turn = (target_direction.value - starting_direction.value) % 8
    if initial_turn > 4:  # turning counterclockwise
        initial_turn -= 8
        return CompassDirection(starting_direction.value + max(initial_turn, -max_turn_radius))
    return CompassDirection(starting_direction.value + min(initial_turn, max_turn_radius))

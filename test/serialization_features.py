from unittest.mock import patch

import pytest

from apiwrapper.models import Cell, CellType, Coordinates, CompassDirection, Command, MoveActionData, \
    TurnActionData, ShootActionData
from apiwrapper.serialization import deserialize_map, deserialize_game_state, serialize_command


# noinspection PyMethodMayBeStatic
class SerializationFeatures:

    def should_deserialize_cell_with_no_data_based_on_type(self):
        cells = [
            [
                {"type": "empty", "data": {}},
                {"type": "outOfVision", "data": {}},
                {"type": "audioSignature", "data": {}}
            ]
        ]

        expected_empty, expected_out_of_vision, expected_audio_signature = deserialize_map(cells)[0]

        assert expected_empty.cell_type == CellType.Empty
        assert expected_out_of_vision.cell_type == CellType.OutOfVision
        assert expected_audio_signature.cell_type == CellType.AudioSignature

        assert expected_empty.data == {}
        assert expected_out_of_vision.data == {}
        assert expected_audio_signature.data == {}

    def should_set_entity_id_on_hit_box_deserialization(self):
        cells = [
            [
                {"type": "hitBox", "data": {"entityId": "myShipId"}}
            ]
        ]

        expected_hit_box = deserialize_map(cells)[0][0]

        assert expected_hit_box.cell_type == CellType.HitBox
        assert expected_hit_box.data.entity_id == "myShipId"

    def should_set_ship_data_on_ship_deserialization(self):
        cells = [
            [
                {
                    "type": "ship",
                    "data": {
                        "id": "myShipId",
                        "position": {"x": 1, "y": 2},
                        "direction": "ne",
                        "health": 10,
                        "heat": 3
                    }
                }
            ]
        ]

        expected_ship = deserialize_map(cells)[0][0]

        assert expected_ship.data.id == "myShipId"
        assert expected_ship.data.position == Coordinates(1, 2)
        assert expected_ship.data.direction == CompassDirection.NorthEast
        assert expected_ship.data.health == 10
        assert expected_ship.data.heat == 3

    def should_set_projectile_data_on_projectile_deserialization(self):
        cells = [
            [
                {
                    "type": "projectile",
                    "data": {
                        "id": "projectileId",
                        "position": {"x": 5, "y": 3},
                        "direction": "sw",
                        "velocity": 4,
                        "mass": 2
                    }
                }
            ]
        ]

        expected_projectile = deserialize_map(cells)[0][0]

        assert expected_projectile.data.id == "projectileId"
        assert expected_projectile.data.position == Coordinates(5, 3)
        assert expected_projectile.data.direction == CompassDirection.SouthWest
        assert expected_projectile.data.velocity == 4
        assert expected_projectile.data.mass == 2

    def should_deserialize_whole_matrix_at_a_time(self):
        empty_cell = {"type": "empty", "data": {}}
        empty_row = [empty_cell] * 10
        empty_matrix = [empty_row] * 10

        result_map = deserialize_map(empty_matrix)

        assert len(result_map) == 10
        assert all((len(row) == 10) for row in result_map)

    def should_deserialize_game_state_to_turn_number_and_map(self):
        game_state_dict = {
            "gameMap": [[{"type": "empty", "data": {}}]],
            "turnNumber": 82
        }

        result = deserialize_game_state(game_state_dict)

        assert result.turn_number == 82
        assert result.game_map == [[Cell(CellType.Empty, {})]]

    def should_include_distance_on_move_action_serialization(self):
        action = Command("move", MoveActionData(3))

        json = serialize_command(action)

        assert json["action"] == "move"
        assert json["payload"]["distance"] == 3

    def should_include_direction_on_turn_action_serialization(self):
        action = Command("turn", TurnActionData(CompassDirection.West))

        json = serialize_command(action)

        assert json["action"] == "turn"
        assert json["payload"]["direction"] == "w"

    def should_include_speed_and_mass_on_shoot_action_serialization(self):
        action = Command("shoot", ShootActionData(2, 5))

        json = serialize_command(action)

        assert json["action"] == "shoot"
        assert json["payload"]["mass"] == 2
        assert json["payload"]["speed"] == 5


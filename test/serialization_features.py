import pytest

from src.apiwrapper.models import Cell, CellType, Coordinates, CompassDirection
from src.apiwrapper.serialization import deserialize_map


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
                        "direction": "northEast",
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
                        "direction": "southWest",
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

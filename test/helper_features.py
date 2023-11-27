import pytest

from apiwrapper.models import Coordinates, CompassDirection, Cell, CellType, HitBoxData, ProjectileData
from helpers import get_coordinate_difference, get_approximate_direction, get_entity_coordinates, get_partial_turn


# noinspection PyMethodMayBeStatic
class GetCoordinateDifferenceFeatures:

    def should_return_zero_vector_if_origin_and_target_are_the_same(self):
        origin = Coordinates(3, -5)
        actual = get_coordinate_difference(origin, origin)
        assert actual == Coordinates(0, 0)

    def should_return_vector_pointing_from_origin_to_target_if_not_same_coordinates(self):
        origin = Coordinates(-3, 4)
        target = Coordinates(-5, -2)
        actual = get_coordinate_difference(origin, target)
        assert actual == Coordinates(-2, -6)


# noinspection PyMethodMayBeStatic
class GetApproximateDirectionFeatures:

    @pytest.mark.parametrize("x,y,expected_direction", [(-1, 0, CompassDirection.North),
                                                        (-1, 1, CompassDirection.NorthEast),
                                                        (0, 1, CompassDirection.East),
                                                        (1, 1, CompassDirection.SouthEast),
                                                        (1, 0, CompassDirection.South),
                                                        (1, -1, CompassDirection.SouthWest),
                                                        (0, -1, CompassDirection.West),
                                                        (-1, -1, CompassDirection.NorthWest)])
    def should_return_the_correct_compass_direction_for_exact_directions(self, x: int, y: int,
                                                                         expected_direction: CompassDirection):
        actual_direction = get_approximate_direction(Coordinates(x, y))
        assert actual_direction == expected_direction

    @pytest.mark.parametrize("x,y,expected_direction", [(-5, 1, CompassDirection.North),
                                                        (-5, -1, CompassDirection.North),
                                                        (-4, 5, CompassDirection.NorthEast),
                                                        (-5, 4, CompassDirection.NorthEast),
                                                        (-1, 5, CompassDirection.East),
                                                        (1, 5, CompassDirection.East),
                                                        (5, 4, CompassDirection.SouthEast),
                                                        (4, 5, CompassDirection.SouthEast),
                                                        (5, 1, CompassDirection.South),
                                                        (5, -1, CompassDirection.South),
                                                        (5, -4, CompassDirection.SouthWest),
                                                        (4, -4, CompassDirection.SouthWest),
                                                        (-1, -5, CompassDirection.West),
                                                        (1, -5, CompassDirection.West),
                                                        (-4, -5, CompassDirection.NorthWest),
                                                        (-5, -4, CompassDirection.NorthWest)])
    def should_give_closest_compass_direction_if_not_exact(self, x: int, y: int, expected_direction: CompassDirection):
        actual_direction = get_approximate_direction(Coordinates(x, y))
        assert actual_direction == expected_direction


# noinspection PyMethodMayBeStatic
class GetEntityCoordinatesFeatures:

    def should_give_entity_coordinates_for_single_cell_entity(self):
        empty = Cell(CellType.Empty, {})
        entity = Cell(CellType.Projectile,
                      ProjectileData("entity", Coordinates(1, 1), CompassDirection.NorthEast, 3, 4))
        game_map = [[empty, empty, empty, empty],
                    [empty, entity, empty, empty],
                    [empty, empty, empty, empty],
                    [empty, empty, empty, empty]]
        actual_coordinates = get_entity_coordinates("entity", game_map)
        assert actual_coordinates == entity.data.position # type: ignore

    def should_ignore_hit_box_coordinates_and_return_actual_entity(self):
        empty = Cell(CellType.Empty, {})
        hit_box = Cell(CellType.HitBox, HitBoxData("entity"))
        entity = Cell(CellType.Projectile,
                      ProjectileData("entity", Coordinates(3, 3), CompassDirection.NorthEast, 3, 4))
        game_map = [[empty, empty, empty, empty, empty],
                    [empty, empty, empty, empty, empty],
                    [empty, empty, hit_box, hit_box, hit_box],
                    [empty, empty, hit_box, entity, hit_box],
                    [empty, empty, hit_box, hit_box, hit_box]]
        actual_coordinates = get_entity_coordinates("entity", game_map)
        assert actual_coordinates == entity.data.position # type: ignore


# noinspection PyMethodMayBeStatic
class GetPartialTurnFeatures:

    def should_return_given_direction_if_turn_is_not_too_sharp(self):
        actual_direction = get_partial_turn(CompassDirection.North, CompassDirection.East, 2)
        assert actual_direction == CompassDirection.East

    def should_return_less_sharp_turn_if_turn_is_too_sharp(self):
        actual_direction = get_partial_turn(CompassDirection.North, CompassDirection.SouthEast, 2)
        assert actual_direction == CompassDirection.East

    def should_turn_clockwise_if_half_circle_turn_required(self):
        actual_direction = get_partial_turn(CompassDirection.NorthEast, CompassDirection.SouthWest, 2)
        assert actual_direction == CompassDirection.SouthEast

    def should_function_correctly_for_counterclockwise_turns(self):
        actual_direction = get_partial_turn(CompassDirection.NorthEast, CompassDirection.West, 1)
        assert actual_direction == CompassDirection.North

from apiwrapper.models import Cell, CellType, HitBoxData, ShipData, Coordinates, CompassDirection, ProjectileData, \
    GameState, Command, MoveActionData, TurnActionData, ShootActionData, ActionType

_CELL_TYPE_MAPPING = {
    "empty": CellType.Empty,
    "outOfVision": CellType.OutOfVision,
    "audioSignature": CellType.AudioSignature,
    "hitBox": CellType.HitBox,
    "ship": CellType.Ship,
    "projectile": CellType.Projectile
}

_COMPASS_DESERIALIZATION_MAPPING = {
    "n": CompassDirection.North,
    "ne": CompassDirection.NorthEast,
    "e": CompassDirection.East,
    "se": CompassDirection.SouthEast,
    "s": CompassDirection.South,
    "sw": CompassDirection.SouthWest,
    "w": CompassDirection.West,
    "nw": CompassDirection.NorthWest
}

_COMPASS_SERIALIZATION_MAPPING = {
    CompassDirection.North: "n",
    CompassDirection.NorthEast: "ne",
    CompassDirection.East: "e",
    CompassDirection.SouthEast: "se",
    CompassDirection.South: "s",
    CompassDirection.SouthWest: "sw",
    CompassDirection.West: "w",
    CompassDirection.NorthWest: "nw"
}


def _deserialize_no_data(_: dict) -> dict:
    return {}


def _deserialize_hit_box(hit_box_data: dict) -> HitBoxData:
    return HitBoxData(hit_box_data["entityId"])


def _deserialize_ship(ship_data: dict) -> ShipData:
    return ShipData(ship_data["id"], Coordinates(ship_data["position"]["x"], ship_data["position"]["y"]),
                    _COMPASS_DESERIALIZATION_MAPPING[ship_data["direction"]], ship_data["health"], ship_data["heat"])


def _deserialize_projectile(projectile_data: dict) -> ProjectileData:
    projectile_coordinates = Coordinates(projectile_data["position"]["x"], projectile_data["position"]["y"])
    return ProjectileData(projectile_data["id"], projectile_coordinates,
                          _COMPASS_DESERIALIZATION_MAPPING[projectile_data["direction"]], projectile_data["velocity"],
                          projectile_data["mass"])


_CELL_DESERIALIZATION_MAPPING = {
    "empty": _deserialize_no_data,
    "outOfVision": _deserialize_no_data,
    "audioSignature": _deserialize_no_data,
    "hitBox": _deserialize_hit_box,
    "ship": _deserialize_ship,
    "projectile": _deserialize_projectile
}


def deserialize_map(map_matrix: list[list[dict]]) -> list[list[Cell]]:
    return [_deserialize_row(row) for row in map_matrix]


def _deserialize_row(row: list[dict]) -> list[Cell]:
    return [_deserialize_cell(cell) for cell in row]


def _deserialize_cell(cell: dict) -> Cell:
    cell_type = cell["type"]
    return Cell(_CELL_TYPE_MAPPING[cell_type], _CELL_DESERIALIZATION_MAPPING[cell_type](cell["data"]))


def deserialize_game_state(game_state: dict) -> GameState:
    return GameState(game_state["turnNumber"], deserialize_map(game_state["gameMap"]))


def _serialize_move_action(action_data: MoveActionData) -> dict:
    return {"distance": action_data.distance}


def _serialize_turn_action(action_data: TurnActionData) -> dict:
    return {"direction": _COMPASS_SERIALIZATION_MAPPING[action_data.direction]}


def _serialize_shoot_action(action_data: ShootActionData) -> dict:
    return {"mass": action_data.mass, "speed": action_data.speed}


_ACTION_SERIALIZATION_MAPPING = {
    ActionType.Move: _serialize_move_action,
    ActionType.Turn: _serialize_turn_action,
    ActionType.Shoot: _serialize_shoot_action
}

_ACTION_TYPE_MAPPING = {
    ActionType.Move: "move",
    ActionType.Turn: "turn",
    ActionType.Shoot: "shoot"
}


def serialize_command(command: Command) -> dict:
    return {"action": _ACTION_TYPE_MAPPING[command.action],
            "payload": _ACTION_SERIALIZATION_MAPPING[command.action](command.payload)}

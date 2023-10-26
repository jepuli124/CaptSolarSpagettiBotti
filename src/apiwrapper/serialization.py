from src.apiwrapper.models import Cell, CellType, HitBoxData, ShipData, Coordinates, CompassDirection, ProjectileData

_CELL_TYPE_MAPPING = {
    "empty": CellType.Empty,
    "outOfVision": CellType.OutOfVision,
    "audioSignature": CellType.AudioSignature,
    "hitBox": CellType.HitBox,
    "ship": CellType.Ship,
    "projectile": CellType.Projectile
}

_COMPASS_DIRECTION_MAPPING = {
    "north": CompassDirection.North,
    "northEast": CompassDirection.NorthEast,
    "east": CompassDirection.East,
    "southEast": CompassDirection.SouthEast,
    "south": CompassDirection.South,
    "southWest": CompassDirection.SouthWest,
    "west": CompassDirection.West,
    "northWest": CompassDirection.NorthWest
}


def _deserialize_no_data(cell: dict) -> dict:
    return {}


def _deserialize_hit_box(hit_box_data: dict) -> HitBoxData:
    return HitBoxData(hit_box_data["entityId"])


def _deserialize_ship(ship_data: dict) -> ShipData:
    return ShipData(ship_data["id"], Coordinates(ship_data["position"]["x"], ship_data["position"]["y"]),
                    _COMPASS_DIRECTION_MAPPING[ship_data["direction"]], ship_data["health"], ship_data["heat"])


def _deserialize_projectile(projectile_data: dict) -> ProjectileData:
    projectile_coordinates = Coordinates(projectile_data["position"]["x"], projectile_data["position"]["y"])
    return ProjectileData(projectile_data["id"], projectile_coordinates,
                          _COMPASS_DIRECTION_MAPPING[projectile_data["direction"]], projectile_data["velocity"],
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

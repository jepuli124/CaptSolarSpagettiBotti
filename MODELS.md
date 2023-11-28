# ClientContext

The `ClientContext` object is available in the tick processing function as the `context`
argument. It is reset at the start of a game and can be used to store persistent data
between ticks. It also contains data about the game sent by the server at game start.
This data is the tick length of the game in milliseconds and the maximum turn rate for
the game, in 1/8ths of a circle, or compass direction steps.

If you want to use type checking and/or autocomplete with the data you store in the client
context, you can edit the class in `src/apiwrapper/models.py` to add the fields you need.
The basic client context class is as follows:

```python
class ClientContext:
    tick_length_ms: int
    turn_rate: int
```

# GameState

The `GameState` object houses two fields. `turnNumber` and `gameMap`. Please note that
in the python code, these fields are accessed via pythonic snake_case names.

 - `turnNumber` or `turn_number` is a rolling integer denoting the current turn,
starting from 1.
 - `gameMap` is a matrix (array of arrays) of `Cell` objects. See [Cells](#cells) for
further reference

```python
class GameState:
    turn_number: int
    game_map: list[list[Cell]]
```

## Cells

Each cell houses a `Cell` object, with fields `cellType` and `data`. Cell type denotes
the cell type and data houses the unique data for each cell type. 

```python
class Cell:
    cell_type: CellType
    data: dict | HitBoxData | ShipData | ProjectileData
```

Possible cell types and their data models are:

### Empty
Empty cell, only space here. Data is an empty dict (`{}`)

### OutOfVision
Cell outside your vision range. Data is an empty dict (`{}`)


### AudioSignature
If an enemy ship is outside your vision range, an out of vision cell at the edge of your
vision is converted into an audio signature cell on the line from your ship towards
the ship that is out of vision. Data is an empty dict (`{}`)

### HitBox
Entities (ships and projectiles) are not always exactly the size of one cell. In these
cases the middle cell of the entity houses the entity data, while the rest are hit box
cells with a reference to the main entity by entity id.
```python
class HitBoxData:
    entity_id: str
```

### Ship
A cell with a ship entity

See [CompassDirection](#compassdirection) for possible compass direction values.
```python
class ShipData:
    id: str
    position: CompassDirection
    position: Coordinates
    health: int
    heat: int
```

### Projectile
A cell with a projectile entity

See [CompassDirection](#compassdirection) for possible compass direction values.
```python
class ProjectileData:
    id: str
    position: CompassDirection
    position: Coordinates
    velocity: int
    mass: int
```

# Command

The bot sends command models as a response to server game tick events. Each command
model has an `actionType` field and a `payload` field containing action type specific
data.

```python
class ActionType(Enum):
    Move = 0,
    Shoot = 1,
    Turn = 2

class Command:
    action_type: ActionType
    payload: MoveActionData | ShootActionData | TurnActionData
```

The models are as follows:

### Move

Move straight ahead 0 to 3 cells. Dissipates `distance * 2` heat

```python
class MoveActionData:
    distance: int
```

### Turn

Turn to a compass direction. Cannot be compass direction at a time than the game max
turn radius. Validated server-side

```python
class TurnActionData:
    direction: CompassDirection
```

### Shoot

Shoot a projectile. Generates `mass * velocity` heat, moves at `velocity` speed and
does `mass * 2 + velocity` damage on impact. Heat exceeding `25` will be converted to
damage on your ship in a ratio of `1:1`


```python
class ShootActionData:
    mass: int
    velocity: int
```

# CompassDirection
Enum holding compass direction values
```python
class CompassDirection(Enum):
    North = "n",
    NorthEast = "ne",
    East = "e",
    SouthEast = "se",
    South = "s",
    SouthWest = "sw",
    West = "w",
    NorthWest = "nw"
```
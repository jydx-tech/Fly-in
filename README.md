*This project has been created as part of the 42 curriculum by jdenaux.*

# Fly-in

## Description

Fly-in routes a fleet of drones from a start zone to an end zone through a
network of connected zones, in the fewest possible simulation turns.

The network is read from a map file. Zones have a type (`normal`, `priority`,
`restricted`, `blocked`), an optional color and a capacity (`max_drones`).
Connections are bidirectional and have a capacity (`max_link_capacity`).
All drones start in the start zone and must reach the end zone while
respecting every capacity rule.

Overview of the program:

1. **Parser**: reads and validates the map file (clear error with line number).
2. **Network**: custom graph (no graph library) built from the file.
3. **Planner**: finds a conflict-free schedule for every drone.
4. **Simulation**: replays the schedules turn by turn and produces the output.
5. **Display**: colored terminal output and a tkinter graphical window.

Constraints respected: Python 3.10+, `flake8` and `mypy` clean, fully
object-oriented, type hints and docstrings everywhere, no graph library
(only `heapq` from the standard library).

## Instructions

Requirements: Python 3.10 or later, `tkinter` (for the graphical window).

```bash
make install        # install the dependencies (flake8, mypy)
make run MAP=maps/easy/02_simple_fork.txt
make debug MAP=maps/easy/02_simple_fork.txt   # run under pdb
make lint           # flake8 + mypy with the flags of the subject
make lint-strict    # flake8 + mypy --strict
make clean          # remove __pycache__ and .mypy_cache
```

Or directly:

```bash
python3 main.py <map_file>
```

Behavior:

- the colored network (zones and connections) is printed first;
- then one line per turn is printed (the official output);
- then a graphical window opens.

Window controls (click the window first to give it the focus):

| Key | Action |
|---|---|
| Right arrow | next turn |
| Left arrow | previous turn |
| Space | start / stop automatic playback |
| `s` | print the colored state of the current turn in the terminal |

Errors (invalid map, unsolvable map, missing file) are printed on `stderr`
as `Error: <message>` with a non-zero exit code, never as a Python traceback.

## Map format

```
nb_drones: 2
start_hub: s 0 0 [color=green]
hub: r 1 0 [zone=restricted color=red]
end_hub: e 2 0 [color=yellow]
connection: s-r
connection: r-e [max_link_capacity=2]
```

- `nb_drones: <positive integer>` on the first useful line.
- `start_hub:`, `end_hub:` (exactly one each) and `hub:` followed by
  `<name> <x> <y> [metadata]`. Names contain no dash and no space.
- Zone metadata: `zone=<normal|blocked|restricted|priority>` (default
  `normal`), `color=<word>` (default none), `max_drones=<n>` (default 1,
  ignored on start and end).
- `connection: <zone1>-<zone2> [max_link_capacity=<n>]` (default 1).
  `a-b` and `b-a` are the same connection.
- Lines starting with `#` and blank lines are ignored.

## Example

Map (`restricted.txt`):

```
nb_drones: 2
start_hub: s 0 0
hub: r 1 0 [zone=restricted]
end_hub: e 2 0
connection: s-r
connection: r-e
```

Output:

```
D1-s-r
D1-r D2-s-r
D1-e D2-r
D2-e
```

- Turn 1: D1 leaves `s` toward the restricted zone `r`; it is on the
  connection `s-r` (a restricted zone costs 2 turns).
- Turn 2: D1 arrives in `r`; the connection is free again so D2 can start
  crossing it in the same turn.
- Turn 3: D1 reaches `e`, D2 arrives in `r`.
- Turn 4: D2 reaches `e`. 4 turns in total.

Drones that do not move during a turn are omitted from the line, and
delivered drones are no longer shown.

## Algorithm explanation

### Choice: time-expanded search with reservations

A plain shortest path is not enough: drones block each other, so the
question is not only *where* to go but also *when*. The program plans the
drones one after the other, and each drone searches the best route taking
into account what the previous drones have already reserved.

**State.** A state is a pair `(zone, turn)`: "the drone is in this zone at
the end of this turn". Waiting is a move like any other:
`(zone, t) -> (zone, t + 1)`.

**Reservations.** A `Reservations` object keeps two counters indexed by
`(turn, name)`:

- how many drones are in a zone at the end of a turn (limit: zone capacity);
- how many drones cross a connection during a turn (limit:
  `max_link_capacity`).

**Search (`PathFinder.timed_path`).** A Dijkstra over `(zone, turn)` states
using `heapq`. From `(zone, t)` the drone can:

| Move | Conditions | New state |
|---|---|---|
| wait | zone free at `t + 1` | `(zone, t + 1)` |
| go to a normal / priority zone | link free at `t + 1`, zone free at `t + 1` | `(next, t + 1)` |
| go to a restricted zone | link free at `t + 1`, zone free at `t + 2` | `(next, t + 2)` |

For a restricted zone the drone occupies the connection during turn `t + 1`
(it is in no zone) and *must* arrive at `t + 2`, so the capacity of the
destination is tested at `t + 2`. Blocked zones are never returned as
neighbors. Start and end have an unlimited capacity, so they need no special
case.

Because the queue is ordered by turn, the first time the end zone is popped
is the earliest possible arrival for this drone.

**Tie-break.** Several routes can arrive at the same turn. The heap element
is `(turn, penalty, name)`: at equal turn, the smaller penalty wins. Each
move to a non-priority zone costs 1, a move to a priority zone costs 0.
This removes useless detours and prefers priority zones, without ever
making a route slower.

**Planning all the drones (`Simulation`).** For each drone, in order: search
its route, then reserve its zones and links (`PathFinder.reserve_path`).
The next drone sees these reservations. The result is a schedule per drone,
then turned into the output lines.

**Horizon.** The search is bounded by `2 * nb_drones + 2 * nb_zones + 10`
turns (a drone waits at worst for all the previous ones, and each zone costs
at most 2 turns). An unreachable end zone is detected beforehand with a plain
Dijkstra (`shortest_path`) and reported with `UnsolvableError`.

### Complexity

For one drone the search visits at most `Z * T` states (`Z` zones, `T` the
horizon), each with a heap operation: `O(Z * T * log(Z * T))` plus the
neighbors of each state. For `D` drones the total is about `D` times that.
500 drones on a simple map run in about half a second.

### Trade-offs and limits

- Planning drone by drone is a greedy strategy: the first drones get the
  best routes. It reaches the optimum on all the maps of the subject, but it
  is not proven optimal on every possible map.
- Paths are not cached: each drone has its own search, because the
  reservations change after each drone.
- Memory: the reservation counters grow with the number of reserved
  `(turn, name)` pairs, i.e. proportionally to the length of the schedules.

### Results on the maps of the subject

| Map | Optimum | Result |
|---|---|---|
| linear path | 4 | 4 |
| simple fork | 4 | 4 |
| basic capacity | 4 | 4 |
| dead end trap | 8 | 8 |
| circular loop | 10 | 10 |
| priority puzzle | 6 | 6 |
| maze nightmare | 13 | 13 |
| capacity hell | 16 | 16 |
| ultimate challenge | 26 | 26 |

## Visual representation

Two complementary displays are provided.

**Colored terminal output.** `Display` prints the zones (name colored with
the `color` of the zone, role, type, capacity) and the connections (each end
colored, capacity). Unknown colors are printed without color instead of
failing. Pressing `s` in the window prints, for the current turn, where each
drone is (`at <zone>` or `flying <zone> -> <zone>`) and the occupancy
`count/capacity` of every zone.

**Graphical window (tkinter).**

- every zone is a circle filled with its `color` (start and end are bigger),
  with its name written above;
- connections are gray arrows, thicker when `max_link_capacity` is larger;
- drones are gray diamonds labeled `D1`, `D2`...; a drone flying toward a
  restricted zone is drawn in the middle of the connection;
- the turn counter `Turn n / last` is displayed in the corner;
- navigation turn by turn (arrows) and automatic playback (space).

These features make the simulation easy to follow: bottlenecks, waiting
drones and the two-turn flight toward restricted zones are visible
immediately, and the colors of the map are the ones of the file.

## Resources

- Python documentation: `heapq`, `enum`, `typing`, `tkinter`.
- Math-cours.fr
- PEP 8, PEP 257 (docstrings), `flake8` and `mypy` documentation.
- Dijkstra's algorithm; time-expanded graphs and reservation tables
  (cooperative pathfinding / space-time A*).
- Subject of the project (`subject.pdf`).

**Use of AI.** An AI assistant was used to explain concepts (time-expanded search, tkinter events), to review code, and to suggest test maps and edge cases. The code was
written, by me.

## Project structure

```
main.py              entry point
Makefile
fly_in/
    errors.py        FlyInError, ParseError, UnsolvableError
    models.py        ZoneType, ZoneRole, Zone, Connection, Drone
    network.py       Network (the graph)
    parser.py        MapParser
    reservations.py  Reservations
    pathfinding.py   PathFinder
    simulation.py    Simulation
    display.py       Display (colored terminal)
    gui.py           Projection, GraphicalDisplay (tkinter)
maps/                maps of the subject and test maps
```

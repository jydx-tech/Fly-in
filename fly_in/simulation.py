# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulation.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/29 15:08:24 by jdenaux         #+#    #+#               #
#  Updated: 2026/11/03 13:05:05 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #


"""Turn by Turn simulation"""

from fly_in.models import Drone, Zone
from fly_in.pathfinding import PathFinder
from fly_in.reservations import Reservations
from fly_in.network import Network


class Simulation:
    """Plan every drone in advance, then replay the turns."""

    def __init__(self, network: Network, nb_drones: int) -> None:
        self._network = network
        self._drones = [Drone(i, network.start)
                        for i in range(1, nb_drones + 1)]
        self._turn = 0
        finder = PathFinder(network)
        reservations = Reservations()
        horizon = 2 * nb_drones + 2 * len(network.zones) + 10
        for drone in self._drones:
            drone.schedule = finder.timed_path(reservations, horizon)
            finder.reserve_path(reservations, drone.schedule)
            self._fill_moves(drone)

    @property
    def drones(self) -> list[Drone]:
        """Return the drones."""
        return list(self._drones)

    @property
    def last_turn(self) -> int:
        """Return the turn at which the last drone arrives."""
        return max(d.schedule[-1][1] for d in self._drones)

    def _fill_moves(self, drone: Drone) -> None:
        """Save the outpout to display for each turn."""
        pairs = zip(drone.schedule, drone.schedule[1:])
        for (zone_a, t_a), (zone_b, t_b) in pairs:
            if zone_a is zone_b:
                continue
            if t_a + 2 == t_b:
                link = self._network.connection_between(zone_a, zone_b)
                drone.moves_by_turn[t_a + 1] = f"{drone.name}-{link.name}"
            drone.moves_by_turn[t_b] = f"{drone.name}-{zone_b.name}"

    def is_finished(self) -> bool:
        """Return True when every drone has reached its last state."""
        return all(self._turn >= d.schedule[-1][1] for d in self._drones)

    def play_turn(self) -> list[str]:
        """Return the movements of the next turn."""
        self._turn += 1
        moves: list[str] = []
        for drone in self._drones:
            if self._turn in drone.moves_by_turn:
                moves.append(drone.moves_by_turn[self._turn])
        return moves

    def position_at(self, drone: Drone, turn: int) -> tuple[Zone, Zone | None]:
        """Return position of the drone at the and of the given turn.

        Returns:
            (zone, None) if the drone is in a zone,
            (origin, destination) if it is in flight between two zones.
        """
        pairs = zip(drone.schedule, drone.schedule[1:])
        for (zone_a, t_a), (zone_b, t_b) in pairs:
            if turn == t_a:
                return (zone_a, None)
            if t_a < turn < t_b:
                return (zone_a, zone_b)
        return (drone.schedule[-1][0], None)

    def occupancy_at(self, zone: Zone, turn: int) -> int:
        """Return how many drones are in the zone at the end of the turn."""
        count = 0
        for drone in self._drones:
            where, destination = self.position_at(drone, turn)
            if where is zone and destination is None:
                count += 1
        return count

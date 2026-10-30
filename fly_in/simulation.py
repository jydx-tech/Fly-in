# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulation.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/29 15:08:24 by jdenaux         #+#    #+#               #
#  Updated: 2026/10/30 13:34:37 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #


"""Turn by Turn simulation"""

from fly_in.models import Drone, DroneState
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
        for drone in self._drones:
            drone.schedule = finder.timed_path(reservations)
            finder.reserve_path(reservations, drone.schedule)

    def is_finished(self) -> bool:
        """Return True when every drone has reached its last state."""
        return all(self._turn >= len(d.schedule) - 1 for d in self._drones)

    def play_turn(self) -> list[str]:
        """Return the movements of the next turn."""
        self._turn += 1
        moves: list[str] = []
        for drone in self._drones:
            if self._turn < len(drone.schedule):
                before = drone.schedule[self._turn - 1][0]
                after = drone.schedule[self._turn][0]
                if before is not after:
                    moves.append(f"{drone.name}-{after.name}")
        return moves

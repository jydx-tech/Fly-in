# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  pathfinding.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/29 13:32:06 by jdenaux         #+#    #+#               #
#  Updated: 2026/11/04 12:16:01 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Shortest path search in a network."""

import heapq

from fly_in.network import Network
from fly_in.errors import UnsolvableError
from fly_in.models import Zone, ZoneType
from fly_in.reservations import Reservations


class PathFinder:
    """Find shortest path."""

    def __init__(self, network: Network) -> None:
        """Store the network to search in.

        Args:
            network: The network of zones.
        """
        self._network = network

    def timed_path(
            self, reservations: Reservations, horizon: int
    ) -> list[tuple[Zone, int]]:
        """Return the fasted path start to end.

        The result lists (zone, turn) states, from (start, 0) to the
        arrival at the end zone.

        Raises:
            UnsolvableError: If the end is not reached before the horizon.
        """
        start = self._network.start
        end = self._network.end
        heap: list[tuple[int, int, str]] = [(0, 0, start.name)]
        visited: set[tuple[str, int]] = set()
        parent: dict[tuple[str, int], tuple[str, int]] = {}
        best: dict[tuple[str, int], int] = {(start.name, 0): 0}
        while heap:
            turn, penality, name = heapq.heappop(heap)
            if (name, turn) in visited:
                continue
            visited.add((name, turn))
            if name == end.name:
                states = [(end.name, turn)]
                while states[-1] != (start.name, 0):
                    states.append(parent[states[-1]])
                states.reverse()
                return [(self._network.get_zone(n), t) for n, t in states]
            if turn >= horizon:
                continue
            zone = self._network.get_zone(name)
            state = (name, turn + 1)
            if (reservations.zone_is_free(zone, turn + 1)
                    and (state not in best or penality < best[state])):
                best[state] = penality
                parent[state] = (name, turn)
                heapq.heappush(heap, (turn + 1, penality, name))
            for nxt in self._network.neighbors(zone):
                arrival = turn + nxt.zone_type.cost
                link = self._network.connection_between(zone, nxt)
                if nxt.zone_type is ZoneType.PRIORITY:
                    new_penality = penality
                else:
                    new_penality = penality + 1
                state = (nxt.name, arrival)
                if (reservations.link_is_free(link, turn + 1)
                        and reservations.zone_is_free(nxt, arrival)
                        and (state not in best or new_penality < best[state])):
                    best[state] = new_penality
                    parent[state] = (name, turn)
                    heapq.heappush(heap, (arrival, new_penality, nxt.name))
        raise UnsolvableError("no path from start to end")

    def reserve_path(
            self, reservations: Reservations,
            path: list[tuple[Zone, int]]) -> None:
        """Reserve the zones and links used by a timed path."""
        for (zone_a, t_a), (zone_b, t_b) in zip(path, path[1:]):
            reservations.reserve_zone(zone_b, t_b)
            if zone_a is not zone_b:
                link = self._network.connection_between(zone_a, zone_b)
                reservations.reserve_link(link, t_a + 1)

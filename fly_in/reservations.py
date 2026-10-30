# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  reservation.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/30 11:09:21 by jdenaux         #+#    #+#               #
#  Updated: 2026/10/30 11:30:30 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Reservations of zones and connections in the time"""

from fly_in.models import Zone, Connection


class Reservations:
    """Save places in zone in link for each turn."""

    def __init__(self) -> None:
        """Create empty reservation."""
        self._zones: dict[tuple[int, str], int] = {}
        self._links: dict[tuple[int, str], int] = {}

    def zone_is_free(self, zone: Zone, turn: int) -> bool:
        """Return true if there is still place this turn."""
        return self._zones.get((turn, zone.name), 0) < zone.capacity

    def link_is_free(self, link: Connection, turn: int) -> bool:
        """Return True if one more drone can cross the link this turn."""
        return self._links.get((turn, link.name), 0) < link.max_link_capacity

    def reserve_zone(self, zone: Zone, turn: int) -> None:
        """Add one drone in this zone for this turn."""
        self._zones[turn, zone.name] = self._zones.get(
            (turn, zone.name), 0) + 1

    def reserve_link(self, link: Connection, turn: int) -> None:
        """Add one drone crossing the link this turn."""
        self._links[turn, link.name] = self._links.get(
            (turn, link.name), 0) + 1

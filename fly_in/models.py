# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  models.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/26 10:34:38 by jdenaux         #+#    #+#               #
#  Updated: 2026/11/04 15:42:17 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Data models"""

from enum import Enum


UNLIMITED = 10**9
"""Capacity used for zones without limit (start and end)."""


class ZoneType(Enum):
    """Type of zone, determine cost of move."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def cost(self) -> int:
        """Number of turns to enter in this zone type."""
        if self is ZoneType.NORMAL or self is ZoneType.PRIORITY:
            return 1
        if self is ZoneType.RESTRICTED:
            return 2
        raise ValueError("a blocked zone cannot be entered")


class ZoneRole(Enum):
    """Role of a zone: start, end or regular."""

    START = "start"
    END = "end"
    REGULAR = "regular"


class Zone:
    """Zone of the network."""

    def __init__(self, name: str, x: int, y: int,
                 zone_type: ZoneType = ZoneType.NORMAL,
                 color: str | None = None,
                 max_drones: int = 1,
                 role: ZoneRole = ZoneRole.REGULAR) -> None:
        """Store the zone information.

        Parameters
        ----------
        name : str
            zone name
        x : int
            zone abscissa
        y : int
            zone ordinate
        zone_type : ZoneType, optional
            Type of zone, determine cost of move., by default ZoneType.NORMAL
        color : str | None, optional
            zone color, by default None
        max_drones : int, optional
            maximum number drones in this zone, by default 1
        role : ZoneRole, optional
            describes zone role, by default ZoneRole.REGULAR
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.role = role

    @property
    def capacity(self) -> int:
        """Maximum number of drones in this zone."""
        if self.role is ZoneRole.START or self.role is ZoneRole.END:
            return UNLIMITED
        return self.max_drones


class Connection:
    """Link between two zones."""

    def __init__(self, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int = 1) -> None:
        """Store the connection information.

        Parameters
        ----------
        zone_a : Zone
            First end of the connection.
        zone_b : Zone
            Second end of the connection.
        max_link_capacity : int, optional
            Maximum drones crossing at once, by default 1.
        """
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    @property
    def name(self) -> str:
        """Name of the connection, as used in the simulation output."""
        return f"{self.zone_a.name}-{self.zone_b.name}"

    def other(self, zone: Zone) -> Zone:
        """Return the end of the connection opposite to the given zone."""
        if zone is self.zone_a:
            return self.zone_b
        if zone is self.zone_b:
            return self.zone_a
        raise ValueError("No zone at the end of this connection")


class Drone:
    """Drone"""

    def __init__(self, drone_id: int, start: Zone) -> None:
        """Create a drone waiting in the start zone.

        Args:
            drone_id: Number of the drone (1 for D1).
            start: Zone where the drone begins.
        """
        self.id = drone_id
        self.step = 0
        self.schedule: list[tuple[Zone, int]] = []
        self.moves_by_turn: dict[int, str] = {}

    @property
    def name(self) -> str:
        """Name used in the simulation output, e.g. "D1"."""
        return "D" + str(self.id)

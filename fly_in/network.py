# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  network.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/27 11:45:24 by jdenaux         #+#    #+#               #
#  Updated: 2026/10/30 09:43:42 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Graph of zones and connections."""

from fly_in.models import Connection, Zone, ZoneType, ZoneRole


class Network:
    """Graph of zones linked by connections."""

    def __init__(self) -> None:
        """Create empty network."""
        self._zones: dict[str, Zone] = {}
        self._connections: list[Connection] = []
        self._links: dict[str, list[Connection]] = {}
        self._link_keys: set[frozenset[str]] = set()

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the network.

        Raises:
            ValueError: if a double name
        """
        if zone.name in self._zones:
            raise ValueError(f"duplicate zone name: {zone.name}")
        self._zones[zone.name] = zone
        self._links[zone.name] = []

    def get_zone(self, name: str) -> Zone:
        """Return the zone with the given name.

        Raises:
            ValueError: if no zone have this name.
        """
        if name in self._zones:
            return self._zones[name]
        raise ValueError(f"unknown zone: {name}")

    def add_connection(self, connection: Connection) -> None:
        """Add a connection to the network.

        Raises:
            ValueError: if end is unknow or allready exist
        """
        if connection.zone_a.name not in self._zones:
            raise ValueError(f"Connection {connection.name}"
                             f" has no end {connection.zone_a.name}")
        if connection.zone_b.name not in self._zones:
            raise ValueError(f"Connection {connection.name}"
                             f" has no end {connection.zone_b.name}")
        key = frozenset({connection.zone_a.name, connection.zone_b.name})
        if key in self._link_keys:
            raise ValueError(f"Connection {connection.name} allready exist")
        self._link_keys.add(key)
        self._connections.append(connection)
        self._links[connection.zone_a.name].append(connection)
        self._links[connection.zone_b.name].append(connection)

    def connections_of(self, zone: Zone) -> list[Connection]:
        """Return the connections for a zone."""
        return self._links[zone.name]

    def neighbors(self, zone: Zone) -> list[Zone]:
        """Return neighbors zone except blocked one."""
        reachable: list[Zone] = []
        connections = self.connections_of(zone)
        for connection in connections:
            opposite = connection.other(zone)
            if opposite.zone_type is not ZoneType.BLOCKED:
                reachable.append(opposite)
        return reachable

    def connection_between(self, zone_a: Zone, zone_b: Zone) -> Connection:
        """Return the connection linking two zones.

        Raises:
            ValueError: If the zones are not directly connected.
        """
        for connect in self.connections_of(zone_a):
            if connect.other(zone_a) is zone_b:
                return connect
        raise ValueError(
            f"no connection between {zone_a.name} and {zone_b.name}")

    @property
    def start(self) -> Zone:
        """Return the start zone."""
        for zone in self._zones.values():
            if zone.role is ZoneRole.START:
                return zone
        raise ValueError("No start Zone")

    @property
    def end(self) -> Zone:
        """Return the end zone."""
        for zone in self._zones.values():
            if zone.role is ZoneRole.END:
                return zone
        raise ValueError("No end Zone")

    @property
    def zones(self) -> list[Zone]:
        """Return all zones."""
        return list(self._zones.values())

    @property
    def connections(self) -> list[Connection]:
        """Return all the connections of the network."""
        return list(self._connections)

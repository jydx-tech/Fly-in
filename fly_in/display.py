# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  display.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/29 08:42:50 by jdenaux         #+#    #+#               #
#  Updated: 2026/11/05 08:52:56 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Colored display in the terminal."""

from fly_in.network import Network
from fly_in.models import UNLIMITED
from fly_in.simulation import Simulation

RESET = "\033[0m"

COLORS: dict[str, str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "gray": "\033[90m",
    "orange": "\033[38;5;208m",
    "purple": "\033[38;5;129m",
    "brown": "\033[38;5;130m",
    "lime": "\033[38;5;118m",
    "gold": "\033[38;5;220m",
    "black": "\033[30m",
    "maroon": "\033[38;5;88m",
    "darkred": "\033[38;5;52m",
    "violet": "\033[38;5;135m",
    "crimson": "\033[38;5;161m",
    "rainbow": "\033[38;5;201m",
}


class Display:
    """Show network and simulation in the terminal."""

    def colorize(self, text: str, color: str | None) -> str:
        """Return text wrapped in the ANSI code of the color."""
        if not color or color not in COLORS:
            return text
        return f"{COLORS[color]}{text}{RESET}"

    def show_zones(self, network: Network) -> None:
        """Print every zone with type, capacity, role."""
        for zone in network.zones:
            name = self.colorize(f"{zone.name:<12}", zone.color)
            if zone.capacity == UNLIMITED:
                capacity = "unlimited"
            else:
                capacity = str(zone.capacity)
            print(f"{name} {zone.role.value:<8} "
                  f"{zone.zone_type.value:<11} capacity: {capacity}")

    def show_connections(self, network: Network) -> None:
        """Print every connection with its capacity."""
        for connection in network.connections:
            name_a = self.colorize(
                connection.zone_a.name, connection.zone_a.color)
            name_b = self.colorize(
                connection.zone_b.name, connection.zone_b.color)
            names = f"{name_a}-{name_b}"
            padding = " " * (12 - len(connection.name))
            print(f"{names}{padding} capacity: {connection.max_link_capacity}")

    def show_turn(self, network: Network, simulation: Simulation,
                  turn: int) -> None:
        """Print the drone movements and the zone occupancy of a turn."""
        print(f"Turn {turn}")
        for drone in simulation.drones:
            zone, destination = simulation.position_at(drone, turn)
            if destination is None:
                print(f"  {drone.name} at "
                      f"{self.colorize(zone.name, zone.color)}")
            else:
                origin = self.colorize(zone.name, zone.color)
                target = self.colorize(destination.name, destination.color)
                print(f"  {drone.name} flying {origin} -> {target}")
        parts: list[str] = []
        for zone in network.zones:
            count = simulation.occupancy_at(zone, turn)
            cap = "unlimited" if zone.capacity == UNLIMITED else str(
                zone.capacity)
            parts.append(
                f"{self.colorize(zone.name, zone.color)}[{count}/{cap}]")
        print("Zones: " + "  ".join(parts))

# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  gui.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/29 10:23:55 by jdenaux         #+#    #+#               #
#  Updated: 2026/10/29 12:58:36 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Graphical display of the network (tkinter)."""

from fly_in.network import Network
import tkinter as tk
from fly_in.models import ZoneRole


class Projection:
    """Convert zone coordinate in canva pixel"""

    def __init__(self, network: Network, width: int, height: int,
                 margin: int = 60) -> None:
        """Find the bounds and compute the scale.

        Args:
            network: The network whose zones must be placed.
            width: Width of the drawing area, in pixels.
            height: Height of the drawing area, in pixels.
            margin: Empty space kept around the zones, in pixels.
        """
        xs = [zone.x for zone in network.zones]
        ys = [zone.y for zone in network.zones]
        self.min_x = min(xs)
        self.min_y = min(ys)
        self.max_x = max(xs)
        self.max_y = max(ys)
        self.margin = margin
        span_x = max(self.max_x - self.min_x, 1)
        span_y = max(self.max_y - self.min_y, 1)
        scale_x = (width - 2 * margin) / span_x
        scale_y = (height - 2 * margin) / span_y
        self.scale = min(scale_x, scale_y)

    def to_pixels(self, x: int, y: int) -> tuple[float, float]:
        """Return the pixel position of the map coordinates (x, y)."""
        px = self.margin + (x - self.min_x) * self.scale
        py = self.margin + (y - self.min_y) * self.scale
        return px, py


class GraphicalDisplay:
    """Show the network in a tkinter window."""

    WIDTH = 3000
    HEIGHT = 1000
    TK_COLORS: dict[str, str] = {
        "red": "#e53935",
        "green": "#2e7d32",
        "yellow": "#fdd835",
        "blue": "#1e40ff",
        "magenta": "#d81b60",
        "cyan": "#26c6da",
        "gray": "#9e9e9e",
        "orange": "#fb8c00",
        "purple": "#8e24aa",
        "brown": "#8d6e63",
        "lime": "#aeea00",
        "gold": "#ffc107",
    }

    DEFAULT_TK_COLOR = "#d3d3d3"

    def __init__(self, network: Network) -> None:
        """Create the window and the drawing area.

        Args:
            network: The network to draw.
        """
        self._network = network
        self._projection = Projection(network, self.WIDTH, self.HEIGHT)
        self._root = tk.Tk()
        self._root.title("Fly-in")
        self._canvas = tk.Canvas(
            self._root, width=self.WIDTH, height=self.HEIGHT, bg="white")
        self._canvas.pack()

    def draw_zones(self) -> None:
        """Draw every zone as a colored circle with its name."""
        for zone in self._network.zones:
            px, py = self._projection.to_pixels(zone.x, zone.y)
            if zone.role is not ZoneRole.REGULAR:
                rayon = 25
            else:
                rayon = 18
            color = self.TK_COLORS.get(zone.color or "", self.DEFAULT_TK_COLOR)
            self._canvas.create_oval(px - rayon, py - rayon, px +
                                     rayon, py + rayon, fill=color)
            self._canvas.create_text(px, py - rayon - 8, text=zone.name,
                                     font=("Arial", 8))

    def draw_connections(self) -> None:
        """Draw every connection as a gray line between its two zones."""
        for connection in self._network.connections:
            pa_x, pa_y = self._projection.to_pixels(
                connection.zone_a.x, connection.zone_a.y)
            pb_x, pb_y = self._projection.to_pixels(
                connection.zone_b.x, connection.zone_b.y)
            width = min(2 * connection.max_link_capacity, 8)
            self._canvas.create_line(
                pa_x, pa_y, pb_x, pb_y, fill="gray",
                width=width, arrow=tk.BOTH)

    def run(self) -> None:
        """Draw the network and keep the window open."""
        self.draw_connections()
        self.draw_zones()
        self._root.mainloop()

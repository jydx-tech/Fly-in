# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  gui.py                                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/29 10:23:55 by jdenaux         #+#    #+#               #
#  Updated: 2026/11/03 15:14:46 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Graphical display of the network (tkinter)."""

from fly_in.network import Network
import tkinter as tk
from fly_in.models import ZoneRole
from fly_in.simulation import Simulation
from fly_in.display import Display


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
    DELAY = 600
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
        "black": "#212121",
        "maroon": "#800000",
        "darkred": "#8b0000",
        "violet": "#ee82ee",
        "crimson": "#dc143c",
        "rainbow": "#ff00ff",
    }

    DEFAULT_TK_COLOR = "#d3d3d3"

    def __init__(self, network: Network, simulation: Simulation,
                 display: Display) -> None:
        """Create the window and the drawing area.

        Args:
            network: The network to draw.
            simulation: simulation of the network
            display: display in the terminal
        """
        self._network = network
        self._display = display
        self._projection = Projection(network, self.WIDTH, self.HEIGHT)
        self._root = tk.Tk()
        self._root.title("Fly-in")
        self._canvas = tk.Canvas(
            self._root, width=self.WIDTH, height=self.HEIGHT, bg="white")
        self._canvas.pack()
        self._simulation = simulation
        self._turn = 0
        self._root.bind("<Right>", self._next)
        self._root.bind("<Left>", self._previous)
        self._playing = False
        self._root.bind("<space>", self._toggle)
        self._root.bind("<s>", self._print_in_terminal)

    def draw_zones(self) -> None:
        """Draw every zone as a colored circle with its name."""
        for zone in self._network.zones:
            px, py = self._projection.to_pixels(zone.x, zone.y)
            if zone.role is not ZoneRole.REGULAR:
                rayon = 35
            else:
                rayon = 28
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
            width = min(3 * connection.max_link_capacity, 10)
            self._canvas.create_line(
                pa_x, pa_y, pb_x, pb_y, fill="gray",
                width=width, arrow=tk.BOTH)

    def draw_drones(self, turn: int) -> None:
        """Draw every drone as it is at the end of the given turn."""
        for drone in self._simulation.drones:
            zone, destination = self._simulation.position_at(drone, turn)
            if not destination:
                px, py = self._projection.to_pixels(zone.x, zone.y)
            else:
                ox, oy = self._projection.to_pixels(zone.x, zone.y)
                dx, dy = self._projection.to_pixels(
                    destination.x, destination.y)
                px, py = (ox + dx) / 2, (oy + dy) / 2
            self._canvas.create_polygon(
                px, py - 20,
                px + 20, py,
                px, py + 20,
                px - 20, py,
                fill="dimgray", tags="drone")
            self._canvas.create_text(
                px, py, text=drone.name, font=("Arial", 7), tags="drone")

    def show_turn(self, turn: int) -> None:
        """Erase the drones and the turn counter, then redraw them."""
        self._canvas.delete("drone")
        self._canvas.delete("hud")
        self.draw_drones(turn)
        self.draw_hud(turn)

    def _next(self, event: tk.Event) -> None:
        """Go to the next turn."""
        if self._turn < self._simulation.last_turn:
            self._turn += 1
            self.show_turn(self._turn)

    def _previous(self, event: tk.Event) -> None:
        """Go to the previous turn."""
        if self._turn > 0:
            self._turn -= 1
            self.show_turn(self._turn)

    def draw_hud(self, turn: int) -> None:
        """Write the current turn number in the top-left corner."""
        last = self._simulation.last_turn
        self._canvas.create_text(
            1500, 800, anchor="nw", text=f"Turn {turn} / {last}",
            font=("Arial", 14), tags="hud")

    def _tick(self) -> None:
        """Advance one turn, then schedule the next one."""
        if not self._playing:
            return
        if self._turn >= self._simulation.last_turn:
            self._playing = False
            return
        self._turn += 1
        self.show_turn(self._turn)
        self._root.after(self.DELAY, self._tick)

    def _toggle(self, event: "tk.Event[tk.Misc]") -> None:
        """Start or stop the automatic playback."""
        self._playing = not self._playing
        if self._playing:
            self._tick()

    def _print_in_terminal(self, event: "tk.Event[tk.Misc]") -> None:
        """Display turn by turn in color in the terminal."""
        self._display.show_turn(
            self._network, self._simulation, self._turn)

    def run(self) -> None:
        """Draw the network and keep the window open."""
        self.draw_connections()
        self.draw_zones()
        self.show_turn(0)
        self._root.mainloop()

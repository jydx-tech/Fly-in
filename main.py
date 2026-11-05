# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/26 09:53:28 by jdenaux         #+#    #+#               #
#  Updated: 2026/11/03 12:13:01 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Entry point of the Fly-in project."""

import sys

from fly_in.errors import FlyInError
from fly_in.parser import MapParser
from fly_in.display import Display
from fly_in.gui import GraphicalDisplay
from fly_in.simulation import Simulation


def main() -> None:
    """Run the simulation on the map given on the command line."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>", file=sys.stderr)
        sys.exit(1)
    try:
        nb_drones, network = MapParser(sys.argv[1]).parse()
        simulation = Simulation(network, nb_drones)
    except FlyInError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    display = Display()
    display.show_zones(network)
    display.show_connections(network)
    while not simulation.is_finished():
        print(" ".join(simulation.play_turn()))
    GraphicalDisplay(network, simulation, display).run()


if __name__ == "__main__":
    main()

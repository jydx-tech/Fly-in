# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/26 09:53:28 by jdenaux         #+#    #+#               #
#  Updated: 2026/10/30 10:55:22 by jdenaux         ###   ########.fr        #
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
    """Parse the map given on the command line."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>", file=sys.stderr)
        sys.exit(1)
    try:
        nb_drones, network = MapParser(sys.argv[1]).parse()
    except FlyInError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    Display().show_zones(network)
    Display().show_connections(network)
    # GraphicalDisplay(network).run()
    simulation = Simulation(network, nb_drones)
    turns = 0
    while not simulation.is_finished() and turns < 100:
        print(" ".join(simulation.play_turn()))
        turns += 1
    print(f"turns: {turns}")


if __name__ == "__main__":
    main()

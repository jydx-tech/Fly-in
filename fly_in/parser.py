# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parser.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/27 15:14:05 by jdenaux         #+#    #+#               #
#  Updated: 2026/10/28 15:25:35 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Parser of the map file."""

from fly_in.errors import ParseError
from fly_in.models import Zone, ZoneRole, ZoneType, Connection
from fly_in.network import Network


class MapParser:
    """Check the map file."""

    def __init__(self, path: str) -> None:
        """Store the path of the map file.

        Args:
            path: Path of the map file to read.
        """
        self._path = path

    def _read_lines(self) -> list[tuple[int, str]]:
        """Clean and save lines.

        Returns
        -------
        list[tuple[int, str]]
             Comments and empty lines are skipped, but the line numbers
             still refer to the original file.
        """
        try:
            with open(self._path, "r") as file:
                lines = file.readlines()
        except OSError as error:
            raise ParseError(f"cannot read '{self._path}': {error}") from error
        clean_file: list[tuple[int, str]] = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            clean_file.append((line_num, line))
        return clean_file

    def _parse_nb_drones(self, lines: list[tuple[int, str]]) -> int:
        """Return the number of drones declared on the first line.

        Raises:
            ParseError: If the first line is missing or invalid.
        """
        if not lines:
            raise ParseError("empty map file")
        line_num, text = lines[0]
        if not text.startswith("nb_drones:"):
            raise ParseError(
                f"first line must be 'nb_drones:"
                f" <number>', got '{text}'", line_num)
        nb = text.split(":", 1)[1].strip()
        try:
            value = int(nb)
        except ValueError as error:
            raise ParseError(
                f"nb_drones must be an integer,"
                f" got '{nb}'", line_num) from error
        if value <= 0:
            raise ParseError("nb_drones must be > 0", line_num)
        return value

    def _parse_metadata(self, text: str, line_num: int) -> dict[str, str]:
        """Return key/value of metadata.

        Parameters
        ----------
        text : str
            The block, brackets included (e.g. "[color=red]").
        line_num : int
            Line of the file, used in error messages.

        Raises:
            ParseError: If the block is not valid.
        """
        if not text.startswith("[") or not text.endswith("]"):
            raise ParseError(
                f"metadata must be '[data=example]'"
                f" , got '{text}'", line_num)
        string = text[1:-1]
        datas = string.split()
        hub_metadata: dict[str, str] = {}
        for data in datas:
            if "=" not in data:
                raise ParseError(f"missing '=' in metadata, got {text}",
                                 line_num)
            key, value = data.split('=', 1)
            if not key or not value:
                raise ParseError(f"invalid syntax metadata, got {text}",
                                 line_num)
            if key in hub_metadata:
                raise ParseError(f"double metadata, {key}", line_num)
            hub_metadata[key] = value
        return hub_metadata

    def _parse_zone(self, text: str, line_num: int) -> Zone:
        """Build a Zone from a zone line.

        Raises:
            ParseError: If the line is invalid.
        """
        zone_type = ZoneType.NORMAL

        color: str | None = None
        max_drones = 1
        if ":" not in text:
            raise ParseError("invalid syntax, missing ':'", line_num)
        prefix, reste = text.split(":", 1)
        prefix = prefix.strip()
        role_dict = {"start_hub": ZoneRole.START,
                     "hub": ZoneRole.REGULAR,
                     "end_hub": ZoneRole.END}
        if prefix not in role_dict:
            raise ParseError(f"hub role error, got {prefix}", line_num)
        role = role_dict[prefix]
        cut = reste.find("[")
        if cut != -1:
            infos = reste[:cut]
            metadata = reste[cut:]
            dict_meta = self._parse_metadata(metadata, line_num)
            for key in dict_meta.keys():
                if key not in {"zone", "color", "max_drones"}:
                    raise ParseError(f"invalid metadata key, got {key}",
                                     line_num)
                if key == "zone":
                    try:
                        zone_type = ZoneType(dict_meta[key])
                    except ValueError as error:
                        raise ParseError(
                            f"invalid zone type, got {dict_meta[key]}",
                            line_num) from error
                if key == "color":
                    color = dict_meta[key]
                if key == "max_drones":
                    try:
                        max_drones = int(dict_meta[key])
                    except ValueError as error:
                        raise ParseError(
                            f"invalid max drones, got {dict_meta[key]}",
                            line_num) from error
                    if max_drones <= 0:
                        raise ParseError(
                            f"invalid positif max drones,"
                            f" got {dict_meta[key]}",
                            line_num)
        else:
            infos = reste
        name_and_coords = infos.split()
        if len(name_and_coords) != 3:
            raise ParseError(f"invalid hub syntax, got {infos}", line_num)
        hub_name = name_and_coords[0]
        sx = name_and_coords[1]
        sy = name_and_coords[2]
        try:
            x = int(sx)
            y = int(sy)
        except ValueError as error:
            raise ParseError(f"coordinate must be valid int, got {infos}",
                             line_num) from error
        if "-" in hub_name:
            raise ParseError(f"no '-' in name, got {hub_name}", line_num)
        return Zone(hub_name, x, y, zone_type, color, max_drones, role)

    def _parse_connection(
            self, text: str, line_num: int) -> tuple[str, str, int]:
        """Return (name1, name2, capacity) of a connection line.

        Raises:
            ParseError: If the line is invalid.
        """
        max_link_capacity = 1
        if ":" not in text:
            raise ParseError("invalid syntax, missing ':'", line_num)
        prefix, reste = text.split(":", 1)
        prefix = prefix.strip()
        if prefix != "connection":
            raise ParseError(
                "invalid syntax prefix expected 'connection:'", line_num)
        cut = reste.find("[")
        if cut != -1:
            infos = reste[:cut]
            metadata = reste[cut:]
            dict_meta = self._parse_metadata(metadata, line_num)
            for key in dict_meta.keys():
                if key not in {"max_link_capacity"}:
                    raise ParseError(f"invalid metadata key, got {key}",
                                     line_num)
                try:
                    max_link_capacity = int(dict_meta[key])
                except ValueError as error:
                    raise ParseError(
                        f"invalid max link capacity, got {dict_meta[key]}",
                        line_num) from error
                if max_link_capacity <= 0:
                    raise ParseError(
                        f"invalid positif max link capacity,"
                        f" got {dict_meta[key]}",
                        line_num)
        else:
            infos = reste
        names = infos.strip()
        if len(names.split("-")) != 2:
            raise ParseError(
                f"invalid zone name connection, got {names}", line_num)
        name1, name2 = names.split("-")
        if not name1 or not name2 or " " in name1 or " " in name2:
            raise ParseError(
                f"invalid zone name connection, got {names}", line_num)
        return name1, name2, max_link_capacity

    def parse(self) -> tuple[int, Network]:
        """Read the map file and build the network.

        Returns:
            The number of drones and the network.

        Raises:
            ParseError: If the file is invalid.
        """
        lines = self._read_lines()
        nb_drones = self._parse_nb_drones(lines)
        network = Network()
        start = 0
        end = 0
        for line_num, text in lines[1:]:
            if text.startswith(("start_hub:", "end_hub:", "hub:")):
                zone = self._parse_zone(text, line_num)
                if zone.role is ZoneRole.START:
                    start += 1
                    if start > 1:
                        raise ParseError("too much start", line_num)
                if zone.role is ZoneRole.END:
                    end += 1
                    if end > 1:
                        raise ParseError("too much end", line_num)
                try:
                    network.add_zone(zone)
                except ValueError as error:
                    raise ParseError(str(error), line_num) from error
            elif text.startswith("connection:"):
                name1, name2, capacity = self._parse_connection(
                    text, line_num)
                if name1 == name2:
                    raise ParseError(
                        f"connection '{text}' links a zone to itself",
                        line_num)
                try:
                    zone1 = network.get_zone(name1)
                    zone2 = network.get_zone(name2)
                    connection = Connection(zone1, zone2, capacity)
                    network.add_connection(connection)
                except ValueError as error:
                    raise ParseError(str(error), line_num) from error
            else:
                raise ParseError(f"unknown line '{text}'", line_num)
        if start != 1:
            raise ParseError("error there is no start hub")
        if end != 1:
            raise ParseError("error there is no end hub")
        return nb_drones, network

# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  errors.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: jdenaux <jdenaux@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/10/26 10:13:08 by jdenaux         #+#    #+#               #
#  Updated: 2026/10/26 13:33:41 by jdenaux         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Custom exeptions for the fly_in project"""


class FlyInError(Exception):
    """Base class for all error."""


class ParseError(FlyInError):
    """Raised when invalid parse of the map file."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        """Store the error message and his line number

        Parameters
        ----------
        message : str
            cause of the error
        line_number : int | None, optional
            line in the file where is the error, by default None
        """
        if line_number is not None:
            message = f"line {line_number}: {message}"
        super().__init__(message)


class UnsolvableError(FlyInError):
    """No valid path, start to end."""

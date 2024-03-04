# Copyright 2024 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Base methods for Open Ondemand configuration file editors."""

import logging
from os import PathLike
from pathlib import Path
from typing import Union

import yaml

_logger = logging.getLogger(__name__)


def dump(obj, file: Union[str, PathLike]) -> None:
    """Serialise configuration into file using the `.yaml()` method of the provided object.

    Do not use this function directly.
    """
    if (loc := Path(file)).exists():
        _logger.warning("Overwriting contents of %s file located at %s.", loc.name, loc)

    _logger.debug("Dumping YAML configuration into %s file located at %s.", loc.name, loc)
    Path(file).write_text(yaml.dump(obj._register))


def dumps(obj) -> str:
    """Dump configuration into a string using the `.yaml()` method of the provided object.

    Do not use this function directly.
    """
    return obj.yaml()


def load_base(file: Union[str, PathLike], cls):
    """Load configuration from file using provided parsing function.

    Do not use this function directly.
    """
    if (file := Path(file)).exists():
        _logger.debug("Parsing contents of %s located at %s.", file.name, file)
        config = file.read_text()
        return cls.from_yaml(config)
    else:
        msg = "Unable to locate file"
        _logger.error(msg + " %s.", file)
        raise FileNotFoundError(msg + f" {file}")


def loads_base(content: str, cls):
    """Load configuration from Python String using provided parsing function.

    Do not use this function directly.
    """
    return cls.from_yaml(content)

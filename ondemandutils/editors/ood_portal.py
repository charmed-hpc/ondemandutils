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

"""Edit ood_portal.yml files."""

__all__ = ["dump", "dumps", "load", "loads", "edit"]

import os
from contextlib import contextmanager
from functools import partial
from typing import Union

from ondemandutils.models import OODPortalConfig

from ._editor import dump, dumps, load_base, loads_base

# Bind dump functions into module namespace.
dump = dump
dumps = dumps

# Declare partials for load functions.
load = partial(load_base, cls=OODPortalConfig)
loads = partial(loads_base, cls=OODPortalConfig)

# Documentation for module functions.
dump.__doc__ = """
Serialise an `OODPortalConfig` object into a YAML document file.

Args:
    obj: `OODPortalConfig` object to serialise into a YAML document.
    file: File to serialise `OODPortalConfig` object into.
"""

dumps.__doc__ = """
Serialise an `OODPortalConfig` object into a YAML document string.

Args:
    obj: `OODPortalConfig` object to serialise into a YAML document.
"""

load.__doc__ = """
Deserialise a YAML document file into an `OODPortalConfig` object. 

Args:
    file: `ood_portal.yml` file to deserialise into an `OODPortalConfig` object.
"""

loads.__doc__ = """
Deserialise a YAML document string into an `OODPortalConfig` object.

Args:
    content: String content to deserialise into an `OODPortalConfig` object.
"""


@contextmanager
def edit(file: Union[str, os.PathLike]) -> OODPortalConfig:
    """Edit an `ood_portal.yml` configuration file.

    Args:
        file: File path to `ood_portal.yml`. If `ood_portal.yml` does not exist
            at the given path, a blank `ood_portal.yml` will be created.
    """
    if not os.path.exists(file):
        config = OODPortalConfig()
    else:
        config = load(file=file)

    yield config
    dump(obj=config, file=file)

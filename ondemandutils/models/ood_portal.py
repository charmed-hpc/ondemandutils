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

"""Data models for the `ood_portal.yml` configuration file."""

from typing import Any, Dict

from ._model import BaseModel, assert_type, base_descriptors
from ._options import DexOptions, OODPortalOptions


class DexConfig(BaseModel):
    """Data model representing Dex configuration inside `ood_portal.yml`."""

    def __init__(self, obj: Dict[str, Any] = None, /, **kwargs) -> None:
        super().__init__(obj, **kwargs, validator=DexOptions)


# Generate descriptors for accessing Dex configuration options.
for e in DexOptions:
    attr_name = e.name.lower()
    setattr(DexConfig, attr_name, property(*base_descriptors(attr_name)))


class OODPortalConfig(BaseModel):
    """Data model representing the `ood_portal.yml` configuration file."""

    def __init__(self, obj: Dict[str, Any] = None, /, **kwargs) -> None:
        super().__init__(obj, **kwargs, validator=OODPortalOptions)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if key == "dex":
            return DexConfig(**value)

        return value

    def __setitem__(self, key, value):
        if key == "dex" and not isinstance(value, DexConfig):
            try:
                v = value or {}
                value = DexConfig(**v)
            except AttributeError:
                raise TypeError(
                    f"Expected `{DexConfig.__name__}` for key '{key}', not {type(value)}."
                )

        super().__setitem__(key, value)

    @property
    def dex(self) -> DexConfig:
        """Get Dex IDP service configuration."""
        return self["dex"]

    @dex.setter
    @assert_type(value=DexConfig)
    def dex(self, value: DexConfig) -> None:
        """Set new Dex IDP service configuration."""
        self["dex"] = value.dict()

    @dex.deleter
    def dex(self) -> None:
        """Delete Dex IDP service configuration."""
        self["dex"] = {}


# Generate descriptors for accessing `ood_portal.yml` configuration options.
for e in OODPortalOptions:
    attr_name = e.name.lower()
    # `Dex` section of document is assigned a custom descriptor.
    if attr_name == "dex":
        continue

    setattr(OODPortalConfig, attr_name, property(*base_descriptors(attr_name)))

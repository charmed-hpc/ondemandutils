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

"""Unit tests for the `BaseModel` class that all data models inherit from."""

import unittest

from ondemandutils.models import NginxStageConfig, OODPortalConfig


class TestBaseModel(unittest.TestCase):
    """Unit tests for the `BaseModel` parent class."""

    def test_merge(self) -> None:
        """Test the `__or__`, `__ror__`, and `__ior__` magic methods."""
        portal_conf_1 = OODPortalConfig.from_dict(
            {"servername": "10.69.205.59", "logroot": "/var/log", "lua_log_level": "debug"}
        )
        portal_conf_2 = OODPortalConfig.from_dict(
            {
                "lua_root": "/usr/local/ood/mod_ood_proxy/lib",
                "server_aliases": ["ondemand.ubuntu.com", "ondemand.charmed-hpc.rocks"],
                "auth": ["AuthType openid-connect", "Require valid-user"],
                "user_env": [{"PATH": "/opt/bin:$PATH"}],
            }
        )

        new_portal_1 = portal_conf_1 | portal_conf_2
        new_portal_2 = portal_conf_2 | portal_conf_1
        portal_conf_1 |= portal_conf_2
        self.assertDictEqual(new_portal_1.dict(), new_portal_2.dict())
        self.assertDictEqual(portal_conf_1.dict(), new_portal_1.dict())

    def test_bad_merge(self) -> None:
        """Test the `__or__`, `__ror__`, and `__ior__` magic methods with bad inputs."""
        portal_conf = OODPortalConfig.from_dict(
            {"servername": "10.69.205.59", "logroot": "/var/log", "lua_log_level": "debug"}
        )
        nginx_stage_conf = NginxStageConfig.from_dict(
            {
                "passenger_ruby": "/snap/ondemand/common/usr/bin/ruby",
                "passenger_nodejs": "/snap/ondemand/common/bin/node",
                "passenger_python": "/snap/ondemand/common/bin/python3",
                "pun_custom_env_declarations": [
                    "PATH",
                    "LD_LIBRARY_PATH",
                    "MANPATH",
                    "SCLS",
                    "X_SCLS",
                    "CPATH",
                ],
            }
        )

        with self.assertRaises(TypeError):
            _ = portal_conf | nginx_stage_conf
            _ = nginx_stage_conf | portal_conf
            portal_conf |= nginx_stage_conf

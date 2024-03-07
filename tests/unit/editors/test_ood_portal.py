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

"""Unit tests for the `ood_portal.yml` configuration editor."""

import tempfile
import unittest
from pathlib import Path

from ondemandutils.editors import ood_portal
from ondemandutils.models import DexConfig, OODPortalConfig

example_ood_portal_yml = r"""#
# `ood_portal.yml` generated at 2024-03-05 09:59:02.084563 by ondemandutils.
#

listen_addr_port: 443
servername: 10.69.205.59
server_aliases: ['www.example.com', 'www.awjeezrick.com']
proxy_server: null
port: 8080
ssl: null
logroot: 'logs'
errorlog: 'error.log'
accesslog: 'access.log'
logformat: Apache combine format
use_rewrites: true
use_maintenance: true
maintenance_ip_allowlist: []
security_csp_frame_ancestors:
security_strict_transport: false
lua_root: '/opt/ood/mod_ood_proxy/lib'
lua_log_level: 'info'
user_map_match: '.*'
user_map_cmd: null
user_env: null
map_fail_uri: null
pun_stage_cmd: 'sudo /opt/ood/nginx_stage/sbin/nginx_stage'
auth:
  - 'AuthType openid-connect'
  - 'Require valid-user'
root_uri: '/pun/sys/dashboard'
analytics: null
public_uri: '/public'
public_root: '/var/www/ood/public'
logout_uri: '/logout'
logout_redirect: '/pun/sys/dashboard/logout'
host_regex: '[^/]+'
node_uri: null
rnode_uri: null
nginx_uri: '/nginx'
pun_uri: '/pun'
pun_socket_root: '/var/run/ondemand-nginx'
pun_max_retries: 5
pun_pre_hook_root_cmd: null
pun_pre_hook_exports: null
oidc_uri: null
oidc_discover_uri: null
oidc_discover_root: null
register_uri: null
register_root: null
oidc_provider_metadata_url: null
oidc_client_id: null
oidc_client_secret: null
oidc_remote_user_claim: preferred_username
oidc_scope: "openid profile email"
oidc_session_inactivity_timeout: 28800
oidc_session_max_duration: 28800
oidc_state_max_number_of_cookies: "10 true"
oidc_cookie_same_site: 'On'
oidc_settings: {}
dex_uri: /dex
dex:
  ssl: false
  http_port: 5551
  https_port: 5554
  tls_cert: null
  tls_key: null
  storage_file: /etc/ood/dex/dex.db
  grpc: null
  expiry: null
  client_id: null
  client_name: OnDemand
  client_secret: /etc/ood/dex/ondemand.secret
  client_redirect_uris: []
  connectors:
    - type: ldap
      id: ldap
      name: LDAP
      config:
        host: openldap.my_center.edu:636
        insecureSkipVerify: false
        bindDN: cn=admin,dc=example,dc=org
        bindPW: admin
        userSearch:
          baseDN: ou=People,dc=example,dc=org
          filter: "(objectClass=posixAccount)"
          username: uid
          idAttr: uid
          emailAttr: mail
          nameAttr: gecos
          preferredUsernameAttr: uid
        groupSearch:
          baseDN: ou=Groups,dc=example,dc=org
          filter: "(objectClass=posixGroup)"
          userMatchers:
            - userAttr: DN
              groupAttr: member
          nameAttr: cn
  frontend:
    theme: ondemand
    dir: /usr/share/ondemand-dex/web
"""


class TestDexConfigEditor(unittest.TestCase):
    """Unit tests for the nested Dex configuration in `ood_portal.yml`."""

    def setUp(self) -> None:
        Path("ood_portal.yaml").write_text(example_ood_portal_yml)

    def test_dex_config(self) -> None:
        """Test setting a Dex service configuration in `ood_portal.yml`."""
        dex_config = DexConfig()
        dex_config.http_port = 5556
        dex_config.tls_cert = "/var/snap/ondemand/common/tls.cert"
        dex_config.tls_key = "/var/snap/ondemand/common/tls.secret"
        dex_config.frontend = {"dir": "/var/snap/ondemand/common/web", "theme": "ondemand"}

        with ood_portal.edit("ood_portal.yaml") as portal_config:
            portal_config.dex = dex_config

        with ood_portal.edit("ood_portal.yaml") as portal_config:
            self.assertDictEqual(portal_config.dex.dict(), dex_config.dict())
            del portal_config.dex

        portal_config = ood_portal.load("ood_portal.yaml")
        # Ensure that empty `DexConfig` object is returned by getter.
        self.assertDictEqual(portal_config.dex.dict(), DexConfig().dict())

    def test_bad_dex_config(self) -> None:
        """Test setting a bad Dex service configuration in `ood_portal.yml`."""
        # Attempt setting a bad Dex configuration on `OODPortalConfig`.
        # Setter should raise an error if the type does not match.
        portal_config = OODPortalConfig()
        with self.assertRaises(TypeError):
            portal_config.dex = "awjeezrick"

        with self.assertRaises(AttributeError):
            # Set some random, non-existent value on the Dex configuration.
            DexConfig(spill_secrets="SHREK!")

    def tearDown(self) -> None:
        Path("ood_portal.yaml").unlink()


class TestOODPortalEditor(unittest.TestCase):
    """Unit tests for `ood_portal.yml` editor."""

    def setUp(self) -> None:
        Path("ood_portal.yaml").write_text(example_ood_portal_yml)

    def test_loads(self) -> None:
        """Test `loads` function of the ood_portal module."""
        config = ood_portal.loads(example_ood_portal_yml)
        self.assertListEqual(config.auth, ["AuthType openid-connect", "Require valid-user"])
        self.assertListEqual(config.server_aliases, ["www.example.com", "www.awjeezrick.com"])
        self.assertEqual(config.public_root, "/var/www/ood/public")
        self.assertEqual(config.pun_stage_cmd, "sudo /opt/ood/nginx_stage/sbin/nginx_stage")

    def test_dumps(self) -> None:
        """Test `dumps` function of the ood_portal module."""
        config = ood_portal.loads(example_ood_portal_yml)
        # The new configuration and old configuration will not be equal since the
        # timestamps in the header will be different.
        self.assertNotEqual(ood_portal.dumps(config), example_ood_portal_yml)

    def test_edit(self) -> None:
        """Test `edit` context manager of the ood_portal module."""
        with ood_portal.edit("ood_portal.yaml") as config:
            config.servername = "commander-1"
            config.server_aliases = []
            config.ssl = None
            config.public_root = "/var/snap/ondemand/common" + config.public_root
            config.log_root = "/var/snap/ondemand/common/var/logs/ondemand"
            config.pun_stage_cmd = "sudo /snap/ondemand/current/nginx_stage/sbin/nginx_stage"

        config = ood_portal.load("ood_portal.yaml")
        self.assertEqual(config.servername, "commander-1")
        self.assertListEqual(config.server_aliases, [])
        self.assertIsNone(config.ssl)
        self.assertEqual(config.public_root, "/var/snap/ondemand/common/var/www/ood/public")
        self.assertEqual(
            config.pun_stage_cmd, "sudo /snap/ondemand/current/nginx_stage/sbin/nginx_stage"
        )

    def test_empty_config(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        tmp_file = tmp.name + "/ood_portal.yaml"

        with ood_portal.edit(tmp_file) as config:
            config.servername = "commander-1"

        config = ood_portal.load(tmp_file)
        self.assertEqual(config.servername, "commander-1")
        self.assertIsNone(config.oidc_client_id)

        tmp.cleanup()

    def tearDown(self) -> None:
        Path("ood_portal.yaml").unlink()

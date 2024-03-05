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

"""Unit tests for the `nginx_stage.yml` configuration editor."""

import tempfile
import unittest
from pathlib import Path

from ondemandutils.editors import nginx_stage

example_nginx_stage_yml = r"""#
# `nginx_stage.yml` generated at 2024-03-05 09:59:02.084563 by ondemandutils.
#

ondemand_version_path: '/opt/ood/VERSION'
ondemand_portal: null
ondemand_title: null
pun_custom_env:
   OOD_DASHBOARD_TITLE: "Open OnDemand"
   OOD_BRAND_BG_COLOR: "#53565a"
   OOD_BRAND_LINK_ACTIVE_BG_COLOR: "#fff"
pun_custom_env_declarations:
  - PATH
  - LD_LIBRARY_PATH
  - MANPATH
  - SCLS
  - X_SCLS
template_root: '/opt/ood/nginx_stage/templates'
proxy_user: 'apache'
nginx_bin: '/opt/ood/ondemand/root/usr/sbin/nginx'
nginx_signals:
  - 'stop'
  - 'quit'
  - 'reopen'
  - 'reload'
mime_types_path: '/opt/ood/ondemand/root/etc/nginx/mime.types'
passenger_root: '/opt/ood/ondemand/root/usr/share/ruby/vendor_ruby/phusion_passenger/locations.ini'
passenger_ruby: '/opt/ood/nginx_stage/bin/ruby'
passenger_nodejs: '/opt/ood/nginx_stage/bin/node'
passenger_python: '/opt/ood/nginx_stage/bin/python'
passenger_pool_idle_time: 300
passenger_options: {}
nginx_file_upload_max: '10737420000'
pun_config_path: '/var/lib/ondemand-nginx/config/puns/%{user}.conf'
pun_tmp_root: '/var/tmp/ondemand-nginx/%{user}'
pun_access_log_path: '/var/log/ondemand-nginx/%{user}/access.log'
pun_error_log_path: '/var/log/ondemand-nginx/%{user}/error.log'
pun_secret_key_base_path: '/var/lib/ondemand-nginx/config/puns/%{user}.secret_key_base.txt'
pun_log_format: '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for"'
pun_pid_path: '/var/run/ondemand-nginx/%{user}/passenger.pid'
pun_socket_path: '/var/run/ondemand-nginx/%{user}/passenger.sock'
pun_sendfile_root: '/'
pun_sendfile_uri: '/sendfile'
pun_app_configs:
  - env: 'dev'
    owner: '%{user}'
    name: '*'
  - env: 'usr'
    owner: '*'
    name: '*'
  - env: 'sys'
    owner: ''
    name: '*'
app_config_path:
  dev: '/var/lib/ondemand-nginx/config/apps/dev/%{owner}/%{name}.conf'
  usr: '/var/lib/ondemand-nginx/config/apps/usr/%{owner}/%{name}.conf'
  sys: '/var/lib/ondemand-nginx/config/apps/sys/%{name}.conf'
app_root:
  dev: '/var/www/ood/apps/dev/%{owner}/gateway/%{name}'
  usr: '/var/www/ood/apps/usr/%{owner}/gateway/%{name}'
  sys: '/var/www/ood/apps/sys/%{name}'
app_request_uri:
  dev: '/dev/%{name}'
  usr: '/usr/%{owner}/%{name}'
  sys: '/sys/%{name}'
app_request_regex:
  dev: '^/dev/(?<name>[-\w.]+)'
  usr: '^/usr/(?<owner>[\w]+)\/(?<name>[-\w.]+)'
  sys: '^/sys/(?<name>[-\w.]+)'
app_token:
  dev: 'dev/%{owner}/%{name}'
  usr: 'usr/%{owner}/%{name}'
  sys: 'sys/%{name}'
app_passenger_env:
  dev: 'development'
  usr: 'production'
  sys: 'production'
user_regex: '[\w@\.\-]+'
min_uid: 1000
disabled_shell: '/access/denied'
disable_bundle_user_config: true
"""


class TestNginxStageEditor(unittest.TestCase):
    """Unit tests for `nginx_stage.yml` editor."""

    def setUp(self) -> None:
        Path("nginx_stage.yaml").write_text(example_nginx_stage_yml)

    def test_loads(self) -> None:
        """Test `loads` function of the ood_portal module."""
        config = nginx_stage.loads(example_nginx_stage_yml)
        self.assertEqual(config.ondemand_version_path, "/opt/ood/VERSION")
        self.assertEqual(config.template_root, "/opt/ood/nginx_stage/templates")
        self.assertEqual(config.passenger_python, "/opt/ood/nginx_stage/bin/python")
        self.assertTrue(config.disable_bundle_user_config)
        self.assertListEqual(
            config.pun_custom_env_declarations,
            ["PATH", "LD_LIBRARY_PATH", "MANPATH", "SCLS", "X_SCLS"],
        )

    def test_dumps(self) -> None:
        """Test `dumps` function of the ood_portal module."""
        config = nginx_stage.loads(example_nginx_stage_yml)
        # The new configuration and old configuration will not be equal since the
        # timestamps in the header will be different.
        self.assertNotEqual(nginx_stage.dumps(config), example_nginx_stage_yml)

    def test_edit(self) -> None:
        """Test `edit` context manager of the ood_portal module."""
        with nginx_stage.edit("nginx_stage.yaml") as config:
            config.pun_access_log_path = "/var/snap/ondemand/common" + config.pun_access_log_path
            config.pun_error_log_path = "/var/snap/ondemand/common" + config.pun_error_log_path
            config.passenger_ruby = "/snap/ondemand/common/usr/bin/ruby"
            config.passenger_nodejs = "/snap/ondemand/common/bin/node"
            config.passenger_root = "/snap/ondemand/current/opt/passenger/locations.ini"
            config.disable_bundle_user_config = False
            config.pun_custom_env_declarations.append("CPATH")

        config = nginx_stage.load("nginx_stage.yaml")
        self.assertEqual(
            config.pun_access_log_path,
            "/var/snap/ondemand/common/var/log/ondemand-nginx/%{user}/access.log",
        )
        self.assertEqual(
            config.pun_error_log_path,
            "/var/snap/ondemand/common/var/log/ondemand-nginx/%{user}/error.log",
        )
        self.assertEqual(config.passenger_ruby, "/snap/ondemand/common/usr/bin/ruby")
        self.assertEqual(config.passenger_nodejs, "/snap/ondemand/common/bin/node")
        self.assertEqual(
            config.passenger_root, "/snap/ondemand/current/opt/passenger/locations.ini"
        )
        self.assertFalse(config.disable_bundle_user_config)
        self.assertListEqual(
            config.pun_custom_env_declarations,
            ["PATH", "LD_LIBRARY_PATH", "MANPATH", "SCLS", "X_SCLS", "CPATH"],
        )

    def test_empty_config(self) -> None:
        """Test `edit` context manager when there is no pre-existing configuration."""
        tmp = tempfile.TemporaryDirectory()
        tmp_file = tmp.name + "/nginx_stage.yaml"

        with nginx_stage.edit(tmp_file) as config:
            config.ondemand_title = "Charmed HPC"

        config = nginx_stage.load(tmp_file)
        self.assertEqual(config.ondemand_title, "Charmed HPC")
        self.assertIsNone(config.pun_custom_env)

        tmp.cleanup()

    def tearDown(self) -> None:
        Path("nginx_stage.yaml").unlink()

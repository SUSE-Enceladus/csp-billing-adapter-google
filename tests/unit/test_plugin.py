#
# Copyright 2023 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
from urllib.error import HTTPError

from unittest.mock import Mock, MagicMock, patch

from csp_billing_adapter.adapter import get_plugin_manager
from csp_billing_adapter_google import plugin
from csp_billing_adapter.config import Config

# Comment out the following for now, not currently used which
# flake8 flags as error
# import pytest
# from unittest.mock import Mock, patch


pm = get_plugin_manager()
config = Config.load_from_file(
    'tests/data/config_good.yaml',
    pm.hook
)


def test_setup():
    plugin.setup_adapter(config)  # Currently no-op


def test_get_csp_name():
    assert plugin.get_csp_name(config) == 'google'


@patch('csp_billing_adapter_google.plugin.urllib.request.urlopen')
def test_get_account_info(mock_urlopen):
    urlopen = Mock()
    urlopen.read.return_value = b'identity'
    mock_urlopen.return_value = urlopen

    info = plugin.get_account_info(config)
    assert info == {
        'cloud_provider': 'google',
        'identity': 'identity'
    }


@patch('csp_billing_adapter_google.plugin.urllib.request.urlopen')
def test_fetch_metadata_fail(mock_urlopen):
    urlopen = MagicMock()
    urlopen.read.side_effect = HTTPError(
        'http://169.254.169.254/computeMetadata/v1',
        500,
        'Internal Error',
        {},
        None
    )
    urlopen.__enter__.return_value = urlopen
    mock_urlopen.return_value = urlopen

    metadata = plugin._fetch_metadata()
    assert metadata == "{}"


@patch('csp_billing_adapter_google.plugin.urllib.request.urlopen')
def test_meter_billing_pass(mock_urlopen):
    urlopen = Mock()
    urlopen.read.return_value = b'sure'
    mock_urlopen.return_value = urlopen

    dimensions = {'tier_1': 10}
    timestamp = datetime.datetime.now(datetime.timezone.utc)

    status = plugin.meter_billing(
        config,
        dimensions,
        timestamp,
        '2024-10-02T17:58:09.985794+00:00',
        '2024-10-02T17:58:09.985794+00:00',
        dry_run=True
    )
    status["tier_1"] == {'status': 'submitted'}


@patch('csp_billing_adapter_google.plugin.urllib.request.urlopen')
def test_meter_billing_fail(mock_urlopen):
    urlopen = Mock()
    urlopen.read.side_effect = HTTPError(
        'http://localhost:4567/report',
        500,
        'Internal Error',
        {},
        None
    )
    mock_urlopen.return_value = urlopen

    dimensions = {'tier_1': 10}
    timestamp = datetime.datetime.now(datetime.timezone.utc)

    status = plugin.meter_billing(
        config,
        dimensions,
        timestamp,
        '2024-10-02T17:58:09.985794+00:00',
        '2024-10-02T17:58:09.985794+00:00',
        dry_run=True
    )
    assert status["tier_1"] == {
        'error': (
            r'Failed to meter bill dimension tier_1: '
            r'HTTP Error 500: '
            r'Internal Error'
            ),
        'status': 'failed'
    }


def test_get_version():
    version = plugin.get_version()
    assert version[0] == 'google_plugin'
    assert version[1]

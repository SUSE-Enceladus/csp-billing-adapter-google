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
from csp_billing_adapter.adapter import get_plugin_manager
from csp_billing_adapter_google import plugin
from csp_billing_adapter.config import Config

# Comment out the following for now, not currently used which
# flake8 flags as error
# import pytest
# from unittest.mock import Mock, patch


good_config_file = 'tests/data/config_good.yaml'
bad_config_file = 'tests/data/config_bad.yaml'
missing_config_file = 'tests/data/config_missing.yaml'

pm = get_plugin_manager()
config = Config.load_from_file(
    'tests/data/config_good.yaml',
    pm.hook
)


def test_setup():
    plugin.setup_adapter(config)  # Currently no-op


def test_get_csp_name():
    assert plugin.get_csp_name(config) == 'google'


def test_get_account_info():
    plugin.get_account_info(config)  # Currently no-op


def test_meter_billing():   # Currently no-op
    dimensions = {'tier_1': 10}
    timestamp = datetime.datetime.now(datetime.timezone.utc)

    plugin.meter_billing(
        config,
        dimensions,
        timestamp,
        dry_run=True
    )

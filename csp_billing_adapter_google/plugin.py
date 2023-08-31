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

import csp_billing_adapter
import urllib.request
import urllib.error

from csp_billing_adapter.config import Config

METADATA_ADDR = 'http://169.254.169.254/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
AUDIENCE = 'http://smt-gce.susecloud.net'
IDENTITY_URL = (METADATA_ADDR +
                'instance/service-accounts/default/' +
                'identity?audience={audience}&format={format}')


@csp_billing_adapter.hookimpl
def setup_adapter(config: Config):
    pass


@csp_billing_adapter.hookimpl(trylast=True)
def meter_billing(
    config: Config,
    dimensions: dict,
    timestamp: str,
    dry_run: bool
) -> dict:
    return {}


@csp_billing_adapter.hookimpl(trylast=True)
def get_csp_name(config: Config) -> str:
    return 'google'


@csp_billing_adapter.hookimpl(trylast=True)
def get_account_info(config: Config) -> dict:
    """
    Return a dictionary with account information

    The information contains the cloud provider
    and the metadata for instance and project.
    """
    account_info = {}
    account_info['identity'] = _get_identity()
    account_info['cloud_provider'] = get_csp_name(config)
    return account_info


def _get_identity():
    """Return instance identity."""
    identity = _fetch_metadata()
    return identity.decode()


def _fetch_metadata():
    """Return the response of the metadata request."""
    url = IDENTITY_URL.format(audience=AUDIENCE, format='full')
    data_request = urllib.request.Request(url, headers=METADATA_HEADERS)
    try:
        value = urllib.request.urlopen(data_request).read()
    except urllib.error.URLError:
        return None

    return value

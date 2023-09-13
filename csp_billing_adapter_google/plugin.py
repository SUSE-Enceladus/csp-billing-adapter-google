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
import functools
import json
import logging
import urllib.request
import urllib.error

from datetime import datetime

from csp_billing_adapter.config import Config
from csp_billing_adapter.utils import retry_on_exception

METADATA_ADDR = 'http://169.254.169.254/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
AUDIENCE = 'http://smt-gce.susecloud.net'
IDENTITY_URL = (METADATA_ADDR +
                'instance/service-accounts/default/' +
                'identity?audience={audience}&format={format}')

log = logging.getLogger('CSPBillingAdapter')

UBBA_REPORT_URL = 'http://localhost:4567/report'


@csp_billing_adapter.hookimpl
def setup_adapter(config: Config):
    pass


@csp_billing_adapter.hookimpl(trylast=True)
def meter_billing(
    config: Config,
    dimensions: dict,
    timestamp: datetime,
    dry_run: bool
) -> dict:
    """
    Process a metered billing based on the dimensions provided

    Uses Google's User Based Billing Agent (ubbagent) as a sidecar
    If a single dimension is provided the meter_usage API is
    used for the metering. If there is an error the metering
    is attempted 3 times before re-raising the exception to
    calling scope.
    """
    status = {}

    for dimension_name, usage_quantity in dimensions.items():
        body = {
            "name": dimension_name,
            "startTime": str(timestamp),
            "endTime":  str(timestamp),
            "value": {
                'int64value': usage_quantity,
                },
            }
        uubody = json.dumps(body)
        req = urllib.request.Request(
            UBBA_REPORT_URL,
            data=uubody.encode(),
            headers={
                'Content-type': 'application/json'
                },
            method='POST'
            )

        exc = None
        response = None

        try:
            response = retry_on_exception(
                functools.partial(
                    urllib.request.urlopen,
                    req
                ),
                logger=log,
                func_name="urllib.request.urlopen"
            )
            print(response.read().decode())
        except Exception as error:
            exc = error
            print(str(exc))
        else:
            status[dimension_name] = {
                'status': 'submitted'
            }
            exc = None

        if exc:
            msg = (
                f'Failed to meter bill dimension {dimension_name}: {str(exc)}'
            )
            status[dimension_name] = {
                'error': msg,
                'status': 'failed'
            }
            log.error(msg)

    return status


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
        return "{}"

    return value

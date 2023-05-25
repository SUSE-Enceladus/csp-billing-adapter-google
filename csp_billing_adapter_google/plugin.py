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

@csp_billing_adapter.hookimpl
def setup_adapter(config: Config):
    pass


@csp_billing_adapter.hookimpl(trylast=True)
def meter_billing(
    config: Config,
    dimensions: dict,
    timestamp: str,
    dry_run: bool
):
    pass


@csp_billing_adapter.hookimpl(trylast=True)
def get_csp_name(config: Config):
    return 'google'


@csp_billing_adapter.hookimpl(trylast=True)
def get_account_info(config: Config):
    """
    Return a dictionary with account information

    The information contains the cloud provider
    and the metadata for instance and project.
    """
    account_info = _get_metadata()
    account_info['cloud_provider'] = get_csp_name(config)

def _get_metadata():
    """
    Return a dictionary with account information

    The information contains the metadata for instance and project.
    """
    metadata = {}
    metadata['instance'] = _get_instance_metadata()
    metadata['project'] = _get_project_metadata()
    return metadata

def _get_instance_metadata():
    """
    Return a dictionary with instance metadata information

    The information contains the metadata for name, license,
    id, image and zone.
    """
    metadata_options = ['name', 'license', 'id', 'image', 'zone']
    metadata = {}
    for metadata_option in metadata_options:
        uri = 'instance/'
        if metadata_option not in ['license']:
           uri += metadata_option
        else:
            if metadata_option in ['license']:
                uri += 'licenses/0/id'

        metadata[metadata_option] = _fetch_metadata(uri)
    return metadata

def _get_project_metadata():
    """
    Return a dictionary with project metadata information

    The information contains the metadata for numeric project id and project-id.
    """
    metadata_options = ['numeric-project-id', 'project-id']
    metadata = {}
    for metadata_option in metadata_options:
        metadata[metadata_option] = _fetch_metadata('project/' + metadata_option)
    return metadata

def _fetch_metadata(uri):
    """Return the response of the metadata request."""
    url = METADATA_ADDR + url
    data_request = urllib.request.Request(url, headers=METADATA_HEADERS)
    try:
        value = urllib.request.urlopen(data_request).read()
    except urllib.error.URLError:
        return None

    return value

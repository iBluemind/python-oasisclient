# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from keystoneauth1.exceptions import catalog
from keystoneauth1 import session as ksa_session
import os_client_config

DEFAULT_SERVICE_TYPE = 'oasis'

class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, magnum_url=None,
                 endpoint_type=None, endpoint_override=None,
                 service_type=DEFAULT_SERVICE_TYPE,
                 region_name=None, input_auth_token=None,
                 session=None, password=None, auth_type='password',
                 interface=None, service_name=None, insecure=False,
                 user_domain_id=None, user_domain_name=None,
                 project_domain_id=None, project_domain_name=None,
                 auth_token=None, timeout=600, **kwargs):

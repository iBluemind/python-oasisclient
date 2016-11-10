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

from keystoneauth1 import loading
from keystoneauth1.exceptions import catalog
from keystoneauth1 import session as ksa_session
import os_client_config

from oasisclient.v1 import functions
from oasisclient.common import httpclient
from oasisclient.v1 import policy
from oasisclient.v1 import nodepool
from oasisclient.v1 import nodepoolpolicy
from oasisclient.v1 import endpoint
from oasisclient.v1 import httpapi
from oasisclient.v1 import request
from oasisclient.v1 import requestheader
from oasisclient.v1 import response
from oasisclient.v1 import responsecode
from oasisclient.v1 import responsemessage

DEFAULT_SERVICE_TYPE = 'oasis'
LEGACY_DEFAULT_SERVICE_TYPE = 'oasis'

import logging
LOG = logging.getLogger(__name__)


class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, oasis_url=None,
                 endpoint_type=None, service_type='function',
                 region_name=None, input_auth_token=None,
                 session=None, password=None, auth_type='password',
                 interface='public', service_name=None, insecure=False,
                 user_domain_id=None, user_domain_name=None,
                 project_domain_id=None, project_domain_name=None):

        # We have to keep the api_key are for backwards compat, but let's
        # remove it from the rest of our code since it's not a keystone
        # concept
        if not password:
            password = api_key
        # Backwards compat for people assing in endpoint_type
        if endpoint_type:
            interface = endpoint_type

        if oasis_url and input_auth_token:
            auth_type = 'admin_token'
            session = None
            loader_kwargs = dict(
                token=input_auth_token,
                endpoint=oasis_url)

        elif input_auth_token and not session:
            auth_type = 'token'
            loader_kwargs = dict(
                token=input_auth_token,
                auth_url=auth_url,
                project_id=project_id,
                project_name=project_name,
                user_domain_id=user_domain_id,
                user_domain_name=user_domain_name,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name)

            print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
            print loader_kwargs
        else:
            loader_kwargs = dict(
                username=username,
                password=password,
                auth_url=auth_url,
                project_id=project_id,
                project_name=project_name,
                user_domain_id=user_domain_id,
                user_domain_name=user_domain_name,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name)

        # Backwards compatibility for people not passing in Session
        if session is None:
            loader = loading.get_plugin_loader(auth_type)

            # This should be able to handle v2 and v3 Keystone Auth
            auth_plugin = loader.load_from_options(**loader_kwargs)
            session = ksa_session.Session(
                auth=auth_plugin, verify=(not insecure))

        client_kwargs = {}
        if oasis_url:
            client_kwargs['endpoint_override'] = oasis_url

        if not oasis_url:
            try:
                # Trigger an auth error so that we can throw the exception
                # we always have
                session.get_endpoint(
                    service_type=service_type,
                    service_name=service_name,
                    interface=interface,
                    region_name=region_name)
            except Exception:
                raise RuntimeError("Not Authorized")

        self.http_client = httpclient.SessionClient(
            service_type=service_type,
            service_name=service_name,
            interface=interface,
            region_name=region_name,
            session=session,
            **client_kwargs)

        self.function = functions.FunctionManager(self.http_client)
        self.policy = policy.PolicyManager(self.http_client)
        self.nodepool = nodepool.NodePoolManager(self.http_client)
        self.nodepool_policy = nodepoolpolicy.NodePoolPolicyManager(self.http_client)
        self.endpoint = endpoint.EndpointManager(self.http_client)
        self.request = request.RequestManager(self.http_client)
        self.request_header = requestheader.RequestHeaderManager(self.http_client)
        self.response = response.ResponseManager(self.http_client)
        self.response_code = responsecode.ResponseCodeManager(self.http_client)
        self.httpapi = httpapi.HttpApiManager(self.http_client)
        self.response_message = responsemessage.ResponseMessageManager(self.http_client)

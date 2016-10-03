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

from oasisclient.v1 import functions
from oasisclient.common import httpclient
from oasisclient.v1 import policy
from oasisclient.v1 import nodepool
from oasisclient.v1 import nodepoolpolicy


DEFAULT_SERVICE_TYPE = 'oasis'
LEGACY_DEFAULT_SERVICE_TYPE = 'oasis'

def _load_session(cloud=None, insecure=False, timeout=None, **kwargs):
    cloud_config = os_client_config.OpenStackConfig()
    cloud_config = cloud_config.get_one_cloud(
        cloud=cloud,
        verify=not insecure,
        **kwargs)
    verify, cert = cloud_config.get_requests_verify_args()

    auth = cloud_config.get_auth()
    session = ksa_session.Session(
        auth=auth, verify=verify, cert=cert,
        timeout=timeout)

    return session


def _load_service_type(session,
                       service_type=None, service_name=None,
                       interface=None, region_name=None):
    try:
        # Trigger an auth error so that we can throw the exception
        # we always have
        session.get_endpoint(
            service_type=service_type,
            service_name=service_name,
            interface=interface,
            region_name=region_name)
    except catalog.EndpointNotFound:
        service_type = LEGACY_DEFAULT_SERVICE_TYPE
        try:
            session.get_endpoint(
                service_type=service_type,
                service_name=service_name,
                interface=interface,
                region_name=region_name)
        except Exception as e:
            raise RuntimeError(str(e))
    except Exception as e:
        raise RuntimeError(str(e))

    return service_type



class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, oasis_url=None,
                 endpoint_type=None, endpoint_override=None,
                 service_type=DEFAULT_SERVICE_TYPE,
                 region_name=None, input_auth_token=None,
                 session=None, password=None, auth_type='password',
                 interface=None, service_name=None, insecure=False,
                 user_domain_id=None, user_domain_name=None,
                 project_domain_id=None, project_domain_name=None,
                 auth_token=None, timeout=600, **kwargs):

        if not session:
            if auth_token:
                auth_type = 'token'
            session = _load_session(
                username=username,
                project_id=project_id,
                project_name=project_name,
                auth_url=auth_url,
                password=password,
                auth_type=auth_type,
                insecure=insecure,
                user_domain_id=user_domain_id,
                user_domain_name=user_domain_name,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name,
                auth_token=auth_token,
                timeout=timeout,
                **kwargs
            )


        # fix (yolanda): os-cloud-config is using endpoint_override
        # instead of magnum_url
        if oasis_url and not endpoint_override:
            endpoint_override = oasis_url

        self.http_client = httpclient.SessionClient(
            service_type=service_type,
            service_name=service_name,
            interface=interface,
            region_name=region_name,
            session=session,
            endpoint_override=endpoint_override,
        )

        self.function = functions.FunctionManager(self.http_client)
        self.policy = policy.PolicyManager(self.http_client)
        self.nodepool = nodepool.NodePoolManager(self.http_client)
        self.nodepool_policy = nodepoolpolicy.NodePoolPolicyManager(self.http_client)
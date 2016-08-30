from __future__ import print_function

import collections
import json
import os
import re
import shutil
import sys
import tempfile
import textwrap
import uuid
import warnings
import zipfile

from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import encodeutils
from oslo_utils import importutils
import prettytable
import requests
import six
from six.moves import urllib
import yaml

from oasisclient.i18n import _


def arg(*args, **kwargs):
    """Decorator for CLI args."""

    def _decorator(func):
        if not hasattr(func, 'arguments'):
            func.arguments = []

        if (args, kwargs) not in func.arguments:
            func.arguments.insert(0, (args, kwargs))

        return func

    return _decorator


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


def isunauthenticated(func):
    """Checks if the function does not require authentication.

    Mark such functions with the `@unauthenticated` decorator.

    :returns: bool
    """
    return getattr(func, 'unauthenticated', False)

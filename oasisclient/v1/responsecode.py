from oasisclient.common import base
from oasisclient.common import utils

import logging

LOG = logging.getLogger(__name__)


class ResponseCode(base.Resource):
    def __repr__(self):
        return "<ResponseCodes %s>" % self._info


class ResponseCodeManager(base.Manager):
    resource_class = ResponseCode

    @staticmethod
    def _path(id=None):
        return '/v1/responsecodes/%s' % id if id else '/v1/responsecodes'

    def list(self, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False):
        """Retrieve a list of requests.
        :param marker: Optional, the UUID of a responsecode, eg the last
                       responsecodes from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of responsecodes to return.
            2) limit == 0, return the entire list of responsecodes.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Oasis API
               (see Magnum's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about responsecodes.

        :returns: A list of responsecodes.
        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(marker, limit, sort_key, sort_dir)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "responsecodes")
        else:
            return self._list_pagination(self._path(path), "responsecodes", limit=limit)

    def create(self, **param):
        LOG.debug('create!!!!!')
        return self._create(self._path(), param)

    def get(self, id):
        try:
            return self._list(self._path(id))[0]
        except IndexError:
            return None

    def delete(self, id):
        return self._delete(self._path(id))

    def update(self, id, patch):
        return self._update(self._path(id), patch)

    def test(self):
        try:
            return self._test('/')
        except Exception:
            return 'Test Connect Error'

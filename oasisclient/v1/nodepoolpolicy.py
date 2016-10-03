from oasisclient.common import base
from oasisclient.common import utils


class NodePoolPolicy(base.Resource):
    def __repr__(self):
        return "<NodePool %s>" % self._info


class NodePoolPolicyManager(base.Manager):
    resource_class = NodePoolPolicy

    @staticmethod
    def _path(id=None):
        return '/v1/nodepoolpolicy/%s' % id if id else '/v1/nodepoolpolicy'

    def list(self, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False):
        """Retrieve a list of bays.
        :param marker: Optional, the UUID of a bay, eg the last
                       bay from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of bays to return.
            2) limit == 0, return the entire list of bays.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Magnum API
               (see Magnum's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about bays.

        :returns: A list of bays.
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
            return self._list(self._path(path), "nodepoolpolicy")
        else:
            return self._list_pagination(self._path(path), "nodepoolpolicy", limit=limit)

    def create(self, **param):
        return self._create(self._path(), param)

    def get(self, id):
        try:
            return self._list(self._path(id))[0]
        except IndexError:
            return None

    def update(self, id, param):
        try:
            return self._update(self._path(id), param)
        except IndexError:
            return None

    def test(self):
        try:
            return self._test('/')
        except Exception :
            return 'Test Connect Error'

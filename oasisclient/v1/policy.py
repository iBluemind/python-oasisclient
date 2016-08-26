from oasisclient.common import base

class Policy(base.Resource):
    def __repr__(self):
        return "<Policy %s>" % self._info


class PolicyManager(base.Manager):
    resource_class = Policy

    @staticmethod
    def _path(id=None):
        return '/v1/policy/%s' % id if id else '/v1/policy'

    def get(self):
        try:
            return self._list(self._path())[0]
        except IndexError:
            return None

    def update(self, **param):
        return self._update(self._path(), param)
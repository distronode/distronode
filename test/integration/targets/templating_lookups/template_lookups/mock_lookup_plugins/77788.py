from __future__ import annotations

from distronode.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        return {'one': 1, 'two': 2}

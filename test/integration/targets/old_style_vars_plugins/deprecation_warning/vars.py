from __future__ import annotations

from distronode.plugins.vars import BaseVarsPlugin


class VarsModule(BaseVarsPlugin):
    REQUIRES_WHITELIST = True

    def get_vars(self, loader, path, entities):
        return {}

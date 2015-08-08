""" Support cache in Muffin framework. """

import asyncio

from muffin.plugins import BasePlugin, PluginException


class Plugin(BasePlugin):

    """ Cache Plugin. """

    name = 'cache'
    defaults = {
        'lifetime': 60 * 30
    }

    def __init__(self, *args, **kwargs):
        """ Initialize the Plugin. """
        super().__init__(*args, **kwargs)

    def setup(self, app):
        """ Setup self. """
        super().setup(app)

    @asyncio.coroutine
    def start(self, app):
        """ Start plugin. """
        if 'redis' not in app.ps:
            raise PluginException(
                'muffin-cache required muffin-redis package.'
                'use pip install muffin-redis to install'
            )

    def finish(self, app):
        """ Finish plugin. """
        pass

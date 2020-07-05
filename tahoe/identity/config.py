"""InputConfig Class."""

if __name__ != 'tahoe.identity.config':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
    
from tahoe import Attribute, Object


class InputConfig(Object):  
    def __init__(self, plugin, name, typetag, orgid, timezone,
                 data=None, **kwargs):
        plugin = Attribute('plugin', plugin, _backend=self._backend)
        """plugin_name"""
        name = Attribute('name', name, _backend=self._backend)
        """human_name"""
        typetag = Attribute('typetag', typetag, _backend=self._backend)
        """archive_processing_typetag"""
        orgid = Attribute('orgid', orgid, _backend=self._backend)
        timezone = Attribute('timezone', timezone, _backend=self._backend)

        if not data:
            data=[]
        elif not isinstance(data, list):
            data = [data]
        data = data + [plugin, name, typetag, orgid, timezone]

        super().__init__('cybexp_input_config', data, **kwargs)


class WebSocketConfig(InputConfig):
    def __init__(self, name, typetag, orgid, timezone, url, **kwargs):
        data = Attribute('url', url)  # future work: check for valid url
        super().__init__('websocket', name, typetag, orgid, timezone,
                         data, **kwargs)


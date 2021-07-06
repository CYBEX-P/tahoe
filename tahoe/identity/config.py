"""InputConfig Class."""

if __name__ != 'tahoe.identity.config':
    import sys, os
    sys.path = ['..', os.path.join('..', '..')] + sys.path
    del sys, os
    
from tahoe import Attribute, Object


class InputConfig(Object):  
    def __init__(self, plugin, name, typetag, orgid, timezone,
                 data=None, enabled=True, **kwargs):
        if "_backend" in kwargs:
            self._backend = kwargs.pop("_backend")
        plugin = Attribute('plugin', plugin, _backend=self._backend)
        """plugin_name"""
        name = Attribute('name', name, _backend=self._backend)
        """human_name"""
        typetag = Attribute('typetag', typetag, _backend=self._backend)
        """archive_processing_typetag"""
        orgid = Attribute('orgid', orgid, _backend=self._backend)
        timezone = Attribute('timezone', timezone, _backend=self._backend)

        assert enabled in [True, False]
        enabled = Attribute('enabled', enabled, _backend=self._backend)

        if not data:
            data=[]
        elif not isinstance(data, list):
            data = [data]
        data = data + [plugin, name, typetag, orgid, timezone, enabled]

        super().__init__('cybexp_input_config', data, **kwargs)

    @property
    def status(self):
        return self.data['enabled'][0] 
    
    def disable(self):
        if self.status == True:
            ae = Attribute("enabled", True, _backend=self._backend)
            ad = Attribute("enabled", False, _backend=self._backend)
            self.edit(add_data=ad, remove_data=ae)

    def enable(self):
        if self.status == False:
            ae = Attribute("enabled", True, _backend=self._backend)
            ad = Attribute("enabled", False, _backend=self._backend)
            self.edit(add_data=ae, remove_data=ad)

class WebSocketConfig(InputConfig):
    def __init__(self, name, typetag, orgid, timezone, url,
                 enabled=True, **kwargs):
        data = Attribute('url', url, _backend=self._backend)
        super().__init__('websocket', name, typetag, orgid, timezone,
                         data, enabled, **kwargs)

        #check for ws:// (the protocol) in the url


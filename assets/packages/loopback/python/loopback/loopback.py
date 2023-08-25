# -*- mode: python; python-indent: 4 -*-
import ipaddress
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')') # pylint: disable=protected-access

        ip_prefix = service.ip_prefix
        self.log.debug(f'Value of ip-prefix leaf is {ip_prefix}')
        net = ipaddress.IPv4Network(ip_prefix)
        ip_address = next(net.hosts())

        tvars = ncs.template.Variables()
        tvars.add('IP_ADDRESS', ip_address)
        template = ncs.template.Template(service)
        template.apply('loopback-template', tvars)


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Loopback(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Loopback RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('loopback-servicepoint', ServiceCallbacks)

# -*- mode: python; python-indent: 4 -*-
import ipaddress
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        ip_address = self.calculate_ip_address(service.ip_prefix)
        gateway_address = self.calculate_ip_address(service.gateway_prefix)
        vars = ncs.template.Variables()
        vars.add('IP_ADDRESS', ip_address)
        vars.add('GATEWAY_ADDRESS', gateway_address)
        template = ncs.template.Template(service)
        template.apply('loopback-template', vars)

    def calculate_ip_address(self, prefix):
        self.log.debug(f'Value of prefix leaf is {prefix}')
        net = ipaddress.IPv4Network(prefix)
        return str(next(net.hosts()))


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

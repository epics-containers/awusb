"""
A class for discovering which local usbip ports are in use and detaching from
those that match the user search criteria.

"""
import re
from awusb.utility import run_command

# regex pattern for matching 'usbip port' output https://regex101.com/r/YphHXi/1
re_ports = re.compile(r'/Port *(?P<port>\d\d)(?:.*\n) *(?P<description>.*) .*\((?P<id>[0-9a-f]{4}:[0-9a-f]{4})\)\n.*usbip:\/\/(?P<server>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}):\d*\/(?P<remote_busid>[1-9-.]*)\n', re.MULTILINE)

def list_ports():
    """Lists the local usbip ports in use.

    Returns:
        A list of dictionaries, each representing a port in use.
    """

    output = run_command(['usbip', 'port'], capture_output=True, text=True).stdout
    print (output)
    ports = []
    for match in re_ports.finditer(output):
        port_info = match.groupdict()
        port_info['port'] = int(port_info['port'])
        ports.append(port_info)
    print(ports)
    return ports

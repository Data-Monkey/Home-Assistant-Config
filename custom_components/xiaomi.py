"""
Support for Xiaomi Gateways.

Developed by Rave from Lazcad.com
"""
import socket
import json
import logging
import struct
import platform
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from threading import Thread
from collections import defaultdict
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.const import ATTR_BATTERY_LEVEL, EVENT_HOMEASSISTANT_STOP


REQUIREMENTS = ['pyCrypto==2.6.1']

DOMAIN = 'xiaomi'
CONF_GATEWAYS = 'gateways'
CONF_INTERFACE = 'interface'
CONF_DISCOVERY_RETRY = 'discovery_retry'
CONF_CHECK_GHOST = 'check_ghost'

DEFAULT_KEY = "xxxxxxxxxxxxxxxx"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_GATEWAYS, default=[{"sid": None, "key": DEFAULT_KEY}]): cv.ensure_list,
        vol.Optional(CONF_INTERFACE, default='any'): cv.string,
        vol.Optional(CONF_CHECK_GHOST, default=False): cv.boolean,
        vol.Optional(CONF_DISCOVERY_RETRY, default=3): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)

XIAOMI_COMPONENTS = ['binary_sensor', 'sensor', 'switch', 'light']
PY_XIAOMI_GATEWAY = None

# Shortcut for the logger
_LOGGER = logging.getLogger(__name__)

ATTR_RINGTONE_ID = 'ringtone_id'
ATTR_GW_SID = 'gw_sid'
ATTR_RINGTONE_VOL = 'ringtone_vol'

def setup(hass, config):
    """Set up the Xiaomi component."""

    gateways = config[DOMAIN][CONF_GATEWAYS]
    interface = config[DOMAIN][CONF_INTERFACE]
    discovery_retry = config[DOMAIN][CONF_DISCOVERY_RETRY]
    check_ghost = config[DOMAIN][CONF_CHECK_GHOST]

    for gateway in gateways:
        sid = gateway['sid']

        if sid != None:
            gateway['sid'] = gateway['sid'].replace(":", "").lower()

        key = gateway['key']
        if key == DEFAULT_KEY:
            _LOGGER.warning('Gateway Key is not provided. Controlling gateway device will not be possible.')

        if len(key) != 16:
            _LOGGER.error('Invalid key %s. Key must be 16 characters', key)
            return False

    global PY_XIAOMI_GATEWAY
    PY_XIAOMI_GATEWAY = PyXiaomiGateway(hass, gateways, interface, check_ghost)

    _LOGGER.info("Expecting %s gateways", len(gateways))
    for _ in range(discovery_retry):
        _LOGGER.info('Discovering Xiaomi Gateways (Try %s)', _ + 1)
        PY_XIAOMI_GATEWAY.discover_gateways()
        if len(PY_XIAOMI_GATEWAY.gateways) >= len(gateways):
            break

    if len(PY_XIAOMI_GATEWAY.gateways) == 0:
        _LOGGER.error("No gateway discovered")
        return False

    PY_XIAOMI_GATEWAY.listen()
    _LOGGER.info("Listening for broadcast")

    def stop_xiaomi(event):
        """Stop Xiaomi Socket."""
        _LOGGER.info("Shutting down Xiaomi Hub.")
        PY_XIAOMI_GATEWAY.stop_listen()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_xiaomi)

    for component in XIAOMI_COMPONENTS:
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    
    def play_ringtone_service(call):
        """Service to play ringtone through Gateway."""
        if call.data.get(ATTR_RINGTONE_ID) is None or call.data.get(ATTR_GW_SID) is None:
           _LOGGER.error("Mandatory parameters is not specified.")
           return

        ring_id = int(call.data.get(ATTR_RINGTONE_ID))
        
        if ring_id in [9, 14-19]:
            _LOGGER.error('Specified mid: %s is not defined in gateway.', mid)
            return
        
        ring_vol = call.data.get(ATTR_RINGTONE_VOL)
        if ring_vol is None:
            ringtone = {'mid': ring_id}
        else:
            ringtone = {'mid': ring_id, 'vol': int(ring_vol)}

        gw_sid = call.data.get(ATTR_GW_SID) 

        gateways = PY_XIAOMI_GATEWAY.gateways
        for (ip_add, gateway) in gateways.items():
            if gateway.sid == gw_sid:
               gateway.write_to_hub(gateway.sid, **ringtone )
               break
        else:
            _LOGGER.error('Unknown gateway sid: %s was specified.', gw_sid)

    def stop_ringtone_service(call):
        """Service to stop playing ringtone on Gateway."""
        gw_sid = call.data.get(ATTR_GW_SID)
        if gw_sid is None:
           _LOGGER.error("Mandatory parameters is not specified.")
           return
                
        gateways = PY_XIAOMI_GATEWAY.gateways
        for (ip_add, gateway) in gateways.items():
            if gateway.sid == gw_sid:
               ringtone = {'mid': 10000}
               gateway.write_to_hub(gateway.sid, **ringtone )
               break
        else:
            _LOGGER.error('Unknown gateway sid: %s was specified.', gw_sid)

    hass.services.async_register(DOMAIN, 'play_ringtone', play_ringtone_service, description=None, schema=None)
    hass.services.async_register(DOMAIN, 'stop_ringtone', stop_ringtone_service, description=None, schema=None)

    return True


class PyXiaomiGateway:
    """PyXiami."""
    MULTICAST_ADDRESS = '224.0.0.50'
    MULTICAST_PORT = 9898
    GATEWAY_DISCOVERY_PORT = 4321
    SOCKET_BUFSIZE = 1024

    gateways = defaultdict(list)

    def __init__(self, hass, gateways_config, interface, check_ghost):

        self.hass = hass
        self._listening = False
        self._mcastsocket = None
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if interface != 'any':
            self._socket.bind((interface, 0))

        self._threads = []
        self._gateways_config = gateways_config
        self._interface = interface
        self.check_ghost = check_ghost

    def discover_gateways(self):
        """Discover gateways using multicast"""

        _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self._interface != 'any':
            _socket.bind((self._interface, 0))

        try:
            _socket.sendto('{"cmd":"whois"}'.encode(),
                           (self.MULTICAST_ADDRESS, self.GATEWAY_DISCOVERY_PORT))

            _socket.settimeout(5.0)

            while True:
                data, addr = _socket.recvfrom(1024)
                if len(data) is None:
                    continue

                resp = json.loads(data.decode())
                if resp["cmd"] != 'iam':
                    _LOGGER.error("Response does not match return cmd")
                    continue

                if resp["model"] != 'gateway':
                    _LOGGER.error("Response must be gateway model")
                    continue

                ip_add = resp["ip"]
                if ip_add in self.gateways:
                    continue

                gateway_key = ''
                for gateway in self._gateways_config:
                    sid = gateway['sid']
                    key = gateway['key']
                    if sid is None or sid == resp["sid"]:
                        gateway_key = key

                sid = resp["sid"]
                port = resp["port"]

                _LOGGER.info('Xiaomi Gateway %s found at IP %s', sid, ip_add)

                self.gateways[ip_add] = XiaomiGateway(ip_add, port, sid, gateway_key, self._socket, self.check_ghost)

        except socket.timeout:
            _LOGGER.info("Gateway finding finished in 5 seconds")
            _socket.close()

    def _create_mcast_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if self._interface != 'any':
            if platform.system() != "Windows":
                sock.bind((self.MULTICAST_ADDRESS, self.MULTICAST_PORT))
            else:
                sock.bind((self._interface, self.MULTICAST_PORT))

            mreq = socket.inet_aton(self.MULTICAST_ADDRESS) + socket.inet_aton(self._interface)
        else:
            sock.bind((self.MULTICAST_ADDRESS, self.MULTICAST_PORT))
            mreq = struct.pack("4sl", socket.inet_aton(self.MULTICAST_ADDRESS), socket.INADDR_ANY)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return sock

    def listen(self):
        """Start listening."""

        _LOGGER.info('Creating Multicast Socket')
        self._mcastsocket = self._create_mcast_socket()
        self._listening = True
        thread = Thread(target=self._listen_to_msg, args=())
        self._threads.append(thread)
        thread.daemon = True
        thread.start()

    def stop_listen(self):
        """Stop listening."""
        self._listening = False

        if self._socket is not None:
            _LOGGER.info('Closing socket')
            self._socket.close()
            self._socket = None

        if self._mcastsocket is not None:
            _LOGGER.info('Closing multisocket')
            self._mcastsocket.close()
            self._mcastsocket = None

        for thread in self._threads:
            thread.join()

    def _listen_to_msg(self):
        while self._listening:
            if self._mcastsocket is None:
                continue
            data, (ip_add, port) = self._mcastsocket.recvfrom(self.SOCKET_BUFSIZE)
            try:
                data = json.loads(data.decode("ascii"))
                gateway = self.gateways.get(ip_add)
                if gateway is None:
                    _LOGGER.error('Unknown gateway ip %s', ip_add)
                    continue

                cmd = data['cmd']
                if cmd == 'heartbeat' and data['model'] == 'gateway':
                    gateway.token = data['token']
                elif cmd == 'report' or cmd == 'heartbeat':
                    _LOGGER.debug('MCAST (%s) << %s', cmd, data)
                    self.hass.add_job(gateway.push_data, data)

                else:
                    _LOGGER.error('Unknown multicast data : %s', data)
            except Exception:
                _LOGGER.error('Cannot process multicast message : %s', data)
                continue

class XiaomiGateway:
    """Xiaomi Gateway Component"""

    def __init__(self, ip, port, sid, key, sock, check_ghost):

        self.ip_add = ip
        self.port = int(port)
        self.sid = sid
        self.key = key
        self.devices = defaultdict(list)
        self.ha_devices = defaultdict(list)
        self.token = None
        self.check_ghost = check_ghost
        self._socket = sock

        trycount = 5
        for _ in range(trycount):
            _LOGGER.info('Discovering Xiaomi Devices')
            if self._discover_devices():
                break

    def _discover_devices(self):

        cmd = '{"cmd" : "get_id_list"}'
        resp = self._send_cmd(cmd, "get_id_list_ack")
        if resp is None or "token" not in resp or "data" not in resp:
            return False
        self.token = resp['token']
        sids = json.loads(resp["data"])
        sids.append(self.sid)

        _LOGGER.info('Found %s devices', len(sids))

        sensors = ['sensor_ht']
        binary_sensors = ['magnet', 'motion', 'switch', '86sw1', '86sw2', 'cube', 'smoke', 'natgas']
        switches = ['plug', 'ctrl_neutral1', 'ctrl_neutral2']
        gateway = ['gateway']

        for sid in sids:
            cmd = '{"cmd":"read","sid":"' + sid + '"}'
            resp = self._send_cmd(cmd, "read_ack")
            if resp is None:
                continue
            data = json.loads(resp["data"])
            if "error" in data:
                _LOGGER.error("Not a device")
                continue

            model = resp["model"]
            device_type = None
            if model in sensors:
                device_type = 'sensor'
            elif model in binary_sensors:
                device_type = 'binary_sensor'
            elif model in switches:
                device_type = 'switch'
            elif model in gateway:
                device_type = 'gateway'
            else:
                _LOGGER.error('Unsupported devices : %s', model)
                continue

            xiaomi_device = {
                "model":model,
                "sid":resp["sid"],
                "short_id":resp["short_id"],
                "data":data}
            if device_type == 'gateway':
               self.devices['light'].append(xiaomi_device)
               self.devices['sensor'].append(xiaomi_device)
            else:
                self.devices[device_type].append(xiaomi_device)
        return True

    def _send_cmd(self, cmd, rtn_cmd):
        try:
            self._socket.settimeout(10.0)
            _LOGGER.debug(">> %s", cmd.encode())
            self._socket.sendto(cmd.encode(), (self.ip_add, self.port))
            data, addr = self._socket.recvfrom(1024)
        except socket.timeout:
            _LOGGER.error("Cannot connect to Gateway")
            return None
        if data is None:
            _LOGGER.error("No response from Gateway")
            return None
        resp = json.loads(data.decode())
        _LOGGER.debug("<< %s", resp)
        if resp['cmd'] != rtn_cmd:
            _LOGGER.error("Non matching response. Expecting %s, but got %s", rtn_cmd, resp['cmd'])
            return None
        return resp

    def write_to_hub(self, sid, **kwargs):
        """Send data to gateway to turn on / off device"""
        data = {}
        for key in kwargs:
            data[key] = kwargs[key]
        if self.token is None:
            return False
        data['key'] = self._get_key()
        cmd = {}
        cmd['cmd'] = 'write'
        cmd['sid'] = sid
        cmd['data'] = data
        cmd = json.dumps(cmd)
        resp = self._send_cmd(cmd, "write_ack")
        return self._validate_data(resp)

    def get_from_hub(self, sid):
        """Get data from gateway"""
        cmd = '{ "cmd":"read","sid":"' + sid + '"}'
        resp = self._send_cmd(cmd, "read_ack")
        return self.push_data(resp)

    def push_data(self, data):
        """Push data broadcasted from gateway to device"""
        if not self._validate_data(data):
            return False
        jdata = json.loads(data['data'])
        if jdata is None:
            return False
        sid = data['sid']
        for device in self.ha_devices[sid]:
            device.push_data(jdata)
        return True

    def _get_key(self):
        """Get key using token from gateway"""
        from Crypto.Cipher import AES
        print("here")
        init_vector = bytes(bytearray.fromhex('17996d093d28ddb3ba695a2e6f58562e'))
        encryptor = AES.new(self.key.encode(), AES.MODE_CBC, IV=init_vector)
        ciphertext = encryptor.encrypt(self.token.encode())
        return ''.join('{:02x}'.format(x) for x in ciphertext)

    def _validate_data(self, data):
        if data is None or "data" not in data:
            _LOGGER.error('No data in response from hub %s', data)
            return False
        if 'error' in data['data']:
            _LOGGER.error('Got error element in data %s', data['data'])
            return False
        return True

class XiaomiDevice(Entity):
    """Representation a base Xiaomi device."""

    def __init__(self, device, name, xiaomi_hub):
        """Initialize the xiaomi device."""
        self._sid = device['sid']
        self._name = '{}_{}'.format(name, self._sid)
        self.xiaomi_hub = xiaomi_hub        
        self.parse_data(device['data'])
        self._device_state_attributes = {}
        self.parse_voltage(device['data'])        
        xiaomi_hub.ha_devices[self._sid].append(self)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def should_poll(self):
        """Poll update device status"""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._device_state_attributes

    def push_data(self, data):
        """Push from Hub"""
        _LOGGER.debug("PUSH >> %s: %s", self, data)

        if self.parse_data(data) or self.parse_voltage(data):
            self.schedule_update_ha_state()

    def parse_voltage(self, data):
        if 'voltage' not in data:
            return False

        max_volt = 3300
        min_volt = 2800
        voltage = data['voltage']
        voltage = min(voltage, max_volt)
        voltage = max(voltage, min_volt)
        percent = ((voltage - min_volt) / (max_volt - min_volt)) * 100
        self._device_state_attributes[ATTR_BATTERY_LEVEL] = round(percent)
        return True
            
    def parse_data(self, data):
        """Parse data sent by gateway"""
        raise NotImplementedError()

import gatt

from argparse import ArgumentParser


class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()
        print("[%s] Resolved services" % (self.mac_address))
#        for service in self.services:
#           print("\n\nService [%s] [%s]" % (service.uuid, service._path))
#           for characteristic in service.characteristics:
#               print("Characteristic [%s] [%s]"  % (characteristic.uuid, characteristic._path))

    def descriptor_read_value_failed(self, descriptor, error):
        print('descriptor_value_failed')


arg_parser = ArgumentParser(description="GATT Connect Demo")
arg_parser.add_argument('mac_address', help="MAC address of device to connect")
args = arg_parser.parse_args()

manager = gatt.DeviceManager(adapter_name='hci0')
device = AnyDevice(manager=manager, mac_address=args.mac_address)
print("Devicepath", device._device_path)

print("Connecting...")
device.connect()


battery_service = gatt.Service(device, device._device_path + '/service0014', "0000180a-0000-1000-8000-00805f9b34fb", )
battery_char = gatt.Characteristic(battery_service, battery_service._path + "/char0019", "00001500-0000-1000-8000-00805f9b34fb", )

#print("service [%s] path [%s]" % (battery_service.uuid, battery_service._path))
#print("char [%s] path [%s]" % (battery_char.uuid, battery_cat._path))
value = battery_char.read_value()
print("Raw value: ", value)
print("Battery bytevalue:%s" % [bytes([v]) for v in value])
print("Battery integer value:%s" % [int(v) for v in value])


manager.run()


from abc import ABC, abstractmethod
from screen_recorder.entities import Device, Size
import os
import pathlib
import time
from screen_recorder import utils

def create_handler(platform_name):
    """
    Creates the implementation of DeviceHandler corresponding to the provided
    platform name, or None if no corresponding DeviceHandler exists.

    Args:
        platform_name (string): The platform name for which to create a handler.
            This can be 'android' or 'ios'.

    Returns:
        DeviceHandler: A DeviceHandler or None
    """
    if platform_name == 'ios':
        return iOSDeviceHandler()
    elif platform_name == 'android':
        return AndroidDeviceHandler()
    else:
        return None

class DeviceHandler(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def list_devices(self):
        """
        Lists the available devices for the current platform.
        
        Returns:
            array: An array of Device
        """
        pass

    @abstractmethod
    def get_available_recording_resolutions(self, device, fractions):
        """
        Returns the screen resolutions in which the selected device can be recorded.

        Args:
            device (Device): The Device that the user selected
            fractions (array): A float array describing the relative sizes to use

        Returns:
            array: An array of Size with the same length as fractions
        """
        pass

    @abstractmethod
    def perform_screen_recording(self, device):
        pass

    def record_screen(self, device):
        """
        Performs the screen recording for the selected device.

        Args:
            device (Device): The Device that the user selected

        Returns:
            string: The file path used to store the recording
        """
        print(f'🎥 Started recording! Press Control-C to stop …')
        destination = self.perform_screen_recording(device)

        print('')
        print('👍 Recording completed')
        time.sleep(0.3)

        print('⏳ Converting video to GIF …')
        time.sleep(1)

        return destination

class iOSDeviceHandler(DeviceHandler):

    def __init__(self):
        pass

    def list_devices(self):
        output, _ = utils.run_command(['xcrun', 'simctl', 'list'])
        lines = output.split('\n')
        booted_devices = [line for line in lines if 'Booted' in line]
        devices = [self._create_device_from_line(line) for line in booted_devices]
        return devices

    def _create_device_from_line(self, text):
        components = utils.get_components_in_parentheses(text)
        while 'Booted' in components:
            components.remove('Booted')

        name = text.split('(')[0]

        if utils.is_not_uuid(components[0]):
            # Append this to the name
            name += f"({components[0]})"

        uuid = utils.get_uuid(components[-1])
        return Device(id=uuid, name=name.strip())

    def get_available_recording_resolutions(self, device, fractions):
        output, _ = utils.run_command(['xcrun', 'simctl', 'io', device.id, 'enumerate'])
        return self._parse_available_sizes(output, fractions)

    def _parse_available_sizes(self, output, fractions):
        sections = output.split('\n\n')
        display_sections = list(filter(lambda x: 'Class: Display' in x and 'Display class: 0' in x, sections))

        if not display_sections:
            return []

        lines = display_sections[0].split('\n')
        width_lines = list(filter(lambda x: 'Default width' in x, lines))
        height_lines = list(filter(lambda x: 'Default height' in x, lines))

        if not width_line or not height_line:
            return []
        
        width = int(width_lines[0].split(': ')[1])
        height = int(height_lines[0].split(': ')[1])

        size = Size(width=width, height=height)
        sizes = list(map(lambda fraction: size.scale(factor=fraction), fractions))
        return sizes

    def perform_screen_recording(self, device):
        home = str(pathlib.Path.home())
        timestamp = int(time.time())
        destination = f'{home}/Desktop/recording_{timestamp}.mp4'

        record_command = ['xcrun', 'simctl', 'io', device.id, 'recordVideo', destination]
        utils.wait_for_screen_recording(record_command)

        return destination


class AndroidDeviceHandler(DeviceHandler):

    def __init__(self):
        pass

    def _adb(self):
        try:
            return os.environ['ANDROID_HOME']
        except KeyError:
            raise RuntimeError('💩 Environment variable "ANDROID_HOME" not set. Please do that and try again.')

    def list_devices(self):
        adb = self._adb() + '/platform-tools/adb'
        output, _ = utils.run_command([adb, 'devices'])
        lines = output.split('\n')
        lines = list(filter(lambda line: not line.startswith('*'), lines))
        lines.pop(0) # remove the "List of devices attached" line
        options = [line for line in lines if line]
        devices = [option.split('\t')[0] for option in options]
        # For Android devices, the name is also the identifier
        return [Device(name=device, id=device) for device in devices]

    def get_available_recording_resolutions(self, device, fractions):
        adb = self._adb() + '/platform-tools/adb'
        command = [adb, '-s', device.name, 'shell', 'wm', 'size']
        output, _ = utils.run_command(command)
        return self._parse_available_sizes(output)

    def _parse_available_sizes(self, output):
        height, width = re.findall('\d+', output)
        size = Size(width=int(width), height=int(height))
        sizes = list(map(lambda fraction: size.scale(factor=fraction), fractions))
        return sizes

    def perform_screen_recording(self, device):
        timestamp = int(time.time())
        adb = self._adb() + '/platform-tools/adb'
        device_path = f'/sdcard/video_{timestamp}.mp4'

        record_command = [adb, '-s', device.name, 'shell', 'screenrecord', device_path]
        utils.wait_for_screen_recording(record_command)

        home = str(pathlib.Path.home())
        destination = f'{home}/Desktop/recording_{timestamp}.mp4'

        time.sleep(0.5)

        pull_command = [adb, '-s', device.name, 'pull', device_path, destination]
        utils.run_command(pull_command)

        time.sleep(1.0)

        remove_command = [adb, '-s', device.name, 'shell', 'rm', '-f', device_path]
        utils.run_command(remove_command)

        return destination

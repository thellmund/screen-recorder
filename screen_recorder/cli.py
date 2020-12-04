import enquiries
import click
import os

from screen_recorder.converter import VideoConverter
from screen_recorder.handler import create_handler

def select_device(devices):
    """
    Asks the user to select the desired device to record from the list of
    available devices.

    Args:
        devices (array): The list of available devices

    Returns:
        Device: The selected device, or None if none is available
    """
    if len(devices) == 0:
        return None
    elif len(devices) == 1:
        device = devices[0]
        print(f'📱 Selected {device.name}')
        return device
    else:
        device_names = [device.name for device in devices]
        selected_name = enquiries.choose('Choose a device:', device_names)
        print(f'📱 Selected {selected_name}')
        selected_index = device_names.index(selected_name)
        return devices[selected_index]

def select_resolution(resolutions):
    """
    Asks the user to select the desired resolution to record with.

    Args:
        resolutions (array): The list of available resolutions for the selected
            device

    Returns:
        Size: The selected resolution
    """
    formatted_sizes = [size.formatted() for size in resolutions]
    selected_size = enquiries.choose('Which resolution?', formatted_sizes)
    print(f'🆗 Selected {selected_size}')
    selected_index = formatted_sizes.index(selected_size)
    return resolutions[selected_index]

@click.command()
@click.argument('platform')
def main(platform):
    """
    Record the screen of an Android or iOS device as a GIF.

    Args:
        platform (string): The name of the platform for which to record the
            screen. Use 'ios' for an iOS device and 'android' for an Android 
            device.
    """

    converter = VideoConverter()
    path = None

    try:
        handler = create_handler(platform)
        if not handler:
            raise RuntimeError('👎 Invalid platform provided. Valid options are \'ios\' and \'android\'.')

        devices = handler.list_devices()
        device = select_device(devices)

        if not device:
            print('🤷 No device found')
            return

        resolutions = handler.get_available_recording_resolutions(device, fractions=[1.0, 0.8, 0.6])
        resolution = select_resolution(resolutions)

        path = handler.record_screen(device)
        converter.convert(path, resolution=resolution)
    except RuntimeError as runtime_error:
        print(runtime_error)
    except KeyboardInterrupt:
        if path:
            os.remove(path)
        print('❌ Aborted')

if __name__ =="__main__":
    main()

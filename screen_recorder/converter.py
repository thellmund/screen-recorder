import enquiries
from enum import Enum
import os
import pathlib
import time
from screen_recorder import utils

MAX_SIZE_FOR_GITHUB = 10 # Bytes

class Result(Enum):
    REPEAT_WITH_LOWER_FRAME_RATE = 1
    REPEAT_WITH_LOWER_RESOLUTION = 2
    KEEP_AS_IS = 3

class VideoConverter:

    def convert(self, source, resolution, frame_rate=30):
        destination = self._create_destination_path()
        command, destination = self._create_conversion_command(
            source=source,
            destination=destination,
            width=resolution.width,
            fps=frame_rate
        )
        stdout, stderr = utils.run_command(command)

        if stderr:
            raise RuntimeError(f'🤦 Something went wrong ({stderr})')

        size, result = self._determine_possible_repeat(destination)

        if result == Result.REPEAT_WITH_LOWER_FRAME_RATE:
            new_frame_rate = self._scale_frame_rate(size=size, current_fps=frame_rate)
            print(f'🔁 Trying again with {new_frame_rate} frames per second …')
            os.remove(destination)
            self.convert(source, resolution, new_frame_rate)
        elif result == Result.REPEAT_WITH_LOWER_RESOLUTION:
            new_resolution = self._scale_resolution(size=size, resolution=resolution)
            print(f'🔁 Trying again with resolution of {new_resolution.formatted()} …')
            os.remove(destination)
            self.convert(source, new_resolution, frame_rate)
        else:
            print('✅ Your GIF is ready. Rock on!')
            os.remove(source)

    def _determine_possible_repeat(self, destination):
        size_in_megabytes = os.path.getsize(destination) / 1_000_000
        if size_in_megabytes < 10:
            # Small enough to share on GitHub
            return size_in_megabytes, Result.KEEP_AS_IS

        options = [
            "Convert again with lower frame rate",
            "Convert again with lower resolution",
            "Keep as is"
        ]
        formatted_size = round(size_in_megabytes, 2)
        selected_option = enquiries.choose(f'The GIF ({formatted_size} MB) is too large to be shared on GitHub. What do you want to do?', options)
        selected_index = options.index(selected_option)

        if selected_index == 0:
            return size_in_megabytes, Result.REPEAT_WITH_LOWER_FRAME_RATE
        elif selected_index == 1:
            return size_in_megabytes, Result.REPEAT_WITH_LOWER_RESOLUTION
        else:
            return size_in_megabytes, Result.KEEP_AS_IS

    def _scale_frame_rate(self, size, current_fps):
        if size < (2 * MAX_SIZE_FOR_GITHUB):
            return int(current_fps * 0.75)
        elif size < (3 * MAX_SIZE_FOR_GITHUB):
            return int(current_fps * 0.67)
        else:
            return int(current_fps * 0.50)

    def _scale_resolution(self, size, resolution):
        if size < (2 * MAX_SIZE_FOR_GITHUB):
            return resolution.scale(0.8)
        elif size < (3 * MAX_SIZE_FOR_GITHUB):
            return resolution.scale(0.75)
        else:
            return resolution.scale(0.5)

    def _create_destination_path(self):
        home = str(pathlib.Path.home())
        timestamp = int(time.time())
        destination = f'{home}/Desktop/recording_{timestamp}.gif'
        return destination

    def _create_conversion_command(self, source, destination, width, fps):
        # TODO Consider landscape mode!
        fps = f'fps={fps}'
        scale = f'scale={width}:-1:flags=lanczos'
        palette = 'split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse'
        joined_args = ','.join([fps, scale, palette])

        command = [
            "ffmpeg",
            # overwrite any existing output file
            "-y",
            "-i",
            # the input file path
            source,
            "-vf",
            # the quality parameters
            f'{joined_args}',
            "-loglevel",
            # mute any crazy ffmpeg output
            "error",
            # the output file path
            destination
        ]
        return (command, destination)

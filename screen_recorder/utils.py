import re
import subprocess
import time

from uuid import UUID

def run_command(args):
    """
    Joins the provided arguments into a command and runs it.

    Args:
        args (array): The components of the command to run

    Returns:
        tuple: A tuple with the decoded output and any errors that occurred
    """
    command = ' '.join(args)
    out = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    return stdout.decode('utf-8'), stderr

def wait_for_screen_recording(args):
    """
    Joins the provided arguments into a command and runs it. Control is returned
    to the caller on KeyboardInterrupt.

    Args:
        args (array): The components of the command to run
    """
    try:
        run_command(args)
    except KeyboardInterrupt:
        pass

def is_not_uuid(text):
    """
    Returns whether the provided text is a valid UUID.

    Args:
        text (string): The text to validate
    """
    try:
        uuid = UUID(text, version=4)
        return False
    except ValueError:
        return True

def get_uuid(text):
    """
    Returns a UUID from the provided text if it's valid. Otherwise None.

    Args:
        text (string): The text to convert to a UUID
    """
    try:
        _ = UUID(text, version=4)
        return text
    except ValueError:
        return None

def get_components_in_parentheses(text):
    """
    Returns the substring within the parentheses in the provided text.
    """
    return re.findall('\((.*?)\)', text)

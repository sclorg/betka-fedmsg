import os
import json


class UchoError(RuntimeError):
    pass


def _get_package_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_certificates_path():
    return os.path.join(_get_package_path(), 'ucho', 'data', 'certificates')


def get_configuration_path():
    return os.path.join(_get_package_path(), 'ucho', 'data', 'configuration')


def pretty_dict(report_dict):
    result = json.dumps(report_dict, sort_keys=True, indent=4)
    result = result.replace('\\n', '\n')
    return result

from config.env import env


data = {
    'login': {
        'username': env('login.username'),
        'password': env('login.password'),
        'public_key': '0725@pwdorgopenp'
    }
}

def getter(data, parameters):
    if len(parameters) > 1:
        return getter(
            data[parameters[0]],
            parameters[1: len(parameters)]
        )
    else:
        return data[parameters[0]]

def config(name, default=None):
    params = parse_name(name)
    try:
        value = getter(data, params)
    except KeyError as e:
        return default
    finally:
        return value

def parse_name(name):
    parameters = name.split('.')

    if len(parameters) < 1:
        raise ConfigNameError('config name is invalid')

    return parameters


class ConfigNameError(Exception):
    pass

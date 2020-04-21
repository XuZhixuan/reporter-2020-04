import configparser


def env(name, default=None):
    parser = configparser.RawConfigParser()
    parser.read('.env')

    params = parse_name(name)

    value=None
    try:
        value = parser.get(params['section'], params['option'])
    except KeyError as e:
        value = default
    finally:
        return value

def parse_name(name):
    parameters = name.split('.')

    if len(parameters) != 2:
        raise EnvNameError('env Name is invalid')

    return {
        'section': parameters[0],
        'option': parameters[1]
    }

class EnvNameError(Exception):
    pass

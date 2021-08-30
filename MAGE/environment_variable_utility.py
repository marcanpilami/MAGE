import os

def getenv(environment_variable, default=''):
    get_env = os.getenv(environment_variable, default)
    return get_env if get_env != '' else default
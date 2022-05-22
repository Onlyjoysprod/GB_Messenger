from log.client_log_config import client_log
from functools import wraps
import inspect


def log(func):
    @wraps(func)
    def call_info(*args, **kwargs):
        res = func(*args, **kwargs)
        client_log.debug(f'Function {func.__name__} was called from {inspect.stack()[1][3]}')
        client_log.debug(f'Function {func.__name__}({args}, {kwargs}), return {res}')
        return res
    return call_info

import atexit


_PRINT_FUNCTION = print
_LOGFILE_NAME_FUNCTION = None
__CURRENT_LOG = ''


def no_print(*args, **kwargs):
    pass


def set_print_function(func):
    global _PRINT_FUNCTION
    _PRINT_FUNCTION = func


def set_logfile_func(logfile_name_function):
    global _LOGFILE_NAME_FUNCTION
    _LOGFILE_NAME_FUNCTION = logfile_name_function


def build_str(arg1, *args):
    if not args:
        return str(arg1)
    return str(arg1) + build_str(*args)


def log(*args):
    _PRINT_FUNCTION(*args)
    _log = build_str(*args).replace('\r\n', '\\r\\n\n')
    global __CURRENT_LOG
    if __CURRENT_LOG == '':
        __CURRENT_LOG += _log
    else:
        __CURRENT_LOG += '\n' + _log


def flush(logfile_name_function=None):
    if logfile_name_function is None:
        logfile_name_function = _LOGFILE_NAME_FUNCTION
    if logfile_name_function is not None:
        global __CURRENT_LOG
        filename = logfile_name_function()
        log("Writing log to file: " + filename)
        with open(filename, 'w') as file:
            file.write(__CURRENT_LOG)
        __CURRENT_LOG = ''


atexit.register(flush)

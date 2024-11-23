log_enabled = False

def log(log_text, log_value=None):
    if log_enabled:
        if log_value is not None:
            print(f"{log_text}{log_value}")
        else:
            print(f"{log_text}")

def enable_logging(enabled):
    global log_enabled
    log_enabled = enabled

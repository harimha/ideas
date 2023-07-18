import time


def measure_execution_time(func, *args, **kwargs):
    stime = time.time()
    result = func(*args, **kwargs)
    etime = time.time()
    execution_time = round(etime - stime, 2)

    return result, execution_time
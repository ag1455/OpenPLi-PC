# -*- coding: utf-8 -*-
import concurrent.futures
from itertools import islice
import xbmc
import threading

Executor = concurrent.futures.ThreadPoolExecutor


def execute(f, iterable, stop_flag=None, workers=10, timeout=30):
    with Executor(max_workers=workers) as executor:
        threading.Timer(timeout, stop_flag.set)
        for future in _batched_pool_runner(executor, workers, f,
                                           iterable, timeout):

            if xbmc.abortRequested:
                break
            if stop_flag and stop_flag.isSet():
                break
            yield future.result()


def _batched_pool_runner(pool, batch_size, f, iterable, timeout):
    futures = [pool.submit(f, x) for x in iterable]

    try:
        for item in concurrent.futures.as_completed(futures, timeout):
            yield item
    except:
        pass

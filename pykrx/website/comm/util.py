import logging

from pandas import DataFrame


def dataframe_empty_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            logging.info(args, kwargs)
            logging.info(e)
            return DataFrame()

    return wrapper


def singleton(class_):
    class SingletonWrapper(class_):
        _instance = None

        def __new__(cls, *args, **kwargs):
            if SingletonWrapper._instance is None:
                SingletonWrapper._instance = super().__new__(cls, *args, **kwargs)
                SingletonWrapper._instance._sealed = False
            return SingletonWrapper._instance

        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super().__init__(*args, **kwargs)
            self._sealed = True

    SingletonWrapper.__name__ = class_.__name__
    return SingletonWrapper

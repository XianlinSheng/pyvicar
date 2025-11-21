from abc import abstractmethod
import pyvicar.tools.mpi as mpi


class Logger:
    @abstractmethod
    def log(self, *args, **kwargs):
        pass

    @abstractmethod
    def log_host(self, *args, **kwargs):
        pass


def add_header(args: list):
    return (f"Info {mpi.rank():4d}:",) + args


def add_header_host(args: list):
    return (f"Info Host:",) + args


class StdLogger(Logger):
    def log(self, *args):
        print(*add_header(args), flush=True)

    def log_host(self, *args):
        if mpi.is_host():
            print(*add_header_host(args), flush=True)


class FileLogger(Logger):
    def __init__(self, basename="log", mode="w"):
        self._basename = basename
        self._f = open(f"{basename}.{mpi.rank()}", mode)

    def log(self, *args):
        print(*add_header(args), file=self._f, flush=True)

    def log_host(self, *args):
        if mpi.is_host():
            print(*add_header_host(args), flush=True)


_logger = StdLogger()


def set_header(text):
    global add_header
    global add_header_host

    def add_header(args: tuple):
        return (f"{text} {mpi.rank():4d}",) + args

    def add_header_host(args: tuple):
        return (f"{text} Host",) + args


def unset_header():
    global add_header
    global add_header_host

    def add_header(args: tuple):
        return args

    def add_header_host(args: tuple):
        return args


def set_std():
    global _logger
    _logger = StdLogger()


def set_file(**kwargs):
    global _logger
    _logger = FileLogger(**kwargs)


def log(*args):
    _logger.log(*args)


def log_host(*args):
    _logger.log_host(*args)

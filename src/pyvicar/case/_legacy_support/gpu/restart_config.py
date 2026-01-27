from pyvicar.case.common.restart import Restart


def create_restart_obj(case):
    return Restart(
        case,
        [
            {"prefix": "flow"},
            {"prefix": "body"},
            {"prefix": "fsi"},
        ],
    )

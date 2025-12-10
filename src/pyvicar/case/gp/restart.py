from pyvicar.case.common.restart import Restart


def create_restart_obj(case):
    return Restart(
        case,
        [
            {"prefix": "flow", "partitioned": True},
            {"prefix": "body", "partitioned": True},
            {"prefix": "scalar", "partitioned": True},
        ],
    )

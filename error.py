from enum import IntEnum, auto


class ERRORLEVEL(IntEnum):
    NORMAL = 0
    BIND_ERROR = 1
    END_POINT_FAILED = 2
    UNKNOWN_ERROR = 3
from datetime import datetime as dt

epoch = 1420070400000

def to_datetime(snowflake: int) -> dt:
    """ convert discord snowflake ID to datetime object. """
    return dt.utcfromtimestamp(to_unix(snowflake))


def to_unix(snowflake: int) -> int:
    return to_unix_ms(snowflake) / 1000


def to_unix_ms(snowflake: int) -> int:
    return (int(snowflake) >> 22) + epoch


def snowflake_gt_14(snowflake: int) -> bool:
    return (dt.now() - to_datetime(snowflake)).days >= 14


if __name__ == "__main__":
    print(to_datetime(724242687703908353))

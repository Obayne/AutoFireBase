# backend/coverage_service.py
from db.connection import get_connection
from db.coverage_tables import CEILING_STROBE_TABLE_NAME, WALL_STROBE_TABLE_NAME


def get_required_wall_strobe_candela(room_size: int) -> int | None:
    """
    Finds the required candela for a wall-mounted strobe in a room of a given size.

    Args:
        room_size: The longest dimension of the room in feet.

    Returns:
        The required candela rating, or None if no suitable rating is found.
    """
    con = get_connection()
    cur = con.cursor()
    # Find the smallest room_size in the table that is >= the given room_size
    cur.execute(
        f"""
        SELECT candela FROM {WALL_STROBE_TABLE_NAME}
        WHERE room_size >= ?
        ORDER BY room_size ASC
        LIMIT 1
        """,
        (room_size,),
    )
    result = cur.fetchone()
    return result[0] if result else None


def get_required_ceiling_strobe_candela(ceiling_height: int, room_size: int) -> int | None:
    """
    Finds the required candela for a ceiling-mounted strobe.

    Args:
        ceiling_height: The ceiling height in feet.
        room_size: The longest dimension of the room in feet.

    Returns:
        The required candela rating, or None if no suitable rating is found.
    """
    con = get_connection()
    cur = con.cursor()
    # Find the best matching record for the given ceiling height and room size.
    # We look for the closest ceiling height without going under, then the
    # smallest room size that fits.
    cur.execute(
        f"""
        SELECT candela FROM {CEILING_STROBE_TABLE_NAME}
        WHERE ceiling_height >= ? AND room_size >= ?
        ORDER BY ceiling_height ASC, room_size ASC
        LIMIT 1
        """,
        (ceiling_height, room_size),
    )
    result = cur.fetchone()
    return result[0] if result else None

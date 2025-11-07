"""Parity copy of backend.coverage_service into lv_cad.backend."""

from __future__ import annotations

from db.connection import get_connection
from db.coverage_tables import CEILING_STROBE_TABLE_NAME, WALL_STROBE_TABLE_NAME


def get_required_wall_strobe_candela(room_size: int) -> int | None:
    con = get_connection()
    cur = con.cursor()
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
    con = get_connection()
    cur = con.cursor()
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

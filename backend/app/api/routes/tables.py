from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import Reservation, TableModel, User, WaitlistEntry

router = APIRouter(prefix='/api/v1', tags=['tables'])


@router.get('/tables')
async def list_tables(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(TableModel).order_by(TableModel.id.asc()))
    tables = result.scalars().all()
    payload = []
    for table in tables:
        payload.append(
            {
                'id': table.id,
                'name': table.name,
                'status': table.status,
                'max_players': table.max_players,
                'spectator_capacity': table.spectator_capacity,
                'start_time': table.start_time.isoformat() if table.start_time else None,
                'available_seats': max(0, table.max_players - len(table.reservations)),
            }
        )
    return {'items': payload}


@router.post('/tables')
async def create_table(payload: dict, db: AsyncSession = Depends(get_db)) -> dict:
    name = payload.get('name') or 'میز جدید'
    table = TableModel(
        name=name,
        status='waiting',
        max_players=6,
        spectator_capacity=4,
    )
    db.add(table)
    await db.commit()
    await db.refresh(table)
    return {
        'id': table.id,
        'name': table.name,
        'status': table.status,
        'max_players': table.max_players,
        'spectator_capacity': table.spectator_capacity,
    }


@router.post('/tables/{table_id}/reserve')
async def reserve_table(table_id: int, payload: dict, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(TableModel).where(TableModel.id == table_id))
    table = result.scalar_one_or_none()
    if table is None:
        raise HTTPException(status_code=404, detail='Table not found')
    if table.status == 'locked':
        raise HTTPException(status_code=409, detail='Table is locked')

    user_id = payload.get('user_id')
    if user_id is None:
        raise HTTPException(status_code=400, detail='user_id is required')

    user_result = await db.execute(select(User).where(User.id == int(user_id)))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    active_reservation = await db.execute(
        select(Reservation).where(
            Reservation.user_id == int(user_id),
            Reservation.status.in_(['pending', 'confirmed']),
            Reservation.table_id == table_id,
        )
    )
    if active_reservation.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='This user already has an active reservation for this table')

    existing_user_reservations = await db.execute(
        select(Reservation).where(
            Reservation.user_id == int(user_id),
            Reservation.status.in_(['pending', 'confirmed']),
        )
    )
    if existing_user_reservations.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='This account already has a reservation in another table')

    seat_index = payload.get('seat_index')
    if seat_index is not None:
        seat_index = int(seat_index)
        if seat_index < 1 or seat_index > table.max_players:
            raise HTTPException(status_code=400, detail='Seat index is invalid')

    reservation = Reservation(
        user_id=int(user_id),
        table_id=table_id,
        seat_index=seat_index,
        status='pending',
        is_confirmed=False,
        requested_at=datetime.utcnow(),
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)

    return {
        'ok': True,
        'reservation_id': reservation.id,
        'table_id': table_id,
        'seat_index': reservation.seat_index,
        'status': reservation.status,
        'message': 'رزرو با موفقیت ثبت شد',
    }


@router.post('/tables/{table_id}/confirm')
async def confirm_reservation(table_id: int, payload: dict, db: AsyncSession = Depends(get_db)) -> dict:
    user_id = payload.get('user_id')
    if user_id is None:
        raise HTTPException(status_code=400, detail='user_id is required')

    reservation_result = await db.execute(
        select(Reservation).where(
            Reservation.table_id == table_id,
            Reservation.user_id == int(user_id),
            Reservation.status.in_(['pending', 'confirmed']),
        )
    )
    reservation = reservation_result.scalar_one_or_none()
    if reservation is None:
        raise HTTPException(status_code=404, detail='Reservation not found')

    if reservation.requested_at + timedelta(minutes=10) < datetime.utcnow():
        reservation.status = 'expired'
        await db.commit()
        raise HTTPException(status_code=410, detail='Reservation expired')

    reservation.status = 'confirmed'
    reservation.is_confirmed = True
    await db.commit()
    return {
        'ok': True,
        'reservation_id': reservation.id,
        'status': 'confirmed',
        'message': 'حضور شما تأیید شد',
    }


@router.post('/tables/{table_id}/waitlist')
async def join_waitlist(table_id: int, payload: dict, db: AsyncSession = Depends(get_db)) -> dict:
    user_id = payload.get('user_id')
    if user_id is None:
        raise HTTPException(status_code=400, detail='user_id is required')

    table_result = await db.execute(select(TableModel).where(TableModel.id == table_id))
    table = table_result.scalar_one_or_none()
    if table is None:
        raise HTTPException(status_code=404, detail='Table not found')

    existing = await db.execute(
        select(WaitlistEntry).where(WaitlistEntry.table_id == table_id, WaitlistEntry.user_id == int(user_id))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='You are already on the waitlist')

    waitlist_count = await db.execute(select(WaitlistEntry).where(WaitlistEntry.table_id == table_id))
    position = len(waitlist_count.scalars().all()) + 1
    entry = WaitlistEntry(table_id=table_id, user_id=int(user_id), position=position)
    db.add(entry)
    await db.commit()
    return {'ok': True, 'table_id': table_id, 'position': position, 'status': 'waitlisted'}


@router.post('/tables/{table_id}/cancel')
async def cancel_reservation(table_id: int, payload: dict, db: AsyncSession = Depends(get_db)) -> dict:
    user_id = payload.get('user_id')
    if user_id is None:
        raise HTTPException(status_code=400, detail='user_id is required')

    reservation_result = await db.execute(
        select(Reservation).where(
            Reservation.table_id == table_id,
            Reservation.user_id == int(user_id),
            Reservation.status.in_(['pending', 'confirmed']),
        )
    )
    reservation = reservation_result.scalar_one_or_none()
    if reservation is None:
        raise HTTPException(status_code=404, detail='Reservation not found')

    reservation.status = 'cancelled'
    await db.commit()
    return {'ok': True, 'reservation_id': reservation.id, 'status': 'cancelled'}


@router.get('/reservations/{user_id}')
async def get_user_reservations(user_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Reservation).where(Reservation.user_id == user_id).order_by(Reservation.requested_at.desc()))
    reservations = result.scalars().all()
    return {
        'items': [
            {
                'id': r.id,
                'table_id': r.table_id,
                'status': r.status,
                'seat_index': r.seat_index,
                'is_confirmed': r.is_confirmed,
            }
            for r in reservations
        ]
    }


@router.get('/tables/{table_id}/waitlist')
async def list_waitlist(table_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(
        select(WaitlistEntry).where(WaitlistEntry.table_id == table_id).order_by(WaitlistEntry.position.asc())
    )
    items = result.scalars().all()
    return {'items': [{'user_id': item.user_id, 'position': item.position} for item in items]}

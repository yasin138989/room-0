from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import TableModel

router = APIRouter(prefix='/api/v1', tags=['tables'])


@router.get('/tables', response_model=dict)
async def list_tables(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(TableModel))
    tables = result.scalars().all()
    return {
        'items': [
            {
                'id': t.id,
                'name': t.name,
                'status': t.status,
                'max_players': t.max_players,
                'spectator_capacity': t.spectator_capacity,
                'start_time': t.start_time.isoformat() if t.start_time else None,
            }
            for t in tables
        ]
    }


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

    seat_index = payload.get('seat_index')
    if seat_index is not None and (seat_index < 1 or seat_index > table.max_players):
        raise HTTPException(status_code=400, detail='Seat index is invalid')

    return {
        'ok': True,
        'table_id': table.id,
        'seat_index': seat_index,
        'status': 'reserved',
    }

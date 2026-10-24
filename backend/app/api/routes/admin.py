from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import AdminUser, Game, TableModel, User

router = APIRouter(prefix='/api/v1/admin', tags=['admin'])


@router.get('/overview')
async def admin_overview(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    users_total = await db.scalar(select(func.count(User.id))) or 0
    active_games = await db.scalar(select(func.count(Game.id).filter(Game.status == 'started'))) or 0
    tables_reserved = await db.scalar(select(func.count(TableModel.id).filter(TableModel.status == 'reserved'))) or 0
    admins_total = await db.scalar(select(func.count(AdminUser.id))) or 0

    return {
        'users_total': int(users_total),
        'active_games': int(active_games),
        'tables_reserved': int(tables_reserved),
        'admins_total': int(admins_total),
        'status': 'ok',
    }


@router.get('/users')
async def list_admin_users(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(50)
    )
    users = result.scalars().all()
    return {
        'items': [
            {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin,
            }
            for user in users
        ]
    }


@router.get('/tables')
async def list_admin_tables(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(TableModel).order_by(TableModel.id.asc()))
    tables = result.scalars().all()
    return {
        'items': [
            {
                'id': table.id,
                'name': table.name,
                'status': table.status,
                'max_players': table.max_players,
                'spectator_capacity': table.spectator_capacity,
            }
            for table in tables
        ]
    }


@router.get('/games')
async def list_admin_games(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(Game).order_by(Game.created_at.desc()).limit(20))
    games = result.scalars().all()
    return {
        'items': [
            {
                'id': game.id,
                'table_id': game.table_id,
                'status': game.status,
                'winner': game.winner,
                'started_at': game.started_at.isoformat() if game.started_at else None,
            }
            for game in games
        ]
    }


@router.post('/users/{user_id}/toggle-admin')
async def toggle_admin(user_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    user.is_admin = not user.is_admin
    await db.commit()
    return {'ok': True, 'user_id': user.id, 'is_admin': user.is_admin}

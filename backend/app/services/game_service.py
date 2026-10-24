from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import CaseModel, Clue, Game, GamePlayer, Question, TableModel, User

router = APIRouter(prefix='/api/v1', tags=['games'])


@router.get('/games/health')
def games_health() -> dict[str, str]:
    return {'status': 'ok', 'module': 'games'}


@router.post('/games/start')
async def start_game(payload: dict, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    table_id = payload.get('table_id')
    case_id = payload.get('case_id')
    if table_id is None or case_id is None:
        raise HTTPException(status_code=400, detail='table_id and case_id are required')

    table_result = await db.execute(select(TableModel).where(TableModel.id == int(table_id)))
    table = table_result.scalar_one_or_none()
    if table is None:
        raise HTTPException(status_code=404, detail='Table not found')

    case_result = await db.execute(select(CaseModel).where(CaseModel.id == int(case_id)))
    case = case_result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail='Case not found')

    game = Game(table_id=table.id, status='started', started_at=datetime.utcnow())
    db.add(game)
    await db.commit()
    await db.refresh(game)

    players = payload.get('players', [])
    if not players:
        raise HTTPException(status_code=400, detail='At least one player is required to start the game')

    roles = ['detective', 'detective', 'detective', 'spy', 'spy', 'independent']
    for index, player in enumerate(players[:6]):
        db.add(
            GamePlayer(
                game_id=game.id,
                user_id=int(player['user_id']),
                role_name=roles[index],
                is_alive=True,
                is_spectator=False,
            )
        )

    table.status = 'playing'
    await db.commit()
    return {
        'ok': True,
        'game_id': game.id,
        'status': 'started',
        'message': 'بازی شروع شد',
    }


@router.get('/games/{game_id}/players')
async def get_game_players(game_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(GamePlayer).where(GamePlayer.game_id == game_id))
    rows = result.scalars().all()
    return {
        'items': [
            {
                'id': row.id,
                'user_id': row.user_id,
                'role_name': row.role_name,
                'is_alive': row.is_alive,
            }
            for row in rows
        ]
    }


@router.post('/games/{game_id}/answer')
async def submit_answer(game_id: int, payload: dict, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    user_id = payload.get('user_id')
    question_id = payload.get('question_id')
    answer = payload.get('answer')
    if user_id is None or question_id is None or answer is None:
        raise HTTPException(status_code=400, detail='user_id, question_id and answer are required')

    question_result = await db.execute(select(Question).where(Question.id == int(question_id)))
    question = question_result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail='Question not found')

    return {
        'ok': True,
        'game_id': game_id,
        'user_id': int(user_id),
        'question_id': int(question_id),
        'answer': answer,
        'status': 'accepted',
    }


@router.post('/games/{game_id}/vote')
async def submit_vote(game_id: int, payload: dict, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    voter_id = payload.get('voter_id')
    target_id = payload.get('target_id')
    if voter_id is None or target_id is None:
        raise HTTPException(status_code=400, detail='voter_id and target_id are required')

    return {
        'ok': True,
        'game_id': game_id,
        'voter_id': int(voter_id),
        'target_id': int(target_id),
        'status': 'voted',
    }


@router.get('/games/{game_id}/clues')
async def list_clues(game_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(Clue).where(Clue.case_id == game_id))
    rows = result.scalars().all()
    return {
        'items': [
            {
                'id': row.id,
                'text': row.text,
                'visibility': row.visibility,
            }
            for row in rows
        ]
    }


@router.post('/games/{game_id}/finish')
async def finish_game(game_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if game is None:
        raise HTTPException(status_code=404, detail='Game not found')
    if game.status == 'finished':
        return {'ok': True, 'game_id': game_id, 'status': 'already_finished'}

    game.status = 'finished'
    game.finished_at = datetime.utcnow()
    await db.commit()
    return {'ok': True, 'game_id': game_id, 'status': 'finished'}


@router.get('/cases')
async def list_cases(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(CaseModel))
    cases = result.scalars().all()
    return {
        'items': [
            {
                'id': case.id,
                'title': case.title,
                'difficulty': case.difficulty,
                'is_published': case.is_published,
            }
            for case in cases
        ]
    }


@router.get('/cases/{case_id}/questions')
async def list_case_questions(case_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(Question).where(Question.case_id == case_id).order_by(Question.order_index.asc()))
    rows = result.scalars().all()
    return {
        'items': [
            {
                'id': row.id,
                'prompt': row.prompt,
                'order_index': row.order_index,
            }
            for row in rows
        ]
    }


@router.get('/games/winner/{game_id}')
async def check_game_winner(game_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(GamePlayer).where(GamePlayer.game_id == game_id))
    players = result.scalars().all()
    data = [
        {'role_name': row.role_name, 'is_alive': row.is_alive}
        for row in players
    ]
    winner = determine_game_winner(data)
    return {'game_id': game_id, 'winner': winner}


def determine_game_winner(players: list[dict[str, Any]]) -> str | None:
    alive_detectives = [p for p in players if p.get('role_name') == 'detective' and p.get('is_alive', True)]
    alive_spies = [p for p in players if p.get('role_name') == 'spy' and p.get('is_alive', True)]
    alive_others = [p for p in players if p.get('role_name') != 'spy' and p.get('is_alive', True)]

    if not alive_spies and alive_detectives:
        return 'detectives'

    if len(alive_spies) >= len(alive_others):
        return 'spies'

    alive_independent = [p for p in players if p.get('role_name') == 'independent' and p.get('is_alive', True)]
    if alive_independent:
        return 'independent'

    return None

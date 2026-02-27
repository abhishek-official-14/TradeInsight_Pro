from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.models.user import User, UserRole

router = APIRouter(prefix='/protected', tags=['protected'])


@router.get('/free')
def free_route(current_user: User = Depends(require_role(UserRole.FREE, UserRole.PRO, UserRole.ADMIN))) -> dict[str, str]:
    return {'message': f'Hello {current_user.email}, free-tier content'}


@router.get('/pro')
def pro_route(current_user: User = Depends(require_role(UserRole.PRO, UserRole.ADMIN))) -> dict[str, str]:
    return {'message': f'Hello {current_user.email}, pro content'}


@router.get('/admin')
def admin_route(current_user: User = Depends(require_role(UserRole.ADMIN))) -> dict[str, str]:
    return {'message': f'Hello {current_user.email}, admin content'}

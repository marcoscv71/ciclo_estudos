from http import HTTPStatus

from fastapi import APIRouter

from ciclo_estudos.dependencies import CurrentUser, CycleServiceDep
from ciclo_estudos.schemas import CycleProgressPublic, CyclePublic

router = APIRouter(prefix='/cycles', tags=['cycles'])


@router.get(
    '/current', status_code=HTTPStatus.OK, response_model=CycleProgressPublic
)
def read_current_cycle(service: CycleServiceDep, current_user: CurrentUser):
    return service.get_progress()


@router.post(
    '/advance', status_code=HTTPStatus.CREATED, response_model=CyclePublic
)
def advanced_cycle(service: CycleServiceDep, current_user: CurrentUser):
    return service.advance()

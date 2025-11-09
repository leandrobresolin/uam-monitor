from http import HTTPStatus

from ninja import Router

from common_tools.schemas.aircraft import AircraftSchemaList
from monitor.services.aircrafts import AircraftService

aircraft = Router(tags=["Aircraft"])
aircraft_type = Router(tags=["Aircraft Type"])


@aircraft.get(
    path="/aircrafts",
    response={
        HTTPStatus.OK: AircraftSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def list_aircrafts(request):
    service = AircraftService()
    aircrafts = service.get_all_aircrafts()

    if not aircrafts.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No Aircrafts found."}

    return HTTPStatus.OK, aircrafts

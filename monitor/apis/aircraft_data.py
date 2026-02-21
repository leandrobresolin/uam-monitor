from http import HTTPStatus

from ninja import Query, Router

from common_tools.schemas.aircraft_data import (
    AircraftDataFilterSchema,
    AircraftDataSchemaList,
)
from monitor.services.aircraft_data import AircraftDataService

aircraft_data = Router(tags=["AircraftData"])


@aircraft_data.get(
    path="/aircraft_data",
    response={
        HTTPStatus.OK: AircraftDataSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def list_aircraft_data(request, filters: AircraftDataFilterSchema = Query(...)):
    service = AircraftDataService()
    data = service.get_aircraft_data(filters=filters)

    if not data.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No aircraft data found."}

    return HTTPStatus.OK, data

from http import HTTPStatus
from uuid import UUID

from ninja import Query, Router

from common_tools.schemas.aircraft import (
    AircraftFilterSchema,
    AircraftSchema,
    AircraftSchemaList,
    SubmitAircraftSchema,
    UpdateAircraftSchema,
)
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
def list_aircrafts(request, filters: AircraftFilterSchema = Query(...)):
    service = AircraftService()
    aircrafts = service.get_aircrafts(filters=filters)

    if not aircrafts.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No Aircrafts found."}

    return HTTPStatus.OK, aircrafts


@aircraft.post(
    path="/aircrafts",
    response={
        HTTPStatus.CREATED: AircraftSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def create_aircraft(request, payload: SubmitAircraftSchema):
    service = AircraftService()

    try:
        aircraft = service.create_aircraft(payload=payload)
        return HTTPStatus.CREATED, aircraft

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@aircraft.patch(
    path="/aircrafts/{aircraft_id}",
    response={
        HTTPStatus.OK: AircraftSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def update_aircraft(request, aircraft_id: UUID, payload: UpdateAircraftSchema):
    service = AircraftService()
    try:
        updated = service.update_aircraft(aircraft_id=aircraft_id, payload=payload)
        return HTTPStatus.OK, updated

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@aircraft.delete(
    path="/aircrafts/{aircraft_id}",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def delete_aircraft(request, aircraft_id: UUID):
    service = AircraftService()
    try:
        service.delete_aircraft(aircraft_id=aircraft_id)
        return HTTPStatus.OK, {"detail": "Aircraft deleted successfully."}
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}

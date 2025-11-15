from http import HTTPStatus
from uuid import UUID

from ninja import Query, Router

from common_tools.schemas.aircraft_type import (
    AircraftTypeFilterSchema,
    AircraftTypeSchema,
    AircraftTypeSchemaList,
    SubmitAircraftTypeSchema,
    UpdateAircraftTypeSchema,
)
from monitor.services.aircraft_type import AircraftTypeService

aircraft_type = Router(tags=["Aircraft Type"])


# AIRCRAFT TYPES
@aircraft_type.get(
    path="/aircraft_types",
    response={
        HTTPStatus.OK: AircraftTypeSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def list_aircraft_types(request, filters: AircraftTypeFilterSchema = Query(...)):
    service = AircraftTypeService()
    aircrafts_types = service.get_aircraft_types(filters=filters)

    if not aircrafts_types.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No Aircraft Types found."}

    return HTTPStatus.OK, aircrafts_types


@aircraft_type.post(
    path="/aircraft_types",
    response={
        HTTPStatus.CREATED: AircraftTypeSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def create_aircraft_type(request, payload: SubmitAircraftTypeSchema):
    service = AircraftTypeService()

    try:
        aircraft_type = service.create_aircraft_type(payload=payload)
        return HTTPStatus.CREATED, aircraft_type

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@aircraft_type.patch(
    path="/aircraft_types/{aircraft_type_id}",
    response={
        HTTPStatus.OK: AircraftTypeSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def update_aircraft_type(
    request, aircraft_type_id: UUID, payload: UpdateAircraftTypeSchema
):
    service = AircraftTypeService()
    try:
        updated = service.update_aircraft_type(
            aircraft_type_id=aircraft_type_id, payload=payload
        )
        return HTTPStatus.OK, updated

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@aircraft_type.delete(
    path="/aircraft_types/{aircraft_type_id}",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def delete_aircraft_type(request, aircraft_type_id: UUID):
    service = AircraftTypeService()
    try:
        service.delete_aircraft_type(aircraft_type_id=aircraft_type_id)
        return HTTPStatus.OK, {"detail": "Aircraft type deleted successfully."}
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}

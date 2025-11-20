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
from common_tools.schemas.vertiport import (
    SubmitVertiportSchema,
    UpdateVertiportSchema,
    VertiportFilterSchema,
    VertiportSchema,
    VertiportSchemaList,
)
from monitor.services.aircraft_type import AircraftTypeService
from monitor.services.vertiport import VertiportService

vertiport = Router(tags=["Vertiport"])


# VERTIPORTS
@vertiport.get(
    path="/vertiport",
    response={
        HTTPStatus.OK: VertiportSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def list_vertiports(request, filters: VertiportFilterSchema = Query(...)):
    service = VertiportService()
    vertiports = service.get_vertiports(filters=filters)

    if not vertiports.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No Vertiports found."}

    return HTTPStatus.OK, vertiports


@vertiport.post(
    path="/vertiport",
    response={
        HTTPStatus.CREATED: VertiportSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def create_aircraft_type(request, payload: SubmitVertiportSchema):
    service = VertiportService()

    try:
        vertiport = service.create_vertiport(payload=payload)
        return HTTPStatus.CREATED, vertiport

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@vertiport.patch(
    path="/vertiport/{vertiport_id}",
    response={
        HTTPStatus.OK: VertiportSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def update_aircraft_type(request, vertiport_id: UUID, payload: UpdateVertiportSchema):
    service = VertiportService()
    try:
        updated = service.update_vertiport(vertiport_id=vertiport_id, payload=payload)
        return HTTPStatus.OK, updated

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@vertiport.delete(
    path="/vertiport/{vertiport_id}",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def delete_aircraft_type(request, vertiport_id: UUID):
    service = VertiportService()
    try:
        service.delete_vertiport(vertiport_id=vertiport_id)
        return HTTPStatus.OK, {"detail": "Vertiport deleted successfully."}
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}

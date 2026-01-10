from http import HTTPStatus
from uuid import UUID

from ninja import Query, Router

from common_tools.schemas.flight_instance import (
    FlightInstanceFilterSchema,
    FlightInstanceSchema,
    FlightInstanceSchemaList,
    SubmitFlightInstance,
    UpdateFlightInstance,
)
from monitor.services.flight_instance import FlightInstanceService

flight_instance = Router(tags=["FlightInstance"])


@flight_instance.get(
    path="/flight_instances",
    response={
        HTTPStatus.OK: FlightInstanceSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def list_flight_instances(request, filters: FlightInstanceFilterSchema = Query(...)):
    service = FlightInstanceService()
    fis = service.get_flight_instances(filters=filters)

    if not fis.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No flight instances found."}

    return HTTPStatus.OK, fis


@flight_instance.post(
    path="/flight_instances",
    response={
        HTTPStatus.CREATED: FlightInstanceSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def create_flight_instance(request, payload: SubmitFlightInstance):
    service = FlightInstanceService()
    try:
        fi = service.create_flight_instance(payload=payload)
        return HTTPStatus.CREATED, fi
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}


@flight_instance.patch(
    path="/flight_instances/{flight_instance_id}",
    response={
        HTTPStatus.OK: FlightInstanceSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def update_flight_instance(
    request, flight_instance_id: UUID, payload: UpdateFlightInstance
):
    service = FlightInstanceService()
    try:
        fi = service.update_flight_instance(
            flight_instance_id=flight_instance_id,
            payload=payload,
        )
        return HTTPStatus.OK, fi
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}


@flight_instance.delete(
    path="/flight_instances/{flight_instance_id}",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def delete_flight_instance(request, flight_instance_id: UUID):
    service = FlightInstanceService()
    try:
        service.delete_flight_instance(flight_instance_id=flight_instance_id)
        return HTTPStatus.OK, {"detail": "Flight instance deleted successfully."}
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}

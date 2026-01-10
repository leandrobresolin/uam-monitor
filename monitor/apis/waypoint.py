from http import HTTPStatus
from uuid import UUID

from ninja import Query, Router

from common_tools.schemas.waypoint import (
    SubmitWaypointSchema,
    UpdateWaypointSchema,
    WaypointFilterSchema,
    WaypointSchema,
    WaypointSchemaList,
)
from monitor.services.waypoint import WaypointService

waypoint = Router(tags=["Waypoint"])


# WAYPOINTS
@waypoint.get(
    path="/waypoints",
    response={
        HTTPStatus.OK: WaypointSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def list_waypoints(request, filters: WaypointFilterSchema = Query(...)):
    service = WaypointService()
    waypoints = service.get_waypoints(filters=filters)

    if not waypoints.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No waypoints found."}

    return HTTPStatus.OK, waypoints


@waypoint.post(
    path="/waypoints",
    response={
        HTTPStatus.CREATED: WaypointSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def create_waypoint(request, payload: SubmitWaypointSchema):
    service = WaypointService()

    try:
        waypoint = service.create_waypoint(payload=payload)
        return HTTPStatus.CREATED, waypoint

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@waypoint.patch(
    path="/waypoints/{waypoint_id}",
    response={
        HTTPStatus.OK: WaypointSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def update_waypoint(request, waypoint_id: UUID, payload: UpdateWaypointSchema):
    service = WaypointService()
    try:
        updated = service.update_waypoint(waypoint_id=waypoint_id, payload=payload)
        return HTTPStatus.OK, updated

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@waypoint.delete(
    path="/waypoints/{waypoint_id}",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def delete_waypoint(request, waypoint_id: UUID):
    service = WaypointService()
    try:
        service.delete_waypoint(waypoint_id=waypoint_id)
        return HTTPStatus.OK, {"detail": "Waypoint deleted successfully."}
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}

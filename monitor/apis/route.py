from http import HTTPStatus
from uuid import UUID

from ninja import Query, Router

from common_tools.schemas.route import (
    RouteFilterSchema,
    RouteSchema,
    RouteSchemaList,
    SubmitRouteSchema,
    UpdateRouteSchema,
)
from monitor.services.route import RouteService

route = Router(tags=["Route"])


# ROUTES
@route.get(
    path="/routes",
    response={
        HTTPStatus.OK: RouteSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def list_routes(request, filters: RouteFilterSchema = Query(...)):
    service = RouteService()
    routes = service.get_routes(filters=filters)

    if not routes.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No routes found."}

    return HTTPStatus.OK, routes


@route.post(
    path="/routes",
    response={
        HTTPStatus.CREATED: RouteSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
        HTTPStatus.NOT_FOUND: dict,
    },
)
def create_route(request, payload: SubmitRouteSchema):
    service = RouteService()

    try:
        route = service.create_route(payload=payload)
        return HTTPStatus.CREATED, route

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@route.patch(
    path="/routes/{route_id}",
    response={
        HTTPStatus.OK: RouteSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def update_route(request, route_id: UUID, payload: UpdateRouteSchema):
    service = RouteService()
    try:
        updated = service.update_route(route_id=route_id, payload=payload)
        return HTTPStatus.OK, updated

    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}


@route.delete(
    path="/routes/{route_id}",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def delete_route(request, route_id: UUID):
    service = RouteService()
    try:
        service.delete_route(route_id=route_id)
        return HTTPStatus.OK, {"detail": "Route deleted successfully."}
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}

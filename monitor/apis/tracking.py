from http import HTTPStatus
from uuid import UUID

from ninja import Query, Router

from common_tools.schemas.tracking import (
    SubmitTrackingSchema,
    TrackingFilterSchema,
    TrackingSchema,
    TrackingSchemaList,
)
from monitor.services.tracking import TrackingService

tracking = Router(tags=["Tracking"])


@tracking.get(
    path="/tracking",
    response={
        HTTPStatus.OK: TrackingSchemaList,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def list_tracking(request, filters: TrackingFilterSchema = Query(...)):
    service = TrackingService()
    trackings = service.get_tracking(filters=filters)

    if not trackings.root:
        return HTTPStatus.NOT_FOUND, {"detail": "No tracking records found."}

    return HTTPStatus.OK, trackings


@tracking.post(
    path="/tracking",
    response={
        HTTPStatus.CREATED: TrackingSchema,
        HTTPStatus.BAD_REQUEST: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def create_tracking(request, payload: SubmitTrackingSchema):
    service = TrackingService()
    try:
        tracking_obj = service.create_or_update_tracking(payload=payload)
        return HTTPStatus.CREATED, tracking_obj
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}


@tracking.delete(
    path="/tracking/{tracking_id}",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.NOT_FOUND: dict,
        HTTPStatus.INTERNAL_SERVER_ERROR: dict,
    },
)
def delete_tracking(request, tracking_id: UUID):
    service = TrackingService()
    try:
        service.delete_tracking(tracking_id=tracking_id)
        return HTTPStatus.OK, {"detail": "Tracking deleted successfully."}
    except ValueError as e:
        return HTTPStatus.NOT_FOUND, {"detail": str(e)}
    except Exception as e:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"detail": str(e)}

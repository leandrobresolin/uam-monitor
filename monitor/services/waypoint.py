from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from common_tools.schemas.route import RouteSchema
from common_tools.schemas.vertiport import VertiportSchema
from common_tools.schemas.waypoint import (
    SubmitWaypointSchema,
    UpdateWaypointSchema,
    WaypointFilterSchema,
    WaypointSchema,
    WaypointSchemaList,
)
from monitor.models import Route, Vertiport, Waypoint
from monitor.services.route import RouteService
from monitor.services.vertiport import VertiportService


class WaypointService:
    def get_waypoints(self, filters: WaypointFilterSchema) -> WaypointSchemaList:
        route_service = RouteService()
        vertiport_service = VertiportService()

        queryset = Waypoint.objects.all()

        if filters.id is not None:
            queryset = queryset.filter(id=filters.id)
        if filters.route is not None:
            queryset = queryset.filter(route=filters.route)
        if filters.vertiport is not None:
            queryset = queryset.filter(vertiport=filters.vertiport)
        if filters.name is not None:
            queryset = queryset.filter(name=filters.name)

        waypoint_schema_list = []
        for waypoint in queryset:
            route_id = waypoint.route.id
            vertiport_id = waypoint.vertiport.id if waypoint.vertiport else None

            route = route_service.get_route_by_id(route_id)
            vertiport = vertiport_service.get_vertiport_by_id(vertiport_id)

            waypoint_schema_list.append(
                WaypointSchema(
                    id=waypoint.id,
                    route=RouteSchema.model_validate(route),
                    vertiport=VertiportSchema.model_validate(vertiport),
                    name=waypoint.name,
                    latitude=waypoint.latitude,
                    longitude=waypoint.longitude,
                    altitude=waypoint.altitude,
                    sequence_order=waypoint.sequence_order,
                )
            )

        return WaypointSchemaList(root=waypoint_schema_list)

    def create_waypoint(self, payload: SubmitWaypointSchema) -> WaypointSchema:
        if not Route.objects.filter(id=payload.route).exists():
            raise ValueError("Route not found. Unable to create Waypoint.")

        if not Vertiport.objects.filter(id=payload.route).exists():
            raise ValueError("Vertiport not found. Unable to create Waypoint.")

        data = payload.model_dump()

        try:
            waypoint = Waypoint.objects.create(**data)
        except Exception as e:
            raise ValueError(f"Failed to create waypoint: {e}")

        return WaypointSchema.model_validate(waypoint)

    def update_waypoint(
        self, waypoint_id: UUID, payload: UpdateWaypointSchema
    ) -> WaypointSchema:
        try:
            waypoint = Waypoint.objects.get(id=waypoint_id)
        except ObjectDoesNotExist:
            raise ValueError("Waypoint not found. Unable to update.")

        update_data = payload.model_dump(exclude_unset=True)

        if "route" in update_data:
            try:
                route = Route.objects.get(id=update_data["route"])
                waypoint.route = route
            except ObjectDoesNotExist:
                raise ValueError("Route not found. Unable to update waypoint.")
            del update_data["route"]

        if "vertiport" in update_data:
            try:
                vertiport = Vertiport.objects.get(id=update_data["vertiport"])
                waypoint.vertiport = vertiport
            except ObjectDoesNotExist:
                raise ValueError("Vertiport not found. Unable to update waypoint.")
            del update_data["vertiport"]

        for attr, value in update_data.items():
            setattr(waypoint, attr, value)

        waypoint.save()

        return WaypointSchema.model_validate(waypoint)

    def delete_waypoint(self, waypoint_id: UUID) -> None:
        try:
            waypoint = Waypoint.objects.get(id=waypoint_id)
            waypoint.delete()
        except ObjectDoesNotExist:
            raise ValueError("Waypoint not found. Unable to delete.")

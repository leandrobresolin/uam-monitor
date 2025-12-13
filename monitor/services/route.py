from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from common_tools.schemas.route import (
    RouteFilterSchema,
    RouteSchema,
    RouteSchemaList,
    SubmitRouteSchema,
    UpdateRouteSchema,
)
from monitor.models import Route


class RouteService:
    def get_route_by_id(self, id: UUID) -> Route | None:
        aircraft_type = Route.objects.filter(id=id).first()

        return aircraft_type

    def get_routes(self, filters: RouteFilterSchema) -> RouteSchemaList:

        queryset = Route.objects.all()

        if filters.id is not None:
            queryset = queryset.filter(id=filters.id)
        if filters.name is not None:
            queryset = queryset.filter(name=filters.name)

        route_schema_list = [RouteSchema.model_validate(obj) for obj in queryset]

        return RouteSchemaList(root=route_schema_list)

    def create_route(self, payload: SubmitRouteSchema) -> RouteSchema:

        data = payload.model_dump()

        try:
            route = Route.objects.create(**data)
        except Exception as e:
            raise ValueError(f"Failed to create route: {e}")

        return RouteSchema.model_validate(route)

    def update_route(self, route_id: UUID, payload: UpdateRouteSchema):

        try:
            route = Route.objects.get(id=route_id)
        except ObjectDoesNotExist:
            raise ValueError("Route not found. Unable to update.")

        update_data = payload.model_dump(exclude_unset=True)

        for attr, value in update_data.items():
            setattr(route, attr, value)

        route.save()

        return RouteSchema.model_validate(route)

    def delete_route(self, route_id: UUID) -> None:
        try:
            route = Route.objects.get(id=route_id)
            route.delete()
        except ObjectDoesNotExist:
            raise ValueError("Route not found. Unable to delete.")

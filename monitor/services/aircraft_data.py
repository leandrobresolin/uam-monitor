from uuid import UUID

from common_tools.schemas.aircraft_data import (
    AircraftDataFilterSchema,
    AircraftDataSchema,
    AircraftDataSchemaList,
)
from common_tools.schemas.flight_instance import FlightInstanceSchema
from monitor.models import AircraftData


class AircraftDataService:
    def get_aircraft_data(
        self, filters: AircraftDataFilterSchema
    ) -> AircraftDataSchemaList:

        queryset = AircraftData.objects.select_related(
            "flight_instance",
            "flight_instance__aircraft",
            "flight_instance__route",
            "flight_instance__departure_vertiport",
            "flight_instance__arrival_vertiport",
        ).all()

        if filters.id is not None:
            queryset = queryset.filter(id=filters.id)
        if filters.flight_instance is not None:
            queryset = queryset.filter(flight_instance_id=filters.flight_instance)
        if filters.aircraft is not None:
            if isinstance(filters.aircraft, UUID):
                queryset = queryset.filter(
                    flight_instance__aircraft_id=filters.aircraft
                )
            else:
                queryset = queryset.filter(
                    flight_instance__aircraft__tail_number=filters.aircraft
                )
        if filters.created_from is not None:
            queryset = queryset.filter(created_at__gte=filters.created_from)
        if filters.created_to is not None:
            queryset = queryset.filter(created_at__lte=filters.created_to)
        if filters.created_at is not None:
            queryset = queryset.filter(created_at=filters.created_at)
        if filters.updated_at is not None:
            queryset = queryset.filter(updated_at=filters.updated_at)

        queryset = queryset.order_by("created_at")

        schema_list = [
            AircraftDataSchema(
                id=aircraft_data.id,
                flight_instance=FlightInstanceSchema.model_validate(
                    aircraft_data.flight_instance
                ),
                latitude=aircraft_data.latitude,
                longitude=aircraft_data.longitude,
                altitude=aircraft_data.altitude,
                speed=aircraft_data.speed,
                energy_level=aircraft_data.energy_level,
                created_at=aircraft_data.created_at,
                updated_at=getattr(aircraft_data, "updated_at", None),
            )
            for aircraft_data in queryset
        ]

        return AircraftDataSchemaList(root=schema_list)

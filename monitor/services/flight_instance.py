from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from common_tools.schemas.aircraft import AircraftSchema
from common_tools.schemas.flight_instance import (
    FlightInstanceFilterSchema,
    FlightInstanceSchema,
    FlightInstanceSchemaList,
    SubmitFlightInstance,
    UpdateFlightInstance,
)
from common_tools.schemas.route import RouteSchema
from common_tools.schemas.vertiport import VertiportSchema
from monitor.models import Aircraft, FlightInstance, Route, Vertiport


class FlightInstanceService:
    def get_flight_instances(
        self, filters: FlightInstanceFilterSchema
    ) -> FlightInstanceSchemaList:
        queryset = FlightInstance.objects.select_related(
            "aircraft",
            "route",
            "departure_vertiport",
            "arrival_vertiport",
        ).all()

        if filters.id is not None:
            queryset = queryset.filter(id=filters.id)
        if filters.flight_status is not None:
            queryset = queryset.filter(flight_status=filters.flight_status)
        if filters.departure_vertiport is not None:
            queryset = queryset.filter(
                departure_vertiport_id=filters.departure_vertiport
            )
        if filters.arrival_vertiport is not None:
            queryset = queryset.filter(arrival_vertiport_id=filters.arrival_vertiport)
        if filters.scheduled_departure_datetime is not None:
            queryset = queryset.filter(
                scheduled_departure_datetime=filters.scheduled_departure_datetime
            )
        if filters.scheduled_arrival_datetime is not None:
            queryset = queryset.filter(
                scheduled_arrival_datetime=filters.scheduled_arrival_datetime
            )

        fi_schema_list = []
        for fi in queryset:
            fi_schema_list.append(
                FlightInstanceSchema(
                    id=fi.id,
                    aircraft=AircraftSchema.model_validate(fi.aircraft),
                    callsign=fi.callsign,
                    route=(RouteSchema.model_validate(fi.route) if fi.route else None),
                    flight_status=fi.flight_status,
                    departure_vertiport=(
                        VertiportSchema.model_validate(fi.departure_vertiport)
                        if fi.departure_vertiport
                        else None
                    ),
                    arrival_vertiport=(
                        VertiportSchema.model_validate(fi.arrival_vertiport)
                        if fi.arrival_vertiport
                        else None
                    ),
                    scheduled_departure_datetime=fi.scheduled_departure_datetime,
                    scheduled_arrival_datetime=fi.scheduled_arrival_datetime,
                )
            )

        return FlightInstanceSchemaList(root=fi_schema_list)

    def _get_fk_or_error(self, model, pk, not_found_message: str):
        if pk is None:
            return None
        try:
            return model.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise ValueError(not_found_message)

    def create_flight_instance(
        self, payload: SubmitFlightInstance
    ) -> FlightInstanceSchema:
        # Validates mandatory FK
        aircraft = self._get_fk_or_error(
            Aircraft,
            payload.aircraft,
            "Aircraft not found. Unable to create FlightInstance.",
        )
        route = self._get_fk_or_error(
            Route, payload.route, "Route not found. Unable to create FlightInstance."
        )
        departure_vertiport = self._get_fk_or_error(
            Vertiport,
            payload.departure_vertiport,
            "Departure vertiport not found. Unable to create FlightInstance.",
        )
        arrival_vertiport = self._get_fk_or_error(
            Vertiport,
            payload.arrival_vertiport,
            "Arrival vertiport not found. Unable to create FlightInstance.",
        )

        data = payload.model_dump()
        # Replaces UUIDs for instances
        data["aircraft"] = aircraft
        data["route"] = route
        data["departure_vertiport"] = departure_vertiport
        data["arrival_vertiport"] = arrival_vertiport

        fi = FlightInstance.objects.create(**data)

        return FlightInstanceSchema.model_validate(fi)

    def update_flight_instance(
        self, flight_instance_id: UUID, payload: UpdateFlightInstance
    ) -> FlightInstanceSchema:
        try:
            fi = FlightInstance.objects.get(id=flight_instance_id)
        except ObjectDoesNotExist:
            raise ValueError("FlightInstance not found. Unable to update.")

        update_data = payload.model_dump(exclude_unset=True)

        if "aircraft" in update_data:
            fi.aircraft = self._get_fk_or_error(
                Aircraft,
                update_data["aircraft"],
                "Aircraft not found. Unable to update FlightInstance.",
            )
            del update_data["aircraft"]

        if "route" in update_data:
            fi.route = self._get_fk_or_error(
                Route,
                update_data["route"],
                "Route not found. Unable to update FlightInstance.",
            )
            del update_data["route"]

        if "departure_vertiport" in update_data:
            fi.departure_vertiport = self._get_fk_or_error(
                Vertiport,
                update_data["departure_vertiport"],
                "Departure vertiport not found. Unable to update FlightInstance.",
            )
            del update_data["departure_vertiport"]

        if "arrival_vertiport" in update_data:
            fi.arrival_vertiport = self._get_fk_or_error(
                Vertiport,
                update_data["arrival_vertiport"],
                "Arrival vertiport not found. Unable to update FlightInstance.",
            )
            del update_data["arrival_vertiport"]

        for attr, value in update_data.items():
            setattr(fi, attr, value)

        fi.save()

        return FlightInstanceSchema.model_validate(fi)

    def delete_flight_instance(self, flight_instance_id: UUID) -> None:
        try:
            fi = FlightInstance.objects.get(id=flight_instance_id)
        except ObjectDoesNotExist:
            raise ValueError("FlightInstance not found. Unable to delete.")

        fi.delete()

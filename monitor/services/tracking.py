from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from common_tools.schemas.tracking import (
    SubmitTrackingSchema,
    TrackingFilterSchema,
    TrackingSchema,
    TrackingSchemaList,
)
from monitor.models import AircraftData, FlightInstance, Tracking


class TrackingService:
    def get_tracking(self, filters: TrackingFilterSchema) -> TrackingSchemaList:
        queryset = Tracking.objects.select_related(
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
        if filters.active is not None:
            queryset = queryset.filter(active=filters.active)

        schema_list = [TrackingSchema.model_validate(track) for track in queryset]
        return TrackingSchemaList(root=schema_list)

    def _get_flight_instance_or_error(self, pk: UUID) -> FlightInstance:
        try:
            return FlightInstance.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise ValueError(
                "FlightInstance not found. Unable to create/update Tracking."
            )

    def create_or_update_tracking(
        self, payload: SubmitTrackingSchema
    ) -> TrackingSchema:

        fi = self._get_flight_instance_or_error(payload.flight_instance)

        data = payload.model_dump()

        data.pop("flight_instance", None)
        data.pop("started_at", None)
        data.pop("updated_at", None)

        tracking_obj, _created = Tracking.objects.update_or_create(
            flight_instance=fi,
            defaults=data,
        )

        # Creates history
        AircraftData.objects.create(
            flight_instance=fi,
            latitude=tracking_obj.latitude,
            longitude=tracking_obj.longitude,
            altitude=tracking_obj.altitude,
            speed=tracking_obj.speed,
            energy_level=tracking_obj.energy_level,
        )

        return TrackingSchema.model_validate(tracking_obj)

    def delete_tracking(self, tracking_id: UUID) -> None:
        try:
            tracking_obj = Tracking.objects.get(id=tracking_id)
        except ObjectDoesNotExist:
            raise ValueError("Tracking not found. Unable to delete.")

        tracking_obj.delete()

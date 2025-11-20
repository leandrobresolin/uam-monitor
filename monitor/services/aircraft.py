from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from common_tools.schemas.aircraft import (
    AircraftFilterSchema,
    AircraftSchema,
    AircraftSchemaList,
    SubmitAircraftSchema,
    UpdateAircraftSchema,
)
from common_tools.schemas.aircraft_type import AircraftTypeSchema
from monitor.models import Aircraft, AircraftType
from monitor.services.aircraft_type import AircraftTypeService


class AircraftService:
    def get_aircrafts(self, filters: AircraftFilterSchema) -> AircraftSchemaList:
        aircraft_type_service = AircraftTypeService()

        queryset = Aircraft.objects.all()

        if filters.id is not None:
            queryset = queryset.filter(id=filters.id)
        if filters.tail_number is not None:
            queryset = queryset.filter(tail_number=filters.tail_number)
        if filters.aircraft_type is not None:
            queryset = queryset.filter(aircraft_type_id=filters.aircraft_type)
        if filters.year is not None:
            queryset = queryset.filter(year=filters.year)

        aircraft_schema_list = []
        for aircraft in queryset:
            aircraft_type = aircraft_type_service.get_aircraft_type_by_id(
                aircraft.aircraft_type.id
            )
            aircraft_schema_list.append(
                AircraftSchema(
                    id=aircraft.id,
                    tail_number=aircraft.tail_number,
                    aircraft_type=AircraftTypeSchema(
                        id=aircraft_type.id,
                        name=aircraft_type.name,
                        manufacturer=aircraft_type.manufacturer,
                        energy_type=aircraft_type.energy_type,
                        model_type=aircraft_type.model_type,
                    ),
                    year=aircraft.year,
                )
            )

        return AircraftSchemaList(root=aircraft_schema_list)

    def create_aircraft(self, payload: SubmitAircraftSchema) -> None:
        if not AircraftType.objects.filter(id=payload.aircraft_type).exists():
            raise ValueError("Aircraft type not found. Unable to create aircraft.")

        data = payload.model_dump()

        try:
            aircraft = Aircraft.objects.create(**data)
        except Exception as e:
            raise ValueError(f"Failed to create aircraft: {e}")

        return AircraftSchema.model_validate(aircraft)

    def update_aircraft(
        self, aircraft_id: UUID, payload: UpdateAircraftSchema
    ) -> AircraftSchema:

        try:
            aircraft = Aircraft.objects.get(id=aircraft_id)
        except ObjectDoesNotExist:
            raise ValueError("Aircraft not found. Unable to update.")

        update_data = payload.model_dump(exclude_unset=True)

        if "aircraft_type" in update_data:
            try:
                aircraft_type = AircraftType.objects.get(
                    id=update_data["aircraft_type"]
                )
                aircraft.aircraft_type = aircraft_type
            except ObjectDoesNotExist:
                raise ValueError("Aircraft type not found. Unable to update aircraft.")
            del update_data["aircraft_type"]

        for attr, value in update_data.items():
            setattr(aircraft, attr, value)

        aircraft.save()

        return AircraftSchema.model_validate(aircraft)

    def delete_aircraft(self, aircraft_id: UUID) -> None:
        try:
            aircraft = Aircraft.objects.get(id=aircraft_id)
            aircraft.delete()
        except ObjectDoesNotExist:
            raise ValueError("Aircraft not found. Unable to delete.")

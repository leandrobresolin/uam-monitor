from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from common_tools.schemas.aircraft_type import (
    AircraftTypeFilterSchema,
    AircraftTypeSchema,
    AircraftTypeSchemaList,
    SubmitAircraftTypeSchema,
    UpdateAircraftTypeSchema,
)
from monitor.models import AircraftType


class AircraftTypeService:
    def get_aircraft_type_by_id(self, id: UUID):
        aircraft_type = AircraftType.objects.filter(id=id).first()

        return aircraft_type

    def get_aircraft_types(
        self, filters: AircraftTypeFilterSchema
    ) -> AircraftTypeSchemaList:

        queryset = AircraftType.objects.all()

        if filters.id is not None:
            queryset = queryset.filter(id=filters.id)
        if filters.name is not None:
            queryset = queryset.filter(name=filters.name)
        if filters.manufacturer is not None:
            queryset = queryset.filter(manufacturer=filters.manufacturer)
        if filters.energy_type is not None:
            queryset = queryset.filter(energy_type=filters.energy_type)
        if filters.model_type is not None:
            queryset = queryset.filter(model_type=filters.model_type)

        aircraft_type_schema_list = [
            AircraftTypeSchema.model_validate(obj) for obj in queryset
        ]

        return AircraftTypeSchemaList(root=aircraft_type_schema_list)

    def create_aircraft_type(
        self, payload: SubmitAircraftTypeSchema
    ) -> AircraftTypeSchema:
        try:
            aircraft_type = AircraftType.objects.create(
                name=payload.name,
                manufacturer=payload.manufacturer,
                energy_type=payload.energy_type.value,
                model_type=payload.model_type.value,
            )
        except Exception as e:
            raise ValueError(f"Failed to create aircraft_type: {e}")

        return AircraftTypeSchema.model_validate(aircraft_type)

    def update_aircraft_type(
        self, aircraft_type_id: UUID, payload: UpdateAircraftTypeSchema
    ):

        try:
            aircraft_type = AircraftType.objects.get(id=aircraft_type_id)
        except ObjectDoesNotExist:
            raise ValueError("Aircraft not found. Unable to update.")

        update_data = payload.model_dump(exclude_unset=True)

        for attr, value in update_data.items():
            setattr(aircraft_type, attr, value)

        aircraft_type.save()

        return AircraftTypeSchema.model_validate(aircraft_type)

    def delete_aircraft_type(self, aircraft_type_id: UUID) -> None:
        try:
            aircraft_type = AircraftType.objects.get(id=aircraft_type_id)
            aircraft_type.delete()
        except ObjectDoesNotExist:
            raise ValueError("Aircraft type not found. Unable to delete.")

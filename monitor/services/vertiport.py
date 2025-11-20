from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from common_tools.schemas.vertiport import (
    SubmitVertiportSchema,
    UpdateVertiportSchema,
    VertiportFilterSchema,
    VertiportSchema,
    VertiportSchemaList,
)
from monitor.models import Vertiport


class VertiportService:
    def get_vertiports(self, filters: VertiportFilterSchema) -> VertiportSchemaList:

        queryset = Vertiport.objects.all()

        if filters.id is not None:
            queryset = queryset.filter(id=filters.id)
        if filters.vertiport_code is not None:
            queryset = queryset.filter(vertiport_code=filters.vertiport_code)
        if filters.vertiport_name is not None:
            queryset = queryset.filter(vertiport_name=filters.vertiport_name)

        aircraft_type_schema_list = [
            VertiportSchema.model_validate(obj) for obj in queryset
        ]

        return VertiportSchemaList(root=aircraft_type_schema_list)

    def create_vertiport(self, payload: SubmitVertiportSchema) -> VertiportSchema:

        data = payload.model_dump()

        try:
            vertiport = Vertiport.objects.create(**data)
        except Exception as e:
            raise ValueError(f"Failed to create vertiport: {e}")

        return VertiportSchema.model_validate(vertiport)

    def update_vertiport(
        self, vertiport_id: UUID, payload: UpdateVertiportSchema
    ) -> VertiportSchema:

        try:
            vertiport = Vertiport.objects.get(id=vertiport_id)
        except ObjectDoesNotExist:
            raise ValueError("Vertiport not found. Unable to update.")

        update_data = payload.model_dump(exclude_unset=True)

        for attr, value in update_data.items():
            setattr(vertiport, attr, value)

        vertiport.save()

        return VertiportSchema.model_validate(vertiport)

    def delete_vertiport(self, vertiport_id: UUID) -> None:
        try:
            vertiport = Vertiport.objects.get(id=vertiport_id)
            vertiport.delete()
        except ObjectDoesNotExist:
            raise ValueError("Vertiport not found. Unable to delete.")

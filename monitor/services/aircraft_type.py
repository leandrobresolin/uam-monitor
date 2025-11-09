from uuid import UUID

from monitor.models import AircraftType


class AircraftTypeService:
    def get_aircraft_type_by_id(self, id: UUID):
        aircraft_type = AircraftType.objects.filter(id=id).first()

        return aircraft_type

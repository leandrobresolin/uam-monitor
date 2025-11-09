from common_tools.schemas.aircraft import AircraftSchema, AircraftSchemaList
from common_tools.schemas.aircraft_type import AircraftTypeSchema
from monitor.models import Aircraft
from monitor.services.aircraft_type import AircraftTypeService


class AircraftService:
    def get_all_aircrafts(self) -> AircraftSchemaList:
        aircraft_type_service = AircraftTypeService()

        aircraft_list = Aircraft.objects.all()

        aircraft_schema_list = []
        for aircraft in aircraft_list:
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

from ninja import Router

from common_tools.schemas.aircraft import AircraftSchema
from monitor.models import Aircraft

aircraft = Router(tags=["Aircraft"])
aircraft_type = Router(tags=["Aircraft Type"])


@aircraft.get("/aircrafts", response=list[AircraftSchema])
def list_aircrafts(request) -> list[AircraftSchema]:
    return [
        AircraftSchema(
            id=str(obj.id),
            tail_number=obj.tail_number,
            model=str(obj.model_id),
            year=obj.year,
        )
        for obj in Aircraft.objects.all()
    ]

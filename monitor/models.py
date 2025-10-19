import uuid

from django.db import models


class AircraftType(models.Model):

    class EnergyType(models.Model):
        ELECTRIC = "ELECTRIC"
        FUEL = "FUEL"

    class ModelType(models.Model):
        EVTOL = "EVTOL"
        DRONE = "DRONE"
        HELICOPTER = "HELICOPTER"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    energy_type = models.CharField(
        max_length=10, choices=EnergyType, default=EnergyType.ELECTRIC
    )
    model_type = models.CharField(
        max_length=10, choices=ModelType, default=ModelType.EVTOL
    )

    def __str__(self):
        return f"{self.manufacturer} - {self.name} - {self.model_type}"


class Aircraft(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tail_number = models.CharField(max_length=20, unique=True)
    model = models.ForeignKey(
        AircraftType, on_delete=models.CASCADE, related_name="aircrafts"
    )
    year = models.PositiveIntegerField()

    def __str__(self):
        return self.registration


class AircraftData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aircraft = models.ForeignKey(
        Aircraft, on_delete=models.CASCADE, related_name="data_records"
    )
    altitude = models.FloatField()
    speed = models.FloatField()
    energy_level = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data for {self.aircraft.registration} at {self.date_recorded}"

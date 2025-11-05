import uuid

from django.db import models


class FlightStatus(models.TextChoices):
    PENDING = "PENDING"
    ACTIVATED = "ACTIVATED"
    CANCELLED = "CANCELLED"
    TERMINATED = "TERMINATED"


class AircraftType(models.Model):

    class EnergyType(models.TextChoices):
        ELECTRIC = "ELECTRIC"
        FUEL = "FUEL"

    class ModelType(models.TextChoices):
        EVTOL = "EVTOL"
        DRONE = "DRONE"
        HELICOPTER = "HELICOPTER"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
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
    year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.registration


class AircraftData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aircraft = models.ForeignKey(
        Aircraft, on_delete=models.CASCADE, related_name="data_records"
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    energy_level = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Data for {self.aircraft.registration} at {self.date_recorded}"


class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Waypoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="waypoints")
    name = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)
    sequence_order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class Tracking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flight_instance = models.OneToOneField(
        "FlightInstance", on_delete=models.CASCADE, related_name="tracking"
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    speed = models.FloatField()
    energy_level = models.FloatField()
    active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking for {self.flight_instance.aircraft.tail_number} (active: {self.active})"


class FlightInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aircraft = models.ForeignKey(
        Aircraft, on_delete=models.CASCADE, related_name="flights"
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flight_instances",
    )
    flight_status = models.CharField(
        max_length=15,
        choices=FlightStatus.choices,
        default=FlightStatus.PENDING,
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.aircraft.tail_number} [{self.flight_status}] {self.start_time}"

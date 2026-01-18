from django.contrib import admin

from .models import (
    Aircraft,
    AircraftData,
    AircraftType,
    FlightInstance,
    Route,
    Tracking,
    Vertiport,
    Waypoint,
)


@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "name", "model_type", "energy_type")
    search_fields = ("manufacturer", "name")
    list_filter = ("model_type", "energy_type")


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ("tail_number", "aircraft_type", "year", "energy_fuel")
    search_fields = ("tail_number",)
    list_filter = ("aircraft_type__model_type", "aircraft_type__energy_type")


@admin.register(Vertiport)
class VertiportAdmin(admin.ModelAdmin):
    list_display = ("vertiport_code", "vertiport_name", "latitude", "longitude")
    search_fields = ("vertiport_code", "vertiport_name")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "name",
        "sequence_order",
        "latitude",
        "longitude",
        "altitude",
    )
    list_filter = ("route",)


@admin.register(Tracking)
class TrackingAdmin(admin.ModelAdmin):
    list_display = (
        "flight_instance",
        "latitude",
        "longitude",
        "altitude",
        "speed",
        "energy_level",
        "active",
        "started_at",
        "finished_at",
        "updated_at",
    )
    list_filter = ("active", "flight_instance__aircraft")
    search_fields = ("flight_instance__aircraft__tail_number",)


@admin.register(AircraftData)
class AircraftDataAdmin(admin.ModelAdmin):
    list_display = (
        "flight_instance",
        "latitude",
        "longitude",
        "altitude",
        "speed",
        "energy_level",
        "created_at",
    )
    list_filter = ("flight_instance__aircraft",)
    date_hierarchy = "created_at"


class AircraftDataInline(admin.TabularInline):
    model = AircraftData
    extra = 0
    readonly_fields = (
        "latitude",
        "longitude",
        "altitude",
        "speed",
        "energy_level",
        "created_at",
    )


class TrackingInline(admin.StackedInline):
    model = Tracking
    extra = 0
    can_delete = False


@admin.register(FlightInstance)
class FlightInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "aircraft",
        "callsign",
        "flight_status",
        "route",
        "departure_vertiport",
        "arrival_vertiport",
        "scheduled_departure_datetime",
        "scheduled_arrival_datetime",
    )
    list_filter = ("flight_status", "route", "departure_vertiport", "arrival_vertiport")
    search_fields = ("callsign", "aircraft__tail_number")
    date_hierarchy = "scheduled_departure_datetime"
    inlines = [TrackingInline, AircraftDataInline]

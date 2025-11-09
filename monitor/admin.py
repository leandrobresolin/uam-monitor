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


# AircraftType
@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "name", "energy_type", "model_type")
    search_fields = ("manufacturer", "name")
    list_filter = ("energy_type", "model_type")


# Aircraft
@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ("tail_number", "aircraft_type", "year")
    search_fields = (
        "tail_number",
        "aircraft_type__name",
        "aircraft_type__manufacturer",
    )
    list_filter = ("aircraft_type",)


# AircraftData
@admin.register(AircraftData)
class AircraftDataAdmin(admin.ModelAdmin):
    list_display = (
        "aircraft",
        "created_at",
        "altitude",
        "speed",
        "energy_level",
    )
    list_filter = ("aircraft",)
    search_fields = ("aircraft__tail_number",)
    readonly_fields = ("created_at", "updated_at")


# Inline Waypoints
class WaypointInline(admin.TabularInline):
    model = Waypoint
    extra = 1
    fields = (
        "name",
        "latitude",
        "longitude",
        "altitude",
        "sequence_order",
        "vertiport",
    )


# Route with departure and arrival vertiports and Inline Waypoint
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "name",
        "departure_vertiport__vertiport_name",
        "arrival_vertiport__vertiport_name",
    )
    list_filter = ("id", "name")
    inlines = [WaypointInline]


# FlightInstance admin with Tracking inline
class TrackingInline(admin.StackedInline):
    model = Tracking
    can_delete = False
    readonly_fields = ("id", "updated_at", "started_at", "finished_at")
    extra = 0


@admin.register(FlightInstance)
class FlightInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "aircraft",
        "route",
        "flight_status",
        "departure_vertiport",
        "arrival_vertiport",
        "scheduled_departure_datetime",
        "scheduled_arrival_datetime",
    )
    list_filter = (
        "flight_status",
        "aircraft",
        "route",
        "departure_vertiport",
        "arrival_vertiport",
    )
    search_fields = (
        "aircraft__tail_number",
        "route__name",
        "departure_vertiport__vertiport_name",
        "arrival_vertiport__vertiport_name",
    )
    inlines = [TrackingInline]


# Tracking admin
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
        "updated_at",
    )
    list_filter = ("active", "flight_instance")
    search_fields = ("flight_instance__aircraft__tail_number",)


# Waypoint (registered separately)
@admin.register(Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "name",
        "latitude",
        "longitude",
        "altitude",
        "sequence_order",
        "vertiport",
    )
    list_filter = ("route", "vertiport")
    search_fields = ("name", "route__name", "vertiport__vertiport_name")


# Vertiport
@admin.register(Vertiport)
class VertiportAdmin(admin.ModelAdmin):
    list_display = (
        "vertiport_code",
        "vertiport_name",
        "latitude",
        "longitude",
        "altitude",
        "created_at",
    )
    search_fields = ("vertiport_code", "vertiport_name")
    list_filter = ("vertiport_code",)

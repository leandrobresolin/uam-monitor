from django.contrib import admin

from .models import (
    Aircraft,
    AircraftData,
    AircraftType,
    FlightInstance,
    Route,
    Tracking,
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
    list_display = ("tail_number", "model", "year")
    search_fields = ("tail_number", "model__name", "model__manufacturer")
    list_filter = ("model",)


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
    fields = ("name", "latitude", "longitude", "altitude", "sequence_order")


# Route model with inline waypoints
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
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
        "start_time",
        "end_time",
    )
    list_filter = ("flight_status", "aircraft", "route")
    search_fields = ("aircraft__tail_number", "route__name")
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


# Waypoint (registered separately if needed)
@admin.register(Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "name",
        "latitude",
        "longitude",
        "altitude",
        "sequence_order",
    )
    list_filter = ("route",)
    search_fields = ("name", "route__name")

from django.contrib import admin

from .models import Aircraft, AircraftData, AircraftType


@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "name", "energy_type", "model_type")


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ("tail_number", "model", "year")


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

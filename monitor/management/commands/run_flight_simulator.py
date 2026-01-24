# monitor/management/commands/run_flight_simulator.py
import time
from datetime import datetime
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand
from django.utils import timezone

from common_tools.schemas.flight_instance import FlightStatusEnum
from common_tools.schemas.tracking import SubmitTrackingSchema
from monitor.models import FlightInstance, Waypoint
from monitor.services.tracking import TrackingService

INTERVAL_SECONDS = 5
CRUISE_SPEED_KTS = 80.0
MIN_ENERGY = 20.0  # Reserve energy on landing


class Command(BaseCommand):
    help = "Flight simulator: generates Tracking for PENDING/ACTIVATED FlightInstances"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚁 Flight Simulator started"))
        tracking_service = TrackingService()

        while True:
            try:
                now = timezone.now()

                # 1) Activate PENDING flights whose departure time has arrived
                pendings = (
                    FlightInstance.objects.select_related(
                        "departure_vertiport",
                        "arrival_vertiport",
                        "route",
                    )
                    .prefetch_related("route__route_waypoints")
                    .filter(
                        flight_status=FlightStatusEnum.PENDING.value,
                        scheduled_departure_datetime__isnull=False,
                        scheduled_arrival_datetime__isnull=False,
                        scheduled_departure_datetime__lte=now,
                    )
                )

                for fi in pendings:
                    self._activate_flight(fi, tracking_service)

                # 2) Update ACTIVATED flights
                actives = (
                    FlightInstance.objects.select_related(
                        "departure_vertiport",
                        "arrival_vertiport",
                        "route",
                    )
                    .prefetch_related("route__route_waypoints")
                    .filter(
                        flight_status=FlightStatusEnum.ACTIVATED.value,
                        scheduled_departure_datetime__isnull=False,
                        scheduled_arrival_datetime__isnull=False,
                    )
                )

                for fi in actives:
                    self._update_flight(fi, now, tracking_service)

                self.stdout.write(
                    f"[{now.isoformat()}] PENDING={pendings.count()} ACTIVATED={actives.count()}"
                )

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("🛑 Simulator stopped"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Loop error: {e}"))

            time.sleep(INTERVAL_SECONDS)

    # -------------------------------------------------------------------------
    # Flight activation
    # -------------------------------------------------------------------------
    def _activate_flight(self, fi: FlightInstance, tracking_service: TrackingService):
        """Changes PENDING -> ACTIVATED and creates initial tracking at departure vertiport."""
        dep = fi.departure_vertiport
        arr = fi.arrival_vertiport

        if not dep or not arr:
            waypoints = fi.route.route_waypoints.order_by("sequence_order").all()
            if not waypoints:
                self.stdout.write(
                    self.style.WARNING(
                        f"[{fi.id}] route has no waypoints; skipping activation."
                    )
                )
                return

            if not dep:
                first_wp = waypoints[0]
                dep = first_wp.vertiport
                fi.departure_vertiport = dep
            if not arr:
                last_wp = waypoints.last()
                arr = last_wp.vertiport
                fi.arrival_vertiport = arr

            fi.save(update_fields=["departure_vertiport", "arrival_vertiport"])

        if not dep or not arr:
            self.stdout.write(
                self.style.WARNING(
                    f"[{fi.id}] still missing departure/arrival vertiport; skipping."
                )
            )
            return

        fi.flight_status = FlightStatusEnum.ACTIVATED.value
        fi.save(update_fields=["flight_status"])

        dep = fi.departure_vertiport
        aircraft_max_energy = fi.aircraft.energy_fuel

        # Round to realistic precision
        lat = round(float(dep.latitude), 6)
        lon = round(float(dep.longitude), 6)
        alt = round(float(dep.altitude), 1)

        payload = SubmitTrackingSchema(
            flight_instance=fi.id,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            speed=0.0,
            energy_level=aircraft_max_energy,
            active=True,
            started_at=None,
            finished_at=None,
            updated_at=None,
        )

        tracking_service.create_or_update_tracking(payload=payload)
        self.stdout.write(self.style.SUCCESS(f"✅ [{fi.id}] ACTIVATED"))

    # -------------------------------------------------------------------------
    # Flight update during simulation
    # -------------------------------------------------------------------------
    def _update_flight(
        self,
        fi: FlightInstance,
        now: datetime,
        tracking_service: TrackingService,
    ):
        aircraft_max_energy = fi.aircraft.energy_fuel
        dep_time = fi.scheduled_departure_datetime
        arr_time = fi.scheduled_arrival_datetime
        total_seconds = (arr_time - dep_time).total_seconds()
        if total_seconds <= 0:
            self.stdout.write(
                self.style.WARNING(f"[{fi.id}] invalid duration; terminating flight.")
            )
            self._terminate_flight(fi, now, tracking_service)
            return

        elapsed = (now - dep_time).total_seconds()
        progress = max(0.0, min(elapsed / total_seconds, 1.0))

        if progress >= 1.0:
            self._terminate_flight(fi, now, tracking_service)
            return

        path = self._build_path(fi)
        pos = self._interpolate_path(path, progress)

        # Monotonic decreasing energy: always decreases, never increases
        energy_raw = aircraft_max_energy - (aircraft_max_energy - MIN_ENERGY) * progress
        energy = round(energy_raw, 2)  # 2 decimal places precision

        # Round all values to realistic sensor precision
        lat = round(pos["lat"], 6)  # GPS ~1m
        lon = round(pos["lon"], 6)
        alt = round(pos["alt"], 1)  # 10cm
        speed = round(CRUISE_SPEED_KTS, 1)  # 0.1kt

        payload = SubmitTrackingSchema(
            flight_instance=fi.id,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            speed=speed,
            energy_level=energy,
            active=True,
            started_at=None,
            finished_at=None,
            updated_at=now,
        )

        tracking_service.create_or_update_tracking(payload=payload)
        self.stdout.write(
            f"📡 [{fi.id}] {progress:.0%} energy={energy}% speed={speed}kts"
        )

    # -------------------------------------------------------------------------
    # Flight termination
    # -------------------------------------------------------------------------
    def _terminate_flight(
        self,
        fi: FlightInstance,
        now: datetime,
        tracking_service: TrackingService,
    ):
        """Final tracking at arrival vertiport, sets TERMINATED status."""
        if fi.arrival_vertiport:
            arr = fi.arrival_vertiport
            lat = round(float(arr.latitude), 6)
            lon = round(float(arr.longitude), 6)
            alt = round(float(arr.altitude), 1)
        else:
            lat = lon = alt = 0.0

        payload = SubmitTrackingSchema(
            flight_instance=fi.id,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            speed=0.0,
            energy_level=MIN_ENERGY,
            active=False,
            started_at=None,
            finished_at=now,
            updated_at=now,
        )

        tracking_service.create_or_update_tracking(payload=payload)

        fi.flight_status = FlightStatusEnum.TERMINATED.value
        fi.save(update_fields=["flight_status"])

        self.stdout.write(self.style.SUCCESS(f"🛬 [{fi.id}] TERMINATED"))

    # -------------------------------------------------------------------------
    # Flight path geometry
    # -------------------------------------------------------------------------
    def _build_path(self, fi: FlightInstance) -> List[Tuple[float, float, float]]:
        """Builds flight path: departure → waypoints → arrival."""
        points: List[Tuple[float, float, float]] = []

        dep = fi.departure_vertiport
        arr = fi.arrival_vertiport
        if not dep or not arr:
            return [(0.0, 0.0, 1000.0)]

        # Departure vertiport
        points.append((float(dep.latitude), float(dep.longitude), float(dep.altitude)))

        # Route waypoints (ordered by sequence_order)
        if fi.route:
            waypoints = fi.route.route_waypoints.order_by("sequence_order").all()
            for wp in waypoints:
                lat = (
                    float(wp.latitude)
                    if wp.latitude is not None
                    else float(wp.vertiport.latitude)
                )
                lon = (
                    float(wp.longitude)
                    if wp.longitude is not None
                    else float(wp.vertiport.longitude)
                )
                alt = (
                    float(wp.altitude)
                    if wp.altitude is not None
                    else float(wp.vertiport.altitude)
                )
                points.append((lat, lon, alt))

        # Arrival vertiport
        points.append((float(arr.latitude), float(arr.longitude), float(arr.altitude)))

        # Ensure minimum 2 points for interpolation
        if len(points) == 1:
            points.append(points[0])

        return points

    def _interpolate_path(
        self, path: List[Tuple[float, float, float]], progress: float
    ) -> Dict[str, float]:
        """Linear interpolation across path segments."""
        if len(path) == 1:
            lat, lon, alt = path[0]
            return {"lat": lat, "lon": lon, "alt": alt}

        # Map global progress (0-1) to segments
        seg_count = len(path) - 1
        seg_pos = progress * seg_count
        seg_idx = min(int(seg_pos), seg_count - 1)
        seg_t = seg_pos - seg_idx

        lat1, lon1, alt1 = path[seg_idx]
        lat2, lon2, alt2 = path[seg_idx + 1]

        lat = lat1 + (lat2 - lat1) * seg_t
        lon = lon1 + (lon2 - lon1) * seg_t
        alt = alt1 + (alt2 - alt1) * seg_t

        return {"lat": lat, "lon": lon, "alt": alt}

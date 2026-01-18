# monitor/management/commands/run_flight_simulator.py
import asyncio
import math
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.utils import timezone

from monitor.models import FlightInstance, Tracking  # Ajuste imports


class Command(BaseCommand):
    help = "Simula voos de FlightInstances pendentes"

    def handle(self, *args, **options):
        print("🚁 Flight Simulator iniciado (Ctrl+C para parar)")
        asyncio.run(self.simulation_loop())

    async def simulation_loop(self):
        while True:
            try:
                now = timezone.now()

                # 1. Ativa pendentes
                pendings = await sync_to_async(list)(
                    FlightInstance.objects.filter(
                        flight_status="PENDING", scheduled_departure_datetime__lte=now
                    )
                    .select_related(
                        "aircraft", "departure_vertiport", "arrival_vertiport", "route"
                    )
                    .prefetch_related("route__waypoints")
                )

                for fi in pendings:
                    await self.activate_flight(fi)

                # 2. Atualiza ativas
                actives = await sync_to_async(list)(
                    FlightInstance.objects.filter(flight_status="ACTIVATED")
                )

                for fi in actives:
                    await self.update_tracking(fi, now)

                print(
                    f"⏱️  {len(pendings)} pendings | {len(actives)} ativas | Próxima: 5s"
                )

            except KeyboardInterrupt:
                print("\n🛑 Simulator parado")
                break
            except Exception as e:
                print(f"❌ Erro loop: {e}")

            await asyncio.sleep(5)

    @sync_to_async
    def activate_flight(self, fi: FlightInstance):
        if fi.flight_status != "PENDING":
            return

        fi.flight_status = "ACTIVATED"
        fi.save(update_fields=["flight_status"])

        # Cria tracking inicial
        tracking, created = Tracking.objects.get_or_create(
            flight_instance=fi,
            defaults={
                "latitude": fi.departure_vertiport.latitude,
                "longitude": fi.departure_vertiport.longitude,
                "altitude": fi.departure_vertiport.altitude,
                "speed": Decimal("0.0"),
                "energy_level": Decimal("100.0"),
                "active": True,
                "started_at": timezone.now(),
            },
        )
        print(f"✅ [{fi.id}] ATIVATED (criado: {created})")

    async def update_tracking(self, fi: FlightInstance, now: datetime):
        duration = (
            fi.scheduled_arrival_datetime - fi.scheduled_departure_datetime
        ).total_seconds()
        if duration <= 0:
            return

        elapsed = (now - fi.scheduled_departure_datetime).total_seconds()
        progress = min(elapsed / duration, 1.0)

        if progress >= 1.0:
            await self.finish_flight(fi)
            return

        # Build path
        path = self.build_path(fi)
        pos = self.interpolate_path(path, progress)

        # Consumo realista
        energy = max(15.0, 100.0 * (1 - progress * 0.85))
        speed = min(80.0, 20.0 + progress * 60.0)  # Acelera gradualmente

        # Update tracking
        tracking = await sync_to_async(Tracking.objects.get)(flight_instance=fi)
        tracking.latitude = pos["lat"]
        tracking.longitude = pos["lon"]
        tracking.altitude = pos["alt"]
        tracking.speed = Decimal(f"{speed:.1f}")
        tracking.energy_level = Decimal(f"{energy:.1f}")
        tracking.updated_at = now
        tracking.save(
            update_fields=[
                "latitude",
                "longitude",
                "altitude",
                "speed",
                "energy_level",
                "updated_at",
            ]
        )

        print(f"📡 [{fi.id}] {progress:.0%} | {energy:.0f}% | {speed:.0f}kts")

    @sync_to_async
    def finish_flight(self, fi: FlightInstance):
        fi.flight_status = "TERMINATED"
        fi.save(update_fields=["flight_status"])

        tracking = Tracking.objects.get(flight_instance=fi)
        tracking.active = False
        tracking.finished_at = timezone.now()
        tracking.save(update_fields=["active", "finished_at"])

        print(f"🛬 [{fi.id}] TERMINATED")

    def build_path(self, fi: FlightInstance) -> List[Tuple[float, float, float]]:
        points = []

        # Origem
        points.append(
            (
                float(fi.departure_vertiport.latitude),
                float(fi.departure_vertiport.longitude),
                float(fi.departure_vertiport.altitude),
            )
        )

        # Waypoints
        if fi.route and fi.route.waypoints.exists():
            for wp in fi.route.waypoints.order_by("sequence_order"):
                points.append(
                    (float(wp.latitude), float(wp.longitude), float(wp.altitude))
                )

        # Destino
        points.append(
            (
                float(fi.arrival_vertiport.latitude),
                float(fi.arrival_vertiport.longitude),
                float(fi.arrival_vertiport.altitude),
            )
        )

        return points

    def interpolate_path(
        self, path: List[Tuple[float, float, float]], progress: float
    ) -> Dict[str, float]:
        if len(path) == 1:
            return {"lat": path[0][0], "lon": path[0][1], "alt": path[0][2]}

        seg_idx = min(int(progress * (len(path) - 1)), len(path) - 2)
        seg_prog = (progress * (len(path) - 1)) - seg_idx

        p1, p2 = path[seg_idx], path[seg_idx + 1]
        return {
            "lat": p1[0] + (p2[0] - p1[0]) * seg_prog,
            "lon": p1[1] + (p2[1] - p1[1]) * seg_prog,
            "alt": p1[2] + (p2[2] - p1[2]) * seg_prog,
        }

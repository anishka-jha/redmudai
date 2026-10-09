"""Illustrative, uncalibrated batch filtration surrogate; SI units internally."""
from dataclasses import dataclass, asdict
import math

GOALS = ('Max recovery', 'Min energy', 'Balanced')

@dataclass(frozen=True)
class Result:
    solids_kg: float
    initial_water_kg: float
    recovered_water_kg: float
    cake_water_kg: float
    cake_mass_kg: float
    recovery_pct: float
    moisture_pct: float
    energy_kwh: float
    pressure_bar: float
    time_min: float

def simulate(solids_pct, quantity_kg, pressure_bar, time_min):
    values = (solids_pct, quantity_kg, pressure_bar, time_min)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Inputs must be finite.')
    if not (5 <= solids_pct <= 60 and 1 <= quantity_kg <= 100000
            and 0.5 <= pressure_bar <= 10 and 1 <= time_min <= 120):
        raise ValueError('Inputs outside demonstration bounds.')
    solids = quantity_kg * solids_pct / 100
    water = quantity_kg - solids
    # Arbitrary retained-water floor: 0.35 kg water / kg dry solids.
    removable = max(0, water - 0.35 * solids)
    # Fixed filter area/loading as batch size changes; invented kinetic constant.
    tau = 18 * (solids_pct / 30)**1.5 * (quantity_kg / 1000)**0.5
    fraction = -math.expm1(-time_min * math.sqrt(pressure_bar) / tau)
    recovered = removable * fraction
    retained = water - recovered
    cake = solids + retained
    # Pressure-volume work / assumed efficiency + invented auxiliary power.
    hydraulic = pressure_bar * 1e5 * (recovered / 1000) / (0.6 * 3.6e6)
    auxiliary = 0.25 * time_min / 60
    return Result(solids, water, recovered, retained, cake,
                  100 * recovered / water, 100 * retained / cake,
                  hydraulic + auxiliary, pressure_bar, time_min)

def candidates(solids_pct, quantity_kg):
    return [simulate(solids_pct, quantity_kg, 0.5 + p * 0.5, t)
            for p in range(20) for t in range(5, 121, 5)]

def optimize(solids_pct, quantity_kg, goal):
    rows = candidates(solids_pct, quantity_kg)
    best_recovery = max(r.recovery_pct for r in rows)
    if goal == 'Max recovery':
        return max(rows, key=lambda r: (r.recovery_pct, -r.energy_kwh))
    if goal == 'Min energy':
        # Constrained objective prevents the trivial no-filtration solution.
        feasible = [r for r in rows if r.recovery_pct >= 0.8 * best_recovery]
        return min(feasible, key=lambda r: r.energy_kwh)
    if goal != 'Balanced':
        raise ValueError('Unknown optimization goal.')
    energies = [r.energy_kwh for r in rows]
    lo, hi = min(energies), max(energies)
    return max(rows, key=lambda r: 0.65 * r.recovery_pct / best_recovery
               - 0.35 * (r.energy_kwh - lo) / (hi - lo))

def to_dict(result):
    return asdict(result)

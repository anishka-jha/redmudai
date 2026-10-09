import unittest
from model import simulate, optimize, candidates, GOALS

class ModelTests(unittest.TestCase):
    def test_balance_bounds_and_monotonicity(self):
        for s in (5,30,60):
            for q in (1,1000,100000):
                previous = -1
                for t in (1,5,30,120):
                    r = simulate(s,q,3,t)
                    self.assertAlmostEqual(q,r.cake_mass_kg+r.recovered_water_kg)
                    self.assertAlmostEqual(r.initial_water_kg,r.cake_water_kg+r.recovered_water_kg)
                    self.assertGreaterEqual(r.cake_water_kg,0.35*r.solids_kg-1e-8)
                    self.assertTrue(0 <= r.recovery_pct <= 100)
                    self.assertTrue(0 <= r.moisture_pct <= 100)
                    self.assertGreaterEqual(r.recovered_water_kg,previous)
                    previous=r.recovered_water_kg
                self.assertGreaterEqual(simulate(s,q,10,30).recovery_pct,simulate(s,q,.5,30).recovery_pct)

    def test_goals(self):
        for s,q in ((30,1000),(5,1),(60,100000)):
            rows=candidates(s,q)
            maximum=max(r.recovery_pct for r in rows)
            self.assertEqual(optimize(s,q,GOALS[0]).recovery_pct,maximum)
            feasible=[r for r in rows if r.recovery_pct >= .8*maximum]
            self.assertEqual(optimize(s,q,GOALS[1]).energy_kwh,min(r.energy_kwh for r in feasible))
            selected=optimize(s,q,GOALS[2])
            lo=min(r.energy_kwh for r in rows); hi=max(r.energy_kwh for r in rows)
            score=lambda r: .65*r.recovery_pct/maximum-.35*(r.energy_kwh-lo)/(hi-lo)
            self.assertEqual(score(selected),max(map(score,rows)))

    def test_invalid(self):
        for args in ((0,1000,3,30),(30,-1,3,30),(30,1000,0,30),(30,1000,3,float('nan'))):
            with self.assertRaises(ValueError): simulate(*args)

if __name__ == '__main__': unittest.main()

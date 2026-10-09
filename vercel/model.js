// Exact counterpart of the illustrative Python model. No trained AI.
function simulate(s,q,p,t) {
  if (![s,q,p,t].every(Number.isFinite) || s<5 || s>60 || q<1 || q>100000 || p<.5 || p>10 || t<1 || t>120) throw Error('Inputs outside demonstration bounds');
  const solids=q*s/100, water=q-solids, removable=Math.max(0,water-.35*solids);
  const tau=18*(s/30)**1.5*(q/1000)**.5;
  const recovered=removable*(-Math.expm1(-t*Math.sqrt(p)/tau));
  const retained=water-recovered, cake=solids+retained;
  return {solids_kg:solids, initial_water_kg:water, recovered_water_kg:recovered, cake_water_kg:retained, cake_mass_kg:cake, recovery_pct:100*recovered/water, moisture_pct:100*retained/cake, energy_kwh:p*1e5*(recovered/1000)/(.6*3.6e6)+.25*t/60, pressure_bar:p,time_min:t};
}
function candidates(s,q) {
  const rows=[];
  for(let p=.5;p<=10;p+=.5) for(let t=5;t<=120;t+=5) rows.push(simulate(s,q,p,t));
  return rows;
}
function optimize(s,q,goal) {
  const rows=candidates(s,q), best=Math.max(...rows.map(r=>r.recovery_pct));
  if(goal==='Max recovery') return rows.reduce((a,b)=>b.recovery_pct>a.recovery_pct?b:a);
  if(goal==='Min energy') return rows.filter(r=>r.recovery_pct>=.8*best).reduce((a,b)=>b.energy_kwh<a.energy_kwh?b:a);
  if(goal!=='Balanced') throw Error('Unknown goal');
  const lo=Math.min(...rows.map(r=>r.energy_kwh)), hi=Math.max(...rows.map(r=>r.energy_kwh));
  const score=r=>.65*r.recovery_pct/best-.35*(r.energy_kwh-lo)/(hi-lo);
  return rows.reduce((a,b)=>score(b)>score(a)?b:a);
}
if(typeof module!=='undefined') module.exports={simulate,optimize,candidates};

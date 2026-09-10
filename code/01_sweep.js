#!/usr/bin/env node
/* Experiment runner for the Lunar Farm bioregenerative model.

   This file does not reimplement the simulation. It loads farm/js/data.js and
   farm/js/sim.js from the game itself and drives them, so every number in this
   repository is a measurement of the code that ships. Math.random is replaced
   with a seeded LCG, making every run reproducible from its seed alone.

   Usage:  node 01_sweep.js [experiment ...]     (default: all)
   Output: ../data/<experiment>.csv
*/

const fs = require('fs');
const path = require('path');

const GAME = process.env.LUNARFARM_DIR
  || path.resolve(__dirname, '../../LunarSims/farm');
const OUT = path.resolve(__dirname, '../data');

function loadSim() {
  global.window = {};
  eval(fs.readFileSync(path.join(GAME, 'js/data.js'), 'utf8'));
  eval(fs.readFileSync(path.join(GAME, 'js/sim.js'), 'utf8'));
  return { S: global.window.LF_SIM, D: global.window.LF_DATA };
}
const { S, D } = loadSim();

const seed = n => { let a = n >>> 0; Math.random = () => { a = (a * 1664525 + 1013904223) >>> 0; return a / 4294967296; }; };
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;

/* ---------- a scripted farm manager ----------

   One policy, used by every experiment, so arms differ only in the factor under
   test. It tends, harvests, replants from a rotation and restocks — deliberately
   competent and deliberately not clever.

   With cfg.stochastic the policy stops being deterministic in two ways that
   matter. The event deck is answered rather than suppressed, so a run meets the
   flares, infections and broker offers a player would; and the manager's own
   thresholds are jittered per run, with a chance of skipping a day's tending
   entirely. Without this the seeds test reproducibility, because the deck was
   the model's only stochastic element.

   Answering the deck uniformly at random is not a player and does not model
   one: it never patches a hull, so pressure walks down to the abort limit, and
   it takes the broker's offer to sell the larder down to a twelve-day reserve.
   Every run of a first attempt died that way, most inside a month. The manager
   here takes the remedial choice — conventionally the first offered — with
   probability REMEDIAL and picks freely otherwise, which is a competent
   operator having an occasional bad day rather than a coin toss with a farm. */
const REMEDIAL = 0.75;
function run(cfg) {
  seed(cfg.seed);
  const s = S.newGame();
  /* drawn once per run, so each seed is a slightly different manager */
  const jit = cfg.stochastic
    ? { wet: 0.30 + Math.random() * 0.18, feed: 0.25 + Math.random() * 0.17,
        skip: Math.random() * 0.10 }
    : { wet: 0.4, feed: 0.35, skip: 0 };
  s.credits = cfg.credits === undefined ? 400000 : cfg.credits;
  s.science = 400;
  if (cfg.food) s.food = cfg.food;
  if (cfg.offtake) s.offtake = true;

  const spots = [[13, 7], [14, 7], [11, 7], [10, 7], [15, 7]];
  (cfg.compartments || []).forEach((t, i) => {
    const e = S.place(s, S.tileAt(s, spots[i][0], spots[i][1]), t);
    if (e) throw new Error('could not place ' + t + ': ' + e);
  });

  /* lay out halls on the track spine so service is not a hidden factor */
  let made = 0;
  for (let y = 0; y < D.K.ROWS && made < (cfg.halls || 8); y++) {
    for (let x = 0; x < D.K.COLS && made < (cfg.halls || 8); x++) {
      if (S.checkField(s, x, y, 3, 3)) continue;
      if (S.addField(s, x, y, 3, 3)) continue;
      for (let i = 0; i < 3; i++) {
        const t = S.tileAt(s, x + i, y + 3);
        if (t && !t.b && !t.f) S.place(s, t, 'track');
      }
      made++;
    }
  }
  if (cfg.workedBeds) s.fields.forEach(f => { f.soil = 1; });

  const mix = cfg.mix;
  let rot = 0;
  const series = [];
  let co2Floor = Infinity, shed = [], brokeRun = 0, brokeWorst = 0;

  for (let d = 0; d < (cfg.days || 300) && !s.over; d++) {
    for (let h = 0; h < 24; h++) {
      S.tick(s);
      if (s.pendingEvent) {
        if (cfg.stochastic) {
          const e = D.EVENTS.find(x => x.id === s.pendingEvent);
          if (e) {
            const pick = Math.random() < REMEDIAL
              ? e.choices[0]
              : e.choices[Math.floor(Math.random() * e.choices.length)];
            S.resolveEvent(s, e.id, pick.effect);
          } else s.pendingEvent = null;
        } else s.pendingEvent = null;
      }
      if (s.wantFields > 0) shed.push(1 - s.litFields / s.wantFields);
      if (s.over) break;
    }
    if (s.over) break;
    const tended = !(cfg.stochastic && Math.random() < jit.skip);
    if (tended) for (const f of S.planted(s)) {
      if (f.moisture < jit.wet) S.water(s, f);
      if (f.feed < jit.feed) S.feed(s, f);
      if (f.growth >= 1) S.harvest(s, f);
    }
    s.fields.forEach(f => { if (!f.crop && !f.dead) { S.plant(s, f, mix[rot % mix.length]); rot++; } });
    if (s.water < 400 && s.credits > 2000) S.trade(s, 'water', 200);
    if (s.nutrients < 200 && s.credits > 2000) S.trade(s, 'nutrients', 200);
    if (cfg.buyCO2 && s.co2 < 45 && s.credits > 2000) S.trade(s, 'co2', 40);
    /* a farm without a deep pantry buys rations when the store runs down, the
       way the game's own auto-manage does */
    if (cfg.restock && s.food < S.dailyNeed(s) * 12 && s.credits > 2000) S.trade(s, 'food', 30000);

    /* The carbon and night experiments answer a question that starvation timing
       would otherwise end the run before reaching, so they hold food
       non-limiting by construction — the same control as worked beds, and
       necessary once the deck is live, because the broker's resupply offer will
       otherwise sell the larder down to a twelve-day reserve and reintroduce
       exactly the confound the deep pantry was there to remove. */
    if (cfg.holdFood) s.food = Math.max(s.food, cfg.food || 6e6);

    co2Floor = Math.min(co2Floor, s.co2);
    if (s.credits < 1500) { brokeRun++; brokeWorst = Math.max(brokeWorst, brokeRun); } else brokeRun = 0;
    series.push({
      day: s.day, co2: s.co2, o2: s.o2, water: s.water, nutrients: s.nutrients,
      residue: s.residue, waste: s.waste, credits: s.credits,
      food_days: s.food / Math.max(1, S.dailyNeed(s)),
      closure: s.stats.lastClosure, ls_share: s.stats.lsShare || 0,
      audience: s.media.audience, harvests: s.stats.harvests,
      kinds: Object.keys(s.stats.kinds).length
    });
  }

  return {
    survived: !s.over, end_day: s.day, failure: s.over || '',
    co2_floor: co2Floor === Infinity ? 0 : co2Floor,
    co2_mean: mean(series.map(r => r.co2)),
    o2_mean: mean(series.map(r => r.o2)),
    closure_mean: mean(series.map(r => r.closure)),
    ls_share_mean: mean(series.map(r => r.ls_share)),
    shed_mean: mean(shed),
    harvests: s.stats.harvests,
    kinds: Object.keys(s.stats.kinds).length,
    accessions: S.accessions(s).length,
    credits_end: s.credits,
    media_total: s.stats.mediaTotal || 0,
    service_total: s.stats.serviceTotal || 0,
    waste_processed: s.stats.wasteProcessed || 0,
    broke_worst: brokeWorst,
    series
  };
}

/* ---------- rotations ---------- */
const PLANTS = ['potato', 'romaine', 'radish', 'wheat', 'pakchoi', 'zinnia', 'duckweed', 'kale', 'onion', 'sweetpotato'];
const FUNGAL = ['potato', 'romaine', 'oyster', 'wheat', 'pakchoi', 'oyster', 'duckweed', 'kale', 'onion', 'sweetpotato'];
const ALGAL  = ['potato', 'romaine', 'spirulina', 'wheat', 'pakchoi', 'spirulina', 'duckweed', 'kale', 'onion', 'sweetpotato'];
const SEEDS = [1, 2, 3, 4, 5, 6, 7, 8].map(n => n * 104729);
const SEEDS12 = Array.from({ length: 12 }, (_, i) => (i + 1) * 60013);

function writeCSV(name, rows) {
  if (!rows.length) return;
  const cols = Object.keys(rows[0]);
  const esc = v => typeof v === 'string' && /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  const csv = [cols.join(',')].concat(rows.map(r => cols.map(c => esc(r[c])).join(','))).join('\n');
  fs.writeFileSync(path.join(OUT, name), csv + '\n');
  console.log('  wrote data/' + name, '(' + rows.length + ' rows)');
}

/* ---------- E1: what stabilises the carbon loop ---------- */
function E1() {
  console.log('E1 carbon stability');
  const arms = [
    ['none', [], PLANTS], ['worms', ['worms'], PLANTS],
    ['nitrifier', ['nitrifier'], PLANTS], ['digester', ['digester'], PLANTS],
    ['composter_only', [], PLANTS],
    ['all_four', ['worms', 'nitrifier', 'digester', 'reef'], PLANTS],
    ['fungal_rotation', [], FUNGAL], ['algal_rotation', [], ALGAL]
  ];
  const rows = [], traces = [];
  for (const [arm, comp, mix] of arms) {
    for (const sd of SEEDS) {
      /* deep pantry and worked beds: a naive comparison of this system is
         confounded by starvation timing and by raw-regolith growth, both of
         which end the run before the carbon question is answered */
      const r = run({ seed: sd, compartments: comp, mix, days: 300,
                      food: 6e6, workedBeds: true, buyCO2: false, halls: 8 });
      rows.push({ arm, seed: sd, survived: r.survived ? 1 : 0, end_day: r.end_day,
                  co2_floor: r.co2_floor, co2_mean: r.co2_mean, o2_mean: r.o2_mean,
                  harvests: r.harvests, closure_mean: r.closure_mean, failure: r.failure });
      if (sd === SEEDS[0]) r.series.forEach(p => traces.push({ arm, day: p.day, co2: p.co2, o2: p.o2 }));
    }
  }
  writeCSV('e1_carbon.csv', rows);
  writeCSV('e1_traces.csv', traces);
}

/* ---------- E2: does variety actually pay ---------- */
function E2() {
  console.log('E2 diversity economics');
  const rows = [];
  for (let breadth = 1; breadth <= 10; breadth++) {
    for (const studio of [0, 1]) {
      for (const sd of SEEDS.slice(0, 5)) {
        const mix = PLANTS.slice(0, breadth);
        const r = run({ seed: sd, compartments: studio ? ['studio'] : [], mix,
                        days: 240, food: 6e6, workedBeds: true, buyCO2: true, halls: 6 });
        rows.push({ breadth, studio, seed: sd, media_total: r.media_total,
                    service_total: r.service_total, credits_end: r.credits_end,
                    kinds: r.kinds, accessions: r.accessions, harvests: r.harvests });
      }
    }
  }
  writeCSV('e2_diversity.csv', rows);
}

/* ---------- E3: knock each compartment out ---------- */
function E3() {
  console.log('E3 compartment knockout');
  const all = ['worms', 'nitrifier', 'digester', 'reef'];
  const rows = [];
  const arms = [['none', []], ['all', all]]
    .concat(all.map(t => ['only_' + t, [t]]))
    .concat(all.map(t => ['without_' + t, all.filter(x => x !== t)]));
  for (const [arm, comp] of arms) {
    for (const sd of SEEDS.slice(0, 5)) {
      const r = run({ seed: sd, compartments: comp, mix: PLANTS, days: 260,
                      food: 6e6, workedBeds: true, buyCO2: false, offtake: true, halls: 8 });
      rows.push({ arm, seed: sd, co2_floor: r.co2_floor, co2_mean: r.co2_mean,
                  o2_mean: r.o2_mean, closure_mean: r.closure_mean,
                  ls_share_mean: r.ls_share_mean, waste_processed: r.waste_processed,
                  service_total: r.service_total, credits_end: r.credits_end,
                  harvests: r.harvests, survived: r.survived ? 1 : 0 });
    }
  }
  writeCSV('e3_knockout.csv', rows);
}

/* ---------- E4: the dark-grown fraction and the lunar night ---------- */
function E4() {
  console.log('E4 night resilience');
  const rows = [];
  for (const darkFrac of [0, 0.2, 0.4, 0.6, 0.8, 1.0]) {
    for (const batteries of [0, 3]) {
      for (const sd of SEEDS.slice(0, 5)) {
        const n = 10;
        const mix = [];
        for (let i = 0; i < n; i++) mix.push(i < Math.round(darkFrac * n) ? 'oyster' : 'romaine');
        const cfg = { seed: sd, compartments: [], mix, days: 200, food: 6e6,
                      workedBeds: true, buyCO2: true, halls: 8 };
        /* batteries are placed by hand so the power budget is the only factor */
        seed(sd);
        const r = (() => {
          const saved = cfg.batteries;
          cfg.batteries = batteries;
          return runWithBatteries(cfg, batteries);
        })();
        rows.push({ dark_frac: darkFrac, batteries, seed: sd, shed_mean: r.shed_mean,
                    harvests: r.harvests, survived: r.survived ? 1 : 0,
                    co2_mean: r.co2_mean, end_day: r.end_day });
      }
    }
  }
  writeCSV('e4_night.csv', rows);
}

/* batteries need placing before the halls take the free ground */
function runWithBatteries(cfg, batteries) {
  const orig = S.newGame;
  S.newGame = function () {
    const s = orig.call(S);
    let placed = 0;
    for (let y = 0; y < D.K.ROWS && placed < batteries; y++) {
      for (let x = 0; x < D.K.COLS && placed < batteries; x++) {
        const t = S.tileAt(s, x, y);
        if (t && !t.b && !t.f && t.t === 'flat' && !S.canPlace(s, t, 'battery', true)) {
          if (!S.place(s, t, 'battery')) placed++;
        }
      }
    }
    return s;
  };
  try { return run(cfg); } finally { S.newGame = orig; }
}

/* ---------- E5: the same economics question, with the deck live ---------- */
function E5() {
  console.log('E5 diversity economics under a stochastic policy');
  const rows = [];
  for (let breadth = 1; breadth <= 10; breadth++) {
    for (const sd of SEEDS12) {
      const mix = PLANTS.slice(0, breadth);
      const r = run({ seed: sd, compartments: ['studio'], mix, days: 240,
                      workedBeds: true, buyCO2: true, halls: 6, restock: true,
                      stochastic: true });
      rows.push({ breadth, seed: sd, media_total: r.media_total,
                  service_total: r.service_total, credits_end: r.credits_end,
                  kinds: r.kinds, harvests: r.harvests,
                  survived: r.survived ? 1 : 0, end_day: r.end_day });
    }
  }
  writeCSV('e5_diversity_stochastic.csv', rows);
}

/* ---------- E6-E8: E1, E3 and E4 again, with the deck live ----------

   Same arms, same measurements, same seeds; the only change is the policy. If a
   conclusion drawn from a deterministic trajectory does not survive twelve
   noisy operators, it was a property of the manager rather than of the loop. */

function E6() {
  console.log('E6 carbon stability under a stochastic policy');
  const arms = [
    ['none', [], PLANTS], ['worms', ['worms'], PLANTS],
    ['nitrifier', ['nitrifier'], PLANTS], ['digester', ['digester'], PLANTS],
    ['all_four', ['worms', 'nitrifier', 'digester', 'reef'], PLANTS],
    ['fungal_rotation', [], FUNGAL], ['algal_rotation', [], ALGAL]
  ];
  const rows = [];
  for (const [arm, comp, mix] of arms) {
    for (const sd of SEEDS12) {
      const r = run({ seed: sd, compartments: comp, mix, days: 300,
                      food: 6e6, holdFood: true, workedBeds: true,
                      buyCO2: false, halls: 8, stochastic: true });
      rows.push({ arm, seed: sd, survived: r.survived ? 1 : 0, end_day: r.end_day,
                  co2_floor: r.co2_floor, co2_mean: r.co2_mean, o2_mean: r.o2_mean,
                  harvests: r.harvests, failure: r.failure });
    }
  }
  writeCSV('e6_carbon_stochastic.csv', rows);
}

function E7() {
  console.log('E7 compartment knockout under a stochastic policy');
  const all = ['worms', 'nitrifier', 'digester', 'reef'];
  const arms = [['none', []], ['all', all]]
    .concat(all.map(t => ['only_' + t, [t]]))
    .concat(all.map(t => ['without_' + t, all.filter(x => x !== t)]));
  const rows = [];
  for (const [arm, comp] of arms) {
    for (const sd of SEEDS12) {
      const r = run({ seed: sd, compartments: comp, mix: PLANTS, days: 260,
                      food: 6e6, holdFood: true, workedBeds: true, buyCO2: false,
                      offtake: true, halls: 8, stochastic: true });
      rows.push({ arm, seed: sd, co2_floor: r.co2_floor, co2_mean: r.co2_mean,
                  ls_share_mean: r.ls_share_mean, waste_processed: r.waste_processed,
                  service_total: r.service_total, harvests: r.harvests,
                  survived: r.survived ? 1 : 0, end_day: r.end_day });
    }
  }
  writeCSV('e7_knockout_stochastic.csv', rows);
}

function E8() {
  console.log('E8 night resilience under a stochastic policy');
  const rows = [];
  for (const darkFrac of [0, 0.2, 0.4, 0.6, 0.8, 1.0]) {
    for (const batteries of [0, 3]) {
      for (const sd of SEEDS12) {
        const n = 10, mix = [];
        for (let i = 0; i < n; i++) mix.push(i < Math.round(darkFrac * n) ? 'oyster' : 'romaine');
        const r = runWithBatteries({ seed: sd, compartments: [], mix, days: 200,
                                     food: 6e6, holdFood: true, workedBeds: true,
                                     buyCO2: true, halls: 8, stochastic: true }, batteries);
        rows.push({ dark_frac: darkFrac, batteries, seed: sd, shed_mean: r.shed_mean,
                    harvests: r.harvests, survived: r.survived ? 1 : 0,
                    co2_mean: r.co2_mean, o2_mean: r.o2_mean,
                    end_day: r.end_day, failure: r.failure });
      }
    }
  }
  writeCSV('e8_night_stochastic.csv', rows);
}

const which = process.argv.slice(2);
const ALL = { E1, E2, E3, E4, E5, E6, E7, E8 };
const todo = which.length ? which : Object.keys(ALL);
console.log('Lunar Farm BLSS sweep — driving', GAME);
for (const k of todo) {
  if (!ALL[k]) { console.error('unknown experiment', k); continue; }
  const t = Date.now();
  ALL[k]();
  console.log('  ' + k + ' done in ' + ((Date.now() - t) / 1000).toFixed(1) + 's');
}

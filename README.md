# ISS Crew Ultrasound Phantom Verification Twin
**Simulation study — no new experimental data.** Nominal stiffness targets (~5 kPa, ~27 kPa) are inspired by my Hele Imua tissue-mimicking phantom work; every sensitivity coefficient and distribution in `src/twin.py` is an *assumed/estimated* value from typical ranges and is labeled as such.

## Problem
Portable ultrasound on ISS needs an in-flight calibration check. A gel phantom must survive shipping, sit in a 18.5–26.7 °C cabin, and be scanned by a minimally trained crew member. Which process variables break calibration?

## Approach
- Monte Carlo (20,000 draws/phantom) over cool-down setpoint error, gel-uniformity proxy (CV), shipping vibration (0.5–6 gRMS), cabin temperature, and probe preload strain.
- Apparent E = true E × temperature effects × nonlinear preload stiffening × inhomogeneity noise × uncorrected speed-of-sound scaling.
- Variance attribution with squared standardized regression coefficients; mitigated scenario = standoff/force-limited preload (~1% strain) + 80% cabin-temp correction.
- Systems traceability: `VERIFICATION_MATRIX.md`.

## Results (simulated)
| Phantom | Median bias | p95 abs error | Pass ±10% baseline | Pass mitigated |
|---|---|---|---|---|
| 5 kPa | +10.8% | 32.0% | 45% | 85% |
| 27 kPa | +11.0% | 32.4% | 45% | 84% |
- Probe preload explains ~68% of explained variance, cabin temperature ~21%, cool-down ~11%.
- Predicted shear-wave speeds: 1.33 m/s (5 kPa), 3.10 m/s (27 kPa).
- Takeaway: a preload-limiting standoff is the highest-value design control; even mitigated, 85% < 95% requirement, so cure-temp control and on-board temperature correction are also required.

Figures: `figures/fig1_calibration_error_mc.png`, `figures/fig2_sensitivity_tornado.png`. Table: `docs/results_summary.csv`.

## Run
`pip install -r requirements.txt && python3 src/twin.py`

## Limitations
- Coefficients are assumptions, not fitted to measurements; next step is to fit them with real phantom data (thermal sweeps, preload sweeps).
- Linear SRC attribution cannot see zero-mean multiplicative noise, so uniformity/vibration show ~0 share even though they widen the spread; a variance-based Sobol analysis is the right upgrade.
- No real microgravity effects (bubble migration, fluid shift in gel) modeled.

## License
MIT — see `LICENSE`.

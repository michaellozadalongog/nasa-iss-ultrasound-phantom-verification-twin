Can a crew member with minimal training trust an ultrasound stiffness reading on the ISS? I built a simulation to find out which process variables break phantom calibration in flight.

What I built: a Monte Carlo verification twin (20,000 draws per phantom) for tissue-mimicking gel phantoms at ~5 kPa and ~27 kPa. The stiffness targets come from my Hele Imua phantom work. It varies cool-down setpoint error, gel uniformity, shipping vibration (0.5–6 gRMS), cabin temperature (18.5–26.7 °C), and probe preload strain. Requirements trace through a verification matrix.

Key results (simulated):
• Baseline: about +11% median bias, about 32% p95 error, and only about 45% of scans within ±10%
• Probe preload explains about 68% of explained variance, cabin temperature about 21%, cool-down about 11%
• A force-limiting standoff plus cabin-temperature correction raises pass rate to 84–85%, still short of a 95% requirement. Cure-temperature control and on-board temperature correction are also needed.

Limitations: every coefficient is assumed, not fitted to measurements, and microgravity gel effects are not modeled. Next I want to fit the model to real thermal and preload sweeps on physical phantoms and replace the linear attribution with a Sobol variance analysis.

I'm a biomedical engineering student at Hawaiʻi Pacific University looking for a NASA OSTEM internship for Summer 2027 in crew health, medical systems, or verification engineering. If you work in that space, I'd value your feedback on the approach.

Code + figures: https://github.com/michaellozadalongog/nasa-iss-ultrasound-phantom-verification-twin

📎 Attached: fig1_calibration_error_mc.png (calibration error distributions), fig2_sensitivity_tornado.png (variance attribution)

#NASA #BiomedicalEngineering #Ultrasound #SystemsEngineering #MonteCarlo

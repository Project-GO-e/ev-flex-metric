# EV Flex Metric calculation tool

This tool has been created during the [GO-e](https://www.projectgo-e.nl/) project.

## Quickstart
```bash
./setup.sh                                         # Downloads and sets up all the necessary Python dependencies in the .venv/ folder
cp packages_files/sample_config.toml ./config.toml # Copy the sample config. Change any parameters as you see fit.
./run.sh                                           # Run a calculation. 
```

## What this tool calculates
This tool can calculate the 'shifted' energy profiles for EV charge sessions. Shifted in this context means
that as much energy flexibility is used during the congestion period. The energy is moved from the congestion
period to just after the congestion period. Current implementation moves the energy to be charged as quickly
as possible after the congestion has ended and does not spread it evenly across remaining charge session. 

The baseline is the energy profile if no energy flexibility is used (the default behaviour during the charge session).
This tool also outputs the baseline energy profile for each charge session.

The EV flex metric may be calculated by subtracting the shifted profile from the baseline profile to determine
how much energy has been moved in each timestep or PTU. While this logic exists in this code base, it is currently
not added to the output of this tool.

This implementation has been made specifically for GO-e workpackage 4 and is also used by GO-e workpackage 3.2.

The tool will calculate the shifted profile based on these variables:

- Congestion start: When does the period of congestion start.
- Congestion duration: How long does the period of congestion last.
- Flexwindow start: When does the flexwindow period start.
- Flexwindow duration: How long does the flexwindow period last.
- PC4 neighbourhood: The charge sessions of a number of neighbourhoods have been generated in 
  `wp4_shifted_flexible_profiles/input/cleaned/20230719_charge_session_energy_profiles/`. Shifted profiles are
  calculated per neighbourhood.

Energy is moved from the congestion period to outside the congestion period. To define to where the energy may be
moved, a 'flexwindow' period is defined as well. This period contains the congestion period but the flexwindow period
is currently implemented to start relative to when the congestion period starts as well. This is a simplification which
is based  on the fact that energy from the congestion period is only moved to later in the charge session (in other
words,  after the congestion period). So the `flexwindow start <= congestion start` and the flex window start may
configured relative to congestion start using the `flex-window-start-before-congestion-start-ptu` field in the config.

Calculations are performed for every combination of congestion start, congestion period and flexwindow duration
as defined in `config.toml`.

## Output profiles
Both baseline and shifted CSV files are saved as output after running the tool. Both type or profiles are saved
as files with the following filename template:
```text
pc4<pc4 number>_flexwindowstart<YYYY-mm-ddTHHMM>_flexwindowduration<flex window duration in PTUs>_congestionstart<YYYY-mm-ddTHHMM>_congestionduration<congestion duration in PTUs>.csv
```

An example where pc4 == 1077, flexwindow start == congestion start == 2020-06-03 at 00:00, flex window duration == 48,
congestion start == 2020-06-03 at 00:45 and congestion duration == 20:
```text
pc41077_flexwindowstart2020-06-03T00:00_flexwindowduration48_congestionstart2020-06-03T0045_congestionduration20.csv
```

## CSV Output format
The contents of the file is in standard CSV format and certain parameters such as the separator sign may be configured
in the `config.toml`. Each column is a baseline or shifted energy profile for some EV charger. Each row is a PTU
starting from flex window start. Each value is the average power in watts during that timestep.

An excerpt for 3 chargers where charge `432669` starts charging at `15:45:00` with `733.0` watts on average during that
timestep is below. From the next PTU on the charger charges with an average of `11000.0` watts and during the final PTU
the average power was `10267.0` watts.
In this excerpt the decimal sign was configured as `','` instead of the reguler `'.'` and the headerline is included.
```csv
;432583;432643;432669;432670
2020-06-01 15:30:00;0,0;0,0;0,0;0,0
2020-06-01 15:45:00;0,0;0,0;0,0;733,0
2020-06-01 16:00:00;0,0;0,0;0,0;11000,0
2020-06-01 16:15:00;0,0;0,0;0,0;11000,0
2020-06-01 16:30:00;0,0;0,0;0,0;11000,0
2020-06-01 16:45:00;0,0;0,0;0,0;11000,0
2020-06-01 17:00:00;0,0;0,0;0,0;11000,0
2020-06-01 17:15:00;0,0;0,0;0,0;11000,0
2020-06-01 17:30:00;0,0;0,0;0,0;11000,0
2020-06-01 17:45:00;0,0;0,0;0,0;11000,0
2020-06-01 18:00:00;0,0;0,0;0,0;11000,0
2020-06-01 18:15:00;0,0;0,0;0,0;11000,0
2020-06-01 18:30:00;0,0;0,0;0,0;11000,0
2020-06-01 18:45:00;0,0;0,0;0,0;11000,0
2020-06-01 19:00:00;0,0;0,0;0,0;10267,0
```

## Parquet Output format
The contents of the output file is the same as the CSV file except it is in the parquet format and CSV-specific
options such as seperator and headerline are ignored.

## Update installation to a new version
Run the `setup.sh` script again.

## config.toml
The configuration file uses the [TOML](https://toml.io/en/) format. An explanation of all the keys in the config is
added to `package_files/sample_config.toml`




# What I checked, and what the agent got wrong

The original wear calculation used // instead of /, which caused integer division and could incorrectly report low or zero wear. The code also mishandled missing service readings, potentially causing a KeyError when processing fleet data.

## What the agent got wrong
The original wear calculation used // instead of /, which caused integer division and could incorrectly report low or zero wear. The code also mishandled missing service readings, potentially causing a KeyError when processing fleet data.

## What I checked before I accepted its work
I reviewed the following acceptance requirements:

Wear calculation: Wear is calculated using regular division and does not incorrectly round down to zero.

Service warning: The warning threshold remains at 80%.

Service interval: The service interval remains 15,000 km.

Missing readings: Cars without a recorded last service reading do not crash the report or count as due.

Fleet report: The report handles missing data and calculates average wear correctly.

Unit conversion: Kilometres are converted to miles using the correct conversion factor.

Tests: The test suite should cover service warnings and missing service readings.

## What the data actually said
The analysis compares five factors against historical breakdown records: odometer distance, kilometres since service, average daily kilometres, load factor, and vehicle age.

These comparisons help identify associations between vehicle characteristics and historical breakdowns. The risk ranking can help prioritize inspections, but it should not be interpreted as a probability of breakdown or proof that a particular factor causes a breakdown.

Limitations

Historical associations depend on the quality and coverage of the available data. Risk rankings are relative to the dataset and should support, rather than replace, maintenance decisions and inspections.

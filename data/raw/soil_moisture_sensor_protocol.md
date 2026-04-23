# Soil moisture sensor operating protocol

Soil moisture sensors are useful only when their context is known. Each reading should be interpreted with plot, crop, sensor depth, soil texture, installation date, and recent irrigation history. A sensor installed too close to an emitter can overestimate available water. A sensor installed outside the wetted zone can underestimate it. In drip systems, sensor placement is especially important because wetting patterns are not uniform across the bed.

The recommended operational workflow is to validate the sensor before acting on an alert. Check battery level, timestamp freshness, physical damage, and whether the reading is consistent with nearby observations. If the reading is unexpectedly low after irrigation, inspect the valve, filter, pressure regulator, and emitter line. If the reading is unexpectedly high, inspect drainage, over-irrigation, leaks, or sensor placement.

Sensor alerts should be treated as triage signals. A high-severity low-moisture alert means that the operator should inspect the system and crop quickly, not that a single automatic prescription is always correct. The response depends on crop sensitivity, weather forecast, soil type, and whether stress symptoms are present. For shallow-rooted crops, rapid changes in root-zone moisture can matter more than for established deep-rooted crops.

Good API design should expose the raw reading, timestamp, threshold status, and operational interpretation separately. This avoids hiding uncertainty and helps a human operator understand why the assistant suggested a field action.


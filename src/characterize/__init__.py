from pint import UnitRegistry


ureg = UnitRegistry()

TIME_LABEL = "time"

# Register common time semantic labels
ureg.define(f"date = utc_timestamp = timestamp = epoch = [{TIME_LABEL}] ")

Q_ = ureg.Quantity
U_ = ureg.Unit

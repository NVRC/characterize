from pint import UnitRegistry

from characterize.mime import MIMECategorizer, TIME_LABEL


ureg = UnitRegistry()

# Register common time semantic labels
ureg.define(f"{"=".join(MIMECategorizer.TIMESERIES_COLS)} = [{TIME_LABEL}] ")

Q_ = ureg.Quantity
U_ = ureg.Unit

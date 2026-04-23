from pint import UnitRegistry


ureg = UnitRegistry()

ureg.define("date = utc_timestamp = timestamp = epoch = [time] ")

Q_ = ureg.Quantity
U_ = ureg.Unit

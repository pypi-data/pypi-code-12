from errorpro.dimensions.dimensions import Dimension
from errorpro.units import BaseUnit,DerivedUnit

# seven SI dimensions
length=Dimension(length=1)
time=Dimension(time=1)
mass=Dimension(mass=1)
current=Dimension(current=1)
temperature=Dimension(temperature=1)
amount=Dimension(amount=1)
luminosity=Dimension(luminosity=1)

# corresponding base units
system={}
system["m"]=	BaseUnit("m",length)
system["s"]=	BaseUnit("s",time)
system["kg"]=	BaseUnit("kg",mass)
system["A"]=	BaseUnit("A",current)
system["K"]=	BaseUnit("K",temperature)
system["mol"]=	BaseUnit("mol",amount)
system["cd"]=	BaseUnit("cd",luminosity)

# derived units
system["Hz"]=	DerivedUnit("Hz","1/s", system, False)
system["N"]=	DerivedUnit("N","kg*m/s**2",system)
system["Pa"]=	DerivedUnit("Pa","N/m**2",system)
system["J"]=	DerivedUnit("J","N*m",system)
system["W"]=	DerivedUnit("W","J/s",system)
system["C"]=	DerivedUnit("C","A*s",system)
system["V"]=	DerivedUnit("V","W/A",system)
system["F"]=	DerivedUnit("F","C/V",system)
system["Ohm"]=	DerivedUnit("Ohm","V/A",system)
system["ohm"]=	DerivedUnit("ohm","V/A", system, False)
system["S"]=	DerivedUnit("S","1/Ohm", system, False)
system["Wb"]=	DerivedUnit("Wb","V*s",system)
system["T"]=	DerivedUnit("T","Wb/m**2",system)
system["H"]=	DerivedUnit("H","Wb/A",system)

# additional units
system["deg"]=	DerivedUnit("deg","2*pi/360", system, False)
system["min"]=	DerivedUnit("min","60*s", system, False)
system["h"]=	DerivedUnit("h","3600*s", system, False)
system["d"]=	DerivedUnit("d","24*3600*s", system, False)

def extend_by_prefixes(unit, system):
	""" adds units with all SI prefixes to unit system
	"""
	for prefix, factor in [("p",1e-12),("n",1e-9),("mu",1e-6),("m",1e-3),("c",1e-2),("d",1e-1),("da",1e1),("h",1e2),("k",1e3),("M",1e6),("G",1e9),("T",1e12)]:
		system[prefix+unit.name] = DerivedUnit(prefix+unit.name,unit*factor, system, False)

# add prefixes
systemCopy=system.copy()
for name in systemCopy:
	if not name=="kg":
		extend_by_prefixes(system[name],system)

# exception: kg
system["pg"]=	DerivedUnit("pg","1e-15*kg", system, False)
system["ng"]=	DerivedUnit("ng","1e-12*kg", system, False)
system["mug"]=	DerivedUnit("mug","1e-9*kg", system, False)
system["mg"]=	DerivedUnit("mg","1e-6*kg", system, False)
system["cg"]=	DerivedUnit("cg","1e-5*kg", system, False)
system["dg"]=	DerivedUnit("dg","1e-4*kg", system, False)
system["g"]=	DerivedUnit("g","1e-3*kg", system, False)
system["dag"]=	DerivedUnit("dag","1e-2*kg", system, False)
system["hg"]=	DerivedUnit("hg","1e-1*kg", system, False)
system["Mg"]=	DerivedUnit("Mg","1e3*kg", system, False)
system["Gg"]=	DerivedUnit("Gg","1e6*kg", system, False)
system["Tg"]=	DerivedUnit("Tg","1e9*kg", system, False)

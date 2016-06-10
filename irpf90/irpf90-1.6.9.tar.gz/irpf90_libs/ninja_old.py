#!/usr/bin/env python
#   IRPF90 is a Fortran90 preprocessor written in Python for programming using
#   the Implicit Reference to Parameters (IRP) method.
#   Copyright (C) 2009 Anthony SCEMAMA 
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#   Anthony Scemama
#   LCPQ - IRSAMC - CNRS
#   Universite Paul Sabatier
#   118, route de Narbonne      
#   31062 Toulouse Cedex 4      
#   scemama@irsamc.ups-tlse.fr


import os,sys
import irpf90_t
from command_line import command_line
irpdir = irpf90_t.irpdir
mandir = irpf90_t.mandir

FILENAME = "build.ninja"

def run():
    from modules import modules
    cwd = os.getcwd()


    FC = os.environ["FC"]
    FC += "-I %s "%(irpdir)
    for i in command_line.include_dir:
      FC += "-I %s%s "%(irpdir,i)
   
    FCFLAGS = os.environ["FCFLAGS"]

    try:
      l_obj_external = os.environ["OBJ"]
    except KeyError:
      l_obj_external = []


    t = [ "rule compile_fortran" ,
          "  command = {FC} {FCFLAGS} -c $in -o $out".format(FC=FC, FCFLAGS=FCFLAGS),
          "",
          "rule link",
          "  command = {FC} $in -o $out".format(FC=FC) ]
   
    print '\n'.join(t)

    l_mod = list( modules.values() )

    l_basename_needed_in_irpdir = [ "irp_stack.irp", 
#       "irp_checkpoint.irp.F90",
      ]

    for m in l_mod:
      if not m.is_main:
        l_basename_needed_in_irpdir += [ "%s.irp"%(m.filename), "%s.irp.module"%(m.filename) ]

    if command_line.do_openmp:
        l_basename_needed_in_irpdir.append("irp_locks.irp")

    if command_line.do_profile:
        l_basename_needed_in_irpdir.append("irp_profile.irp")

    l_basename_needed_in_irpdir = map(lambda x: os.path.join(cwd,"IRPF90_temp",x), l_basename_needed_in_irpdir)
    l_obj_irp = map(lambda x: "%s.o"%x, l_basename_needed_in_irpdir)
    

    l_targets = filter(lambda x: modules[x].is_main, modules)
    l_targets = map(lambda x: x[:-6], l_targets) # remove ".irp.f"

    l_build = []
    for basename in l_basename_needed_in_irpdir:
        f90    = "%s.F90"%(basename)
        module = "%s.module.o"%(basename)
        o      = "%s.o"  %(basename)
        if basename.endswith(".irp.module"):
            l_build.append( "build {0}: compile_fortran {1}".format(o,f90) )
        elif basename.endswith(".irp"):
            if "%s.module"%(basename) in l_basename_needed_in_irpdir:
               pass # See below for m in l_mod loop
            else:
              l_build.append( "build {0}: compile_fortran {1}".format(o,f90) )
        else:
            raise KeyError
        l_build.append("")

    l_obj = l_obj_irp + l_obj_external
    for target in l_targets:
        l_deps = [ "%s.irp.o"%target, "%s.irp.module.o"%target ] + l_obj
        l_deps = map(lambda x: os.path.join(cwd,irpdir,x), l_deps)
        l_build.append( "build {0}: link {1}".format( os.path.join(cwd,target)," ".join(l_deps)) )
        l_build.append( "build {0}.irp.module.o: compile_fortran {0}.irp.module.F90".format( os.path.join(cwd,target) ) )
        l_build.append("")

    for m in l_mod:
        l_deps = l_obj_external + [ os.path.join(cwd,irpdir,"%s.irp.module.o"%m.filename) ]
        l_needed_files = map(lambda x: "%s.irp.module.o"%(os.path.join(cwd,irpdir,x)), 
          [modules[x].filename for x in modules if modules[x].name in m.needed_modules] )
        o = "%s.irp.o"% ( os.path.join(cwd,irpdir,m.filename) )
        f90 = "%s.irp.F90"% ( os.path.join(cwd,irpdir,m.filename) )
        l_build.append( "build {0}: compile_fortran {1} | {2}".format(o, f90, " ".join(l_deps+l_needed_files)) )
        l_build.append("")

    l_build.append( "build {0}: compile_fortran {1} | {2}".format (
      os.path.join(cwd,irpdir,"irp_touches.irp.o"),
      os.path.join(cwd,irpdir,"irp_touches.irp.F90"),
      " ".join( map(lambda x: os.path.join(cwd,irpdir,x), l_obj) )
      )
      )
    print "\n".join(l_build)

if __name__ == '__main__':
  run()


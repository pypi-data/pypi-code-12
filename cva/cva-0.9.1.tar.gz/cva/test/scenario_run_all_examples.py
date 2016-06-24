import multiprocessing as mp
import cva

def case01():
    cva.examples.case01_torus()

def case02():
    cva.examples.case02_sphere()

def case03():
    cva.examples.case03_earth()

def case04():
    cva.examples.case04_cylinder()

def case05():
    cva.examples.case05_hyperboloid()

def case06():
    cva.examples.case06_plane()

def case07():
    cva.examples.case07_sphylinder()

def case08():
    cva.examples.case08_capped_cylinder()

def case09():
    cva.examples.case09_moebius()

def case10():
    cva.examples.case10_brachistochrone_plane_earth()

def case11():
    cva.examples.case11_brachistochrone_tilted_plane()

def case12():
    cva.examples.case12_brachistochrone_plane_moon()

def case13():
    cva.examples.case13_brachistochrone_unit_sphere()

def case14():
    cva.examples.case14_brachistochrone_hyperboloid()

def case15():
    cva.examples.case15_earth_latlon()

def case18():
    cva.examples.case18_blackhole_geodesic_family()

def case19():
    cva.examples.case19_collapsing_sphere()

def case20():
    cva.examples.case20_inflating_sphere()

def case21():
    cva.examples.case21_sphere_in_r3()

def case22():
    cva.examples.case22_sphere_in_r4()

cva.solve.set_parm('image_file',True)


try:
  processes = [
    mp.Process(target=case01),
    mp.Process(target=case02),
    mp.Process(target=case03),
    mp.Process(target=case04),
    mp.Process(target=case05),
    mp.Process(target=case06),
    mp.Process(target=case07),
    mp.Process(target=case08),
    mp.Process(target=case09),
    mp.Process(target=case10),
    mp.Process(target=case11),
    mp.Process(target=case12),
    mp.Process(target=case13),
    mp.Process(target=case14),
    mp.Process(target=case15),
    mp.Process(target=case18),
    mp.Process(target=case19),
    mp.Process(target=case20),
    mp.Process(target=case21),
    mp.Process(target=case22)
  ]

  for p in processes:
    p.start()

  for p in processes:
    p.join()


except KeyboardInterrupt:
  print("\nExiting...")


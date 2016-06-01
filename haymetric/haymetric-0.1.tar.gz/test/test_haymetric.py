import os
import glob
import unittest
import datetime

from haymetric.haymetric import Metric, Units, Rotations

def remove_files(files):
    for f in glob.glob(files):
        os.remove(f)

class TestHaymetric(unittest.TestCase):

    def setUp(self):
        self.log_path = "tst/logs/Test.log"
        # Wed, 11 May 2016 21:21:00 GMT
        self.sample_timestamp = 1463001660
        self.sample_logfile = self.__get_logfile(self.sample_timestamp)

    def tearDown(self):
        remove_files(self.log_path + "*")
        os.removedirs("tst/logs")

    def test_emit_from_different_metrics(self):
        metric1 = Metric(self.log_path, "service=MyTestProgram,market=Hanoi")
        self.__add_values(metric1.get_scope("method=GetAPI"))
        metric1.flush(self.sample_timestamp)
        metric1.close()
        metric2 = Metric(self.log_path, "service=MyTestProgram,market=Hanoi")
        self.__add_counters(metric2.get_scope("method=PushAPI"))
        metric2.flush(self.sample_timestamp)
        metric2.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(8, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=market=Hanoi,method=GetAPI,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=NoUnit=999+1,DBTime=10ms,Time=1200+800ms\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])
        self.assertEqual('Timestamp=1463001660\n', log_lines[4])
        self.assertEqual('Dimensions=market=Hanoi,method=PushAPI,service=MyTestProgram\n', log_lines[5])
        self.assertEqual('Metrics=Failed=2,Pushes=11\n', log_lines[6])
        self.assertEqual('---------\n', log_lines[7])

    def test_rotation_when_time_changes(self):
        # Wed, 11 May 2016 20:33:01 GMT
        t1 = 1462998781
        # Wed, 11 May 2016 21:33:01 GMT
        t2 = 1463002381

        metric = Metric(self.log_path, "service=MyTestProgram,market=Hanoi")
        self.__add_values(metric.get_scope("method=GetAPI"))
        metric.flush(t1)
        self.__add_counters(metric.get_scope("method=PushAPI"))
        metric.flush(t2)
        metric.close()
        t1_lines = self.__read_file_to_lines(self.__get_logfile(t1))
        t2_lines = self.__read_file_to_lines(self.__get_logfile(t2))
        self.assertEqual(4, len(t1_lines))
        self.assertEqual("Timestamp=1462998781\n", t1_lines[0])
        self.assertEqual("Dimensions=market=Hanoi,method=GetAPI,service=MyTestProgram\n", t1_lines[1])
        self.assertEqual("Metrics=NoUnit=999+1,DBTime=10ms,Time=1200+800ms\n", t1_lines[2])
        self.assertEqual("---------\n", t1_lines[3])
        self.assertEqual(4, len(t2_lines))
        self.assertEqual("Timestamp=1463002381\n", t2_lines[0])
        self.assertEqual("Dimensions=market=Hanoi,method=PushAPI,service=MyTestProgram\n", t2_lines[1])
        self.assertEqual("Metrics=Failed=2,Pushes=11\n", t2_lines[2])
        self.assertEqual("---------\n", t2_lines[3])

    def test_multiple_rotations(self):
        metric_minutely = Metric(self.log_path, "service=MyTestProgram,market=Hanoi", Rotations.MINUTELY)
        metric_minutely.flush()
        self.assertTrue(os.path.isfile(self.__get_logfile(rotation=Rotations.MINUTELY)))
        metric_hourly = Metric(self.log_path, "service=MyTestProgram,market=Hanoi", Rotations.HOURLY)
        metric_hourly.flush()
        self.assertTrue(os.path.isfile(self.__get_logfile(rotation=Rotations.HOURLY)))
        metric_daily = Metric(self.log_path, "service=MyTestProgram,market=Hanoi", Rotations.DAILY)
        metric_daily.flush()
        self.assertTrue(os.path.isfile(self.__get_logfile(rotation=Rotations.DAILY)))

    def test_multiple_units(self):
        metric = Metric(self.log_path, "service=MyTestProgram,market=Hanoi")
        scope = metric.get_scope()
        scope.add_value("NanoSecond", 1, Units.NANOSECOND)
        scope.add_value("MicroSecond", 2, Units.MICROSECOND)
        scope.add_value("MilliSecond", 3, Units.MILLISECOND)
        scope.add_value("Second", 4, Units.SECOND)
        scope.add_value("Minute", 5, Units.MINUTE)
        scope.add_value("Hour", 6, Units.HOUR)
        scope.add_value("Byte", 7, Units.BYTE)
        scope.add_value("KiloByte", 8, Units.KILOBYTE)
        scope.add_value("MegaByte", 9, Units.MEGABYTE)
        scope.add_value("GigaByte", 10, Units.GIGABYTE)
        metric.flush(self.sample_timestamp)
        metric.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(4, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=market=Hanoi,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=MilliSecond=3ms,Hour=6h,KiloByte=8kb,NanoSecond=1ns,GigaByte=10gb,Second=4s,MicroSecond=2us,Byte=7b,MegaByte=9mb,Minute=5m\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])

    def test_get_empty_scope(self):
        metric = Metric(self.log_path, "service=MyTestProgram,market=Hanoi")
        self.__add_values(metric.get_scope())
        metric.flush(self.sample_timestamp)
        metric.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(4, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=market=Hanoi,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=NoUnit=999+1,DBTime=10ms,Time=1200+800ms\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])

    def test_reset_after_flush(self):
        metric = Metric(self.log_path, "service=MyTestProgram,market=Hanoi")
        self.__add_values(metric.get_scope("method=GetAPI"))
        metric.flush(self.sample_timestamp)
        self.__add_counters(metric.get_scope("method=PushAPI"))
        metric.flush(self.sample_timestamp)
        metric.flush(self.sample_timestamp)
        metric.flush(self.sample_timestamp)
        metric.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(8, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=market=Hanoi,method=GetAPI,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=NoUnit=999+1,DBTime=10ms,Time=1200+800ms\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])
        self.assertEqual('Timestamp=1463001660\n', log_lines[4])
        self.assertEqual('Dimensions=market=Hanoi,method=PushAPI,service=MyTestProgram\n', log_lines[5])
        self.assertEqual('Metrics=Failed=2,Pushes=11\n', log_lines[6])
        self.assertEqual('---------\n', log_lines[7])

    def test_scope_override_and_multiple_updates(self):
        metric = Metric(self.log_path, "service=MyTestProgram,market=Hanoi,method=PushAPI")
        scope1 = metric.get_scope("method=GetAPI   , host  = 1.2.3.4")
        scope1.add_counter("CountIt", 1)
        scope2 = metric.get_scope(" host = 1.2.3.4   , methoD=GetAPI")
        scope2.add_counter("CountIt", 8)
        metric.flush(self.sample_timestamp)
        metric.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(4, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=host=1.2.3.4,market=Hanoi,method=GetAPI,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=CountIt=9\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])

    def test_scope_override(self):
        metric = Metric(self.log_path, "service=MyTestProgram,market=Hanoi,method=PushAPI")
        scope = metric.get_scope("method=GetAPI")
        scope.add_counter("MyCounter", 1)
        metric.flush(self.sample_timestamp)
        metric.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(4, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=market=Hanoi,method=GetAPI,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=MyCounter=1\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])

    def test_dimension_normalization(self):
        metric = Metric(self.log_path, "maRket=Hanoi ,   SerViCe=MyTestProgram")
        scope = metric.get_scope("mEthod=PushAPI")
        scope.add_counter("Success", 9)
        metric.flush(self.sample_timestamp)
        metric.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(4, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=market=Hanoi,method=PushAPI,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=Success=9\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])

    def test_counters_and_values(self):
        metric = Metric(self.log_path, "service=MyTestProgram,market=Hanoi")
        scope = metric.get_scope("method=PushAPI")
        self.__add_counters(scope)
        self.__add_values(scope)
        metric.flush(self.sample_timestamp)
        metric.close()
        log_lines = self.__read_file_to_lines(self.sample_logfile)
        self.assertEqual(4, len(log_lines))
        self.assertEqual('Timestamp=1463001660\n', log_lines[0])
        self.assertEqual('Dimensions=market=Hanoi,method=PushAPI,service=MyTestProgram\n', log_lines[1])
        self.assertEqual('Metrics=Failed=2,Pushes=11,NoUnit=999+1,DBTime=10ms,Time=1200+800ms\n', log_lines[2])
        self.assertEqual('---------\n', log_lines[3])

    def __add_counters(self, scope):
        scope.add_counter("Pushes", 10)
        scope.add_counter("Pushes", 1)
        scope.add_counter("Failed", 1)
        scope.add_counter("Failed", 1)

    def __add_values(self, scope):
        scope.add_value("Time", 1200, Units.MILLISECOND)
        scope.add_value("Time", 800, Units.MILLISECOND)
        scope.add_value("DBTime", 10, Units.MILLISECOND)
        scope.add_value("NoUnit", 999)
        scope.add_value("NoUnit", 1)

    def __get_logfile(self, timestamp=None, rotation=Rotations.HOURLY):
        now = datetime.datetime.now()
        if timestamp:
            now = datetime.datetime.fromtimestamp(timestamp)
        if rotation is Rotations.MINUTELY:
            return self.log_path + "." + now.strftime("%Y-%m-%d-%H-%M")
        if rotation is Rotations.HOURLY:
            return self.log_path + "." + now.strftime("%Y-%m-%d-%H")
        if rotation is Rotations.DAILY:
            return self.log_path + "." + now.strftime("%Y-%m-%d")

    def __read_file_to_lines(self, filename):
        f = open(filename)
        lines = f.readlines()
        f.close()
        return lines

if __name__ == "__main__":
    unittest.main()

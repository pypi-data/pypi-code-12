"""
Simple test jig (not yet automated) for intel-times library
"""
import argparse
from . import Cycle, Checkpoint

def main():
    """Class test/example code"""
    parser = argparse.ArgumentParser("checkpoint and cycle time test")
    parser.add_argument("time", type=str, nargs='?', help="optional time (default to now")
    parser.add_argument("--zone", "-z", type=str, help="optional timezone (default to local")
    args = parser.parse_args()

    cycle = Cycle(target=args.time, timezone=args.zone)
    print("Cycle start:", cycle)
    print("Cycle end:", cycle + 1)
    print("Cycle datetime objects:", cycle.start, cycle.end)
    print("Cycle as timestamp:", int(cycle))

    print("Cycle incremental add")
    cycle += 1
    print("New cycle:", cycle)
    print("New datetime objects:", cycle.start, cycle.end)
    cycle = cycle + 5
    print("Moved forward 5 cycles:", cycle)
    print("New datetime objects:", cycle.start, cycle.end)
    print()

    checkpoint = Checkpoint(target=args.time, timezone=args.zone)
    print("Checkpoint start:", checkpoint)
    print("Checkpoint end:", checkpoint + 1)
    print("Checkpoints since start of cycle:", checkpoint.number())
    print("Time since last:", checkpoint.since_last())
    print("Time until next:", checkpoint.until_next())

    checkpoint += 1
    print("Next checkpoint:", checkpoint)
    print("Checkpoints since start of cycle:", checkpoint.number())

    for day in ["04/18/2016", "yesterday", "today", "tomorrow", "April 25, 2016"]:
        print("Checkpoints {}:".format(day))
        for checkpoint in Checkpoint(day, timezone=args.zone).on_day():
            print("Checkpoint {}: {}{}".format(
                checkpoint.number(),
                checkpoint,
                ' (new cycle)' if checkpoint.cycle_start() else ''))

if __name__ == '__main__':
    main()

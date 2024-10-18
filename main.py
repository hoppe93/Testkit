#!/usr/bin/env python3
#
# Test kit entry point.
#

import argparse
import db
import testkit


def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser("Test kit")

    parser.add_argument('-b', '--branch', help="Name of git branch to checkout.", nargs='?', default=None)
    parser.add_argument('-c', '--commit', help="Git commit hash to checkout.", nargs='?', default=None)
    parser.add_argument('-d', '--database', help="Name of database file to load.", nargs='?', default='testkit.db')
    parser.add_argument('--force', help="Force run this test suite, even if the current version of the code has been tested before.", action='store_true')
    parser.add_argument('--init', help="Initialize the database instead of running a test.", action='store_true')

    parser.add_argument('testconfig', help="Name of configuration file for the test suite to run.", nargs='?', default=None)

    return parser.parse_args()


def main():
    args = parse_args()

    _db = db.Database(args.database)
    db.config.init(_db)

    if args.testconfig is None:
        raise Exception("No test suite configuration file specified.")

    try:
        ts = testkit.TestSuite(
            args.testconfig, branch=args.branch, commit=args.commit
        )

        runs = ts.getPreviousRuns()
        # If this version of the code has already been tested,
        # we just ignore this test.
        if not args.force and len(runs) > 0:
            return 0

        ts.run()
    except BuildException as ex:
        print(ex)
    except Exception as ex:
        print(ex)

    return 0


if __name__ == '__main__':
    sys.exit(main())



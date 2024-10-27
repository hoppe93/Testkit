#!/usr/bin/env python3
#
# Test kit entry point.
#

import argparse
import db
import testkit
import traceback
from pathlib import Path
import sys

from testkit import BuildException, testlog


def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser("Test kit")

    dbname = (Path(__file__).parent / 'testkit.db').resolve().absolute()

    parser.add_argument('-b', '--branch', help="Name of git branch to checkout.", nargs='?', default=None)
    parser.add_argument('-c', '--commit', help="Git commit hash to checkout.", nargs='?', default=None)
    parser.add_argument('-d', '--database', help="Name of database file to load.", nargs='?', default=str(dbname))
    parser.add_argument('-e', '--error-log', help="Name of log file for error messages.", nargs='?', default='error.log')
    parser.add_argument('-l', '--log-file', help="Name of standard log file.", nargs='?', default='out.log')
    parser.add_argument('-s', '--stdout', help="Redirect the log files to stdout and stderr.", action='store_true')

    parser.add_argument('--force', help="Force run this test suite, even if the current version of the code has been tested before.", action='store_true')
    parser.add_argument('--init', help="Initialize the database instead of running a test.", action='store_true')
    parser.add_argument('--skip-build', help="Skip building the code.", action='store_true')

    parser.add_argument('testconfig', help="Name of configuration file for the test suite to run.", nargs='?', default=None)

    return parser.parse_args()


def main():
    args = parse_args()

    log_file = args.log_file
    if args.stdout or args.log_file == 'stdout':
        log_file = sys.stdout

    error_log = args.error_log
    if args.stdout or args.error_log == 'stderr':
        error_log = sys.stderr

    testlog.init(log_file, error_log)

    _db = db.Database(args.database)
    db.config.init(_db)

    if args.testconfig is None:
        testlog.error("No test suite configuration file specified.")
        return 1

    try:
        ts = testkit.TestSuite(
            args.testconfig, branch=args.branch, commit=args.commit,
            skipbuild=args.skip_build
        )

        runs = ts.getPreviousRuns()
        # If this version of the code has already been tested,
        # we just ignore this test.
        if len(runs) > 0:
            status = runs[-1].status
            statusmsg = ['', 'RUNNING', 'SUCCESS', 'FAILURE'][status]
            testlog.info(f"Version '{ts.code.getCommit()}' has previously been tested.")
            testlog.info(f"The status of the test was '{statusmsg}'.")

            if not args.force:
                if runs[-1].status in [db.TestRun.STATUS_SUCCESS, db.TestRun.STATUS_RUNNING]:
                    return 0
                else:
                    return 1
            else:
                testlog.info(f"Forcing a re-test of the code.")

        ts.run()
    except BuildException as ex:
        testlog.error(''.join(traceback.format_exception(ex)))
        print(ex)
    except Exception as ex:
        testlog.error(''.join(traceback.format_exception(ex)))
        print(ex)

    testlog.deinit()

    return 0


if __name__ == '__main__':
    sys.exit(main())



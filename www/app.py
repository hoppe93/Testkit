
import numpy as np
from flask import Flask, session, render_template, url_for, request
from pathlib import Path
import json
import sys

ROOTPATH = Path(__file__).parent.parent.resolve().absolute()
sys.path.append(str(ROOTPATH))

import db
from db import TestResult, TestRun


app = Flask(__name__)

with open(f'{ROOTPATH}/www/config.json', 'r') as f:
    config = json.load(f)

database = db.Database(config['database'])
db.config.init(database)


@app.route("/")
def overview():
    """
    Display the overview page.
    """
    LIMIT = 100
    page = request.args.get('p', 0)

    testruns = TestRun.getall(page=page, per_page=LIMIT)
    runcount = TestRun.count()

    return render_template(
        'overview.html', config=config,
        testruns=testruns, TestRun=TestRun,
        page=page, total_runs=runcount,
        per_page=LIMIT, total_pages=int(np.ceil(runcount/LIMIT))
    )


@app.route("/result/<result_id>")
def result(result_id):
    """
    Display details for the a specified test result.
    """
    result = TestResult.get(result_id)
    testrun = TestRun.get(result.testrunid)

    return render_template(
        'result.html', config=config,
        TestResult=TestResult, result=result,
        testrun=testrun
    )


@app.route("/run/<run_id>")
def run(run_id):
    """
    Display details for a specified test run.
    """
    testrun = TestRun.get(run_id)
    results = testrun.results()

    return render_template(
        'run.html', config=config,
        TestRun=TestRun, TestResult=TestResult,
        testrun=testrun, results=results,
    )



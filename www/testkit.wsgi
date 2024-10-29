#!/usr/bin/env python3

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/hoppe/Testkit/www/")

from app import app as application


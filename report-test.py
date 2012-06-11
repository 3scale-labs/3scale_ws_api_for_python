#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ThreeScalePY
import getopt
import sys
import os
import time

def usage(errorMessage=None):
    if errorMessage:
        stream = sys.stderr
    else:
        stream = sys.stdout
    stream.write("""
Usage: %s [--help|-h] --app-id|-i --provider-key|-p""" %
    os.path.basename(sys.argv[0]))
    if errorMessage:
        stream.write("\nERROR: " + errorMessage + "\n")
        exitCode = 1
    else:
        exitCode = 0
    sys.exit(exitCode)

def main():
    """main method"""
    app_id = None
    provider_key = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:p:", ['help', 
                                   'app-id=', 'provider-key='])

        for opt, value in opts:
            if (opt in ('-i', '--app-id')):
                app_id = value
            elif (opt in ('-p', '--provider-key')):
                provider_key = value
            elif (opt in ('-h', '--help')):
                usage()

    except getopt.GetoptError, err:
            usage('Invalid option specified: %s' % err)

    if not app_id:
        usage('App Id not specified')

    if not provider_key:
        usage('Provider Key not specified')

    report = ThreeScalePY.ThreeScaleReport(provider_key)

    t1 = {}
    trans_usage = {}
    trans_usage['hits'] = 1
    trans_usage['max_value'] = 5
    t1['app_id'] = app_id
    t1['usage'] = trans_usage
    t2 = {}
    trans_usage = {}
    trans_usage['hits'] = 2
    trans_usage['timestamp'] = time.gmtime(time.time())
    trans_usage['max_value'] = 2
    t2['app_id'] = app_id
    t2['usage'] = trans_usage

    transactions = [t1]

    print "app id => %s" % app_id
    print "provider key => %s" % provider_key
    resp = report.report(transactions)
    if resp:
        print "      SUCCESS: Report transaction posted"
    else:
        print "      ERROR: Not posted, perhaps invalid credentials " \
              "specified?"

if __name__ == '__main__':
    main()

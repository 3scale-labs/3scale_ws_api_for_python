#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ThreeScalePY
import getopt
import sys
import os

def usage(errorMessage=None):
    if errorMessage:
        stream = sys.stderr
    else:
        stream = sys.stdout
    stream.write("""
Usage: %s [--help|-h] --user-key|-u --provider-key|-p""" %
    os.path.basename(sys.argv[0]))
    if errorMessage:
        stream.write("\nERROR: " + errorMessage + "\n")
        exitCode = 1
    else:
        exitCode = 0
    sys.exit(exitCode)

def main():
    """main method"""
    user_key = None
    provider_key = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:", ['help', 'user-key=', 'provider-key='])

        for opt, value in opts:
            if (opt in ('-u', '--user-key')):
                user_key = value
            elif (opt in ('-p', '--provider-key')):
                provider_key = value
            elif (opt in ('-h', '--help')):
                usage()

    except getopt.GetoptError, err:
            usage('Invalid option specified: %s' % err)


    if not user_key:
        usage('User Key not specified')

    if not provider_key:
        usage('Provider Key not specified')

    auth = ThreeScalePY.ThreeScaleAuthorizeUserKey(provider_key, None, None, user_key)
    print "user id => %s" % auth.user_key
    print "provider key => %s" % auth.provider_key
    if auth.authorize():
        resp = auth.build_auth_response()
    else:
        print "     ERROR: Not authorized, perhaps invalid " \
              "credentials specified?"
        sys.exit(1)

    print "      <===== Usage Report =====>"
    print "           Usage Plan: %s" % resp.get_plan()
    usage_reports = resp.get_usage_reports()
    for report in usage_reports:
        print "      <===== Usage Report =====>"
        print "            metric => %s" % report.get_metric()
        print "            period => %s" % report.get_period()
        print "            start => %s" % report.get_start_period()
        print "            end => %s" % report.get_end_period()
        print "            max => %s" % report.get_max_value()
        print "            current => %s" % report.get_current_value()
        
if __name__ == '__main__':
    main()


"""
accessionlib.py - Utilities for handling accession IDs.
 
This module provides a bunch of functions for dealing with accession IDs.

get_LogicalDB_key( LogicalDB ):
        Returns the _LogicalDB_key for a given LogicalDB.
        03/33/2023 : used by annotload

get_MGIType_key( MGIType ):
        Returns the _MGIType_key for a given MGIType.
        03/22/2023: used by noteload

get_Object_key( accID, MGIType, _MGIType_key ):
        Returns _Object_key, list of _Object keys or None for given accID.
        03/22/2023: used by lib_py_dataload, gxdindexload

split_accnum(s):
        Given an accession ID, split it into its prefix and numeric parts.
        Returns prefixPart (numericPart (int)

"""

import sys
import os
import re
import db 

def get_Object_key(accID, MGIType=None, _MGIType_key=None):
        """Returns _Object_key, list of _Object keys or None for given accID.
        #
        # Requires:
        #	accID -- A str.
        #	MGIType -- 'Reference', 'Marker', 'Segment' or 'Experiment'.
        #	_MGIType_key -- If you don't happen to have the MGIType, you
        #		can pass this instead.  Not recommended.  (integer)
        #
        """
        command = 'select distinct _Object_key from ACC_View where accID = \'%s\'\n' % (accID)

        if MGIType is not None:
                command = command + 'and MGIType = \'%s\'\n' % (MGIType)
        elif _MGIType_key is not None:
                command = command + 'and _MGIType_key = %d\n' % (_MGIType_key)

        results = db.sql(command, 'auto')

        if len(results) == 1:
                _Object_key = results[0]['_Object_key']
        elif len(results) > 1:
                _Object_key = []
                for result in results:
                        _Object_key.append(result['_Object_key'])
        else:
                _Object_key = None

        return _Object_key

def get_MGIType_key( MGIType):
        """Returns the _MGIType_key for a given MGIType or None if invalid Type.
        #
        # Requires:
        #	MGIType -- A str.representing the object type ('Marker', 'Segment'...)
        #
        """
        command = 'select _MGIType_key from ACC_MGIType where name = \'%s\'' % (MGIType)

        results = db.sql(command, 'auto')
        if results:
                _MGIType_key = results[0]['_MGIType_key']
        else:
                _MGIType_key = None

        return _MGIType_key

def get_LogicalDB_key( LogicalDB):
        """Returns the _LogicalDB_key for a given LogicalDB or None if invalid.
        #
        # Requires:
        #	LogicalDB -- A str.representing the LogicalDB('MGI', 'Sequence DB'...)
        """
        command = 'select _LogicalDB_key from ACC_LogicalDB where name = \'%s\'' % (LogicalDB)

        results = db.sql(command, 'auto')
        if results:
                _LogicalDB_key = results[0]['_LogicalDB_key']
        else:
                _LogicalDB_key = None

        return _LogicalDB_key

def split_accnum(accnum):
    # set prefix to the prefix part, numeric to the numeric part

    matchpre = re.compile("^((.*[^0-9])?)([0-9]*)")
    # group(1) = prefix (or "")
    # group(3) = numeric part (or "")
    # .*      anything
    # [^0-9]  non-digit
    # \(.*[^0-9]\)? optional prefix
    # \([0-9]*\)  optional numeric part

    match_result = matchpre.match(accnum)
    prefix = match_result.group(1)
    numeric = match_result.group(3)

    if (numeric != ""):		# have a none null numeric part
        numeric = int(numeric)  # convert it to int
    else:			# have a null numeric part
        numeric = None
    
    return (prefix, numeric)

#
# Warranty Disclaimer and Copyright Notice
# 
#  THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE SUITABILITY OR 
#  ACCURACY OF THIS SOFTWARE OR DATA FOR ANY PURPOSE, AND MAKES NO WARRANTIES, 
#  EITHER EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR A 
#  PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA WILL NOT 
#  INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS, OR OTHER RIGHTS.  
#  THE SOFTWARE AND DATA ARE PROVIDED "AS IS".
# 
#  This software and data are provided to enhance knowledge and encourage 
#  progress in the scientific community and are to be used only for research 
#  and educational purposes.  Any reproduction or use for commercial purpose 
#  is prohibited without the prior express written permission of the Jackson 
#  Laboratory.
# 
# Copyright 1996, 1999, 2002 by The Jackson Laboratory
# All Rights Reserved
#

#!/usr/local/bin/python

"""
accessionlib.py - Utilities for handling accession IDs.
 
INTRODUCTION

This module provides a bunch of functions for dealing with accession IDs.


CLASSES

	ActualDB
	ActualDBTable
	LogicalDB
	LogicalDBTable


FUNCTIONS

build_sql( search, table ):
	Constructs the part of an SQL query that deals with accession IDs.

load_active_LogicalDBs():
	Loads ACC_LogicalDB and active ActualDBs into a Python dictionary.

get_accID( _Object_key, MGIType, LogicalDB, view, preferred ):
	Returns accession ID, list of accession IDs or none for _Object_key.

get_Accession_key(_Object_key, MGIType, _MGIType_key, LogicalDB,
		_LogicalDB_key):
	Returns the _Accession_key, list of _Accession keys or None for a given
	_Object_key.

get_jnumID( _Refs_key ):
	Returns a jnumID for a given _Refs_key.

get_links( _Object_key, MGIType, LogicalDB, view, preferred ):
	Returns a Python dictionary of accession IDs for given _Object_key.

get_LogicalDB( _LogicalDB_key ):
	Returns the LogicalDBfor a given _LogicalDB_key.

get_LogicalDB_key( LogicalDB ):
	Returns the _LogicalDB_key for a given LogicalDB.

get_MGIType( _MGIType_key ):
	Returns the MGIType for a given _MGIType_key.

get_MGIType_key( MGIType ):
	Returns the _MGIType_key for a given MGIType.

get_Object_key( accID, MGIType, _MGIType_key ):
	Returns _Object_key, list of _Object keys or None for given accID.

get_source( LogicalDB, Acc_ID, actualDBTable ):
	Returns HTML containing links to appropriate DBs.

parse_id( s ):
	Given an accession ID expression, returns a nice datastructure.

split_accnum(s):
	Given an accession ID, split it into its prefix and numeric parts.
	Returns prefixPart (string), numericPart (int)

THINGS TO DO

1.  Rewrite get_accID().
2.  Rewrite build_sql().


SPECIAL NOTES
 
Also, you need to set $DSQUERY and $MGD if you are using something besides the
defaults that are in the db module.
"""


# Imports
# =======

import sys
import os
import string
import re
import types
import db 

# Shorthand
# =========
sql = db.sql		# by default, we use the db library to execute SQL

def set_sqlFunction (fn):
	# change the function used to execute SQL statements from its default
	# value (see above)
	global sql
	sql = fn
	return

# Exceptions
# ==========

NoLogicalDBforOrganism = "No Logical Database for Organism key:"
MultLogicalDBsforOrganism = "Multiple Logical Databases for Organism key:"
NoActualDBforOrganism = "No Actual Database for Organism key:"
MultActualDBsforOrganism = "Multiple Actual Databases for Organism key:"

# aliases maintained for backward compatability

NoLogicalDBforSpecies = NoLogicalDBforOrganism
MultLogicalDBsforSpecies = MultLogicalDBsforOrganism
NoActualDBforSpecies = NoActualDBforOrganism
MultActualDBsforSpecies = MultActualDBsforOrganism


# Classes
# ======= 

class LogicalDB:
	"""
	A "Logical Database" in MGI. Corresponds to the entries in the 
    ACC_LogicalDB table in the MGI database.
	"""
	def __init__(self, logicaldbname, logicaldbkey, description, 
			organismkey):
		""" constructor
		# requires: 
		#    logicaldbname: name of the LogicalDB (string).
		#    logicaldbkey: primary key/identifier of the logicaldb (integer).
		#    description: textual description of the logicaldb (string).
		#    organismkey: integer key representing the organism that
		#		this logical database is associated with
		#		(primary key of MGI_Organism table).
		# effects: initializes object with provided parameters. 
		# exceptions: none
		"""
		self.name = logicaldbname
		self.key = logicaldbkey
		self.description = description
		self.organismkey = organismkey

	def getName(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the name of this object (string)
		# exceptions: none
		"""
		return self.name

	def getKey(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the key/identifier of this object. This is the 
		#          _LogicalDB_key from ACC_LogicalDB (integer).
		# exceptions: none
		"""
		return self.key
	
	def getDescription(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the textual description of this object (string).
		# exceptions: none
		"""
		return self.description
		
	def getOrganismKey(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the _Organism_key associated with this object
		#	(integer). 
		# exceptions: none
		"""
		return self.organismkey

	# method alias for backward compatability

	getSpeciesKey = getOrganismKey


class LogicalDBTable:
	"""
	# An in-memory representation of the Sybase ACC_LogicalDB table.
	"""
	def __init__(self):
		""" constructor
		# requires: nothing
		# effects: queries the database for the contents of the ACC_LogicalDB
		#          table. 
		# exceptions: SQL exceptions
		"""
		self.DBbyName = {}
		self.DBbyKey = {}

		command = 'select name, _LogicalDB_key, description, _Organism_key from ACC_LogicalDB'
		results = sql(command, 'auto')

		for result in results:
			logicaldbname = result['name']
			logicaldbkey = result['_LogicalDB_key']
			description = result['description']
			organismkey = result['_Organism_key']
			ldb = LogicalDB(logicaldbname, logicaldbkey, description, organismkey)
			self.DBbyName[logicaldbname] = ldb 
			self.DBbyKey[logicaldbkey] = ldb 

	def getDBbyKey(self, LogicalDBKey):
		"""
		# requires:
		#    LogicalDBKey: integer.
		# effects: finds a LogicalDB object by LogicalDBKey.
		# returns: the LogicalDB object, or None if one with key LogicalDBKey 
		#          couldn't be found.
		# exceptions: none.
		"""
		if self.DBbyKey.has_key(LogicalDBKey):
			return self.DBbyKey[LogicalDBKey]
		else:
			return None

	def getDBbyName(self, LogicalDBName):
		"""
		# requires: 
		#    LogicalDBName: name of the LogicalDB (string).
		# effects: finds LogicalDB object by name
		# returns: the LogicalDB object, or None if one with name LogicalDBName
		#          couldn't be found.
		# exceptions: none.
		"""
		if self.DBbyName.has_key(LogicalDBName):
			return self.DBbyName[LogicalDBName]
		else:
			return None

	def getNamebyKey(self, LogicalDBKey):
		"""
		# requires: 
		#    LogicalDBKey: key/identifier of the LogicalDB (integer).
		# effects: finds LogicalDB object by key/identifier (ACC_LogicalDB's 
        	#          _LogicalDB_key).
		# returns: the LogicalDB object, or None if one with key LogicalDBKey
		#          couldn't be found.
		# exceptions: none.
		"""
		if self.DBbyKey.has_key(LogicalDBKey):
			return self.DBbyKey[LogicalDBKey].getName()
		else:
			return None

	def getKeybyName(self, LogicalDBName):
		"""
		# requires: 
		#   LogicalDBName: string.
		# effects: Looks up the the key of a LogicalDB stored in this table 
		#          by LogicalDB name.
		# returns: integer key of the LogicalDB or None if a LogicalDB 
		#          with provided name doesn't exist.
		# exceptions: none.
		"""
		db = self.getDBbyName(LogicalDBName)
		if db is None:
			return None
		else:
			return db.getKey()

	def dbkeys(self):
		"""
		# requires: nothing:
		# effects: builds list of LogicalDBkeys for all LogicalDBs in this
		#          table.
		# returns: list of integer keys.
		# exceptions: none.
		"""
		return self.DBbyKey.keys()
	


class ActualDB:
	"""
	An "Actual Database" in MGI. Corresponds to the entries in the ACC_ActualDB 
    table in the MGI database.
	"""
	def __init__(self, actualdbname, actualdbkey, logicaldbname, logicaldbkey,
                       active, url, allowsMultiple, delimiter):
		""" constructor
		# requires: 
		#    actualdbname: name of the ActualDB (string).
		#    actualdbkey: primary key/identifier of the ActualDB (integer).
		#    logicaldbname: name of the LogicalDB this ActualDB is associated 
		#                   with (string).
		#    logicaldbkey: primary key/identifier of the LogicalDB this ActualDB
        	#                  is associated with (integer).
		#    active: integer (1|0).  Indicates whether actualdb is logically
		#            enabled or not. 
		#    url: Uniform Resource Locator for this ActualDB.
		#    allowsMultiple: integer (1|0). Indicates whether URL target CGI
		#         will accept multiple arguments in a single query.
		#    delimiter: if allowsMultiple is true, a character used to delimit
        	#               the multiple CGI arguments (string), or None.
		# effects: initializes object with provided parameters. 
		# exceptions: none
		"""
		self.name = actualdbname
		self.key = actualdbkey
		self.logicaldbname = logicaldbname
		self.logicaldbkey = logicaldbkey
		self.active = active
		self.url = url
		self.allowsMultiple = allowsMultiple
		self.delimiter = delimiter

	def getName(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the name of this object (string)
		# exceptions: none
		"""
		return self.name

	def getKey(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the key/identifier of this object. This is the 
		#          _ActualDB_key from ACC_ActualDB (integer).
		# exceptions: none
		"""
		return self.key

	def getLogicalDBName(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the name of the LogicalDB associated with this
		#          ActualDB (string).
		# exceptions: none
		"""
		return self.logicaldbname

	def getLogicalDBKey(self):
		"""
		# requires: nothing
		# effects: none
		# returns: the key of the LogicalDB associated with this
		#          ActualDB (integer).
		# exceptions: none
		"""
		return self.logicaldbkey
	
	def isActive(self):
		"""
		# requires: nothing
		# effects: none
		# returns: 1|0, depending on whether ActualDB is logically active 
		#          or not. 
		# exceptions: none
		"""
		return self.active
	
	def getURL(self):
		"""
		# requires: nothing
		# effects: none
		# returns:  URL associated with this DB (string).
		# exceptions: none
		"""
		return self.url
	
	def acceptsMultiple(self):
		"""
		# requires: nothing
		# effects: none
		# returns: 1|0, depending on whether ActualDB's associated CGI
		#          script accepts multiple arguments in a single query. 
		# exceptions: none
		"""
		return self.allowsMultiple

	def getDelimiter(self):
		"""
		# requires: nothing
		# effects: none
		# returns: delimiter (string) used to separate multiple arguments to
		#          the CGI associated with this ActualDB.  Delimiter is ""
		#          if no delimiter exists.
		# exceptions: none
		"""
		return self.delimiter
 

class ActualDBTable:
	"""
	# An in-memory representation of the ACC_ActualDB table in Sybase.
	"""
	def __init__(self, logicalDBTable):
		""" constructor
		# requires: 
		#    logicalDBTable: LogicalDBTable object.
		# effects: creates a reference to the logicalDBTable object 
		#          associated with this object, and loads table. 
		# exceptions: SQL exceptions
		"""
		self.DBbyName = {}
		self.DBbyKey = {}
		self.logicalDBTable = logicalDBTable
		self.loadtable() 

	def loadtable(self):
		"""
		# requires: nothing
		# effects: Queries the database for the contents of the ACC_ActualDB
		#          table.
		# returns: nothing
		# exceptions: SQL exceptions
		"""
		command = 'select name, _ActualDB_key, _LogicalDB_key, active, url, allowsMultiple, delimiter from ACC_ActualDB'
		results = sql(command, 'auto')
			
		for result in results:
			actualdbname = result['name']
			actualdbkey = result['_ActualDB_key']
			logicaldbkey = result['_LogicalDB_key']
			active = result['active']
			url = result['url']
			allowsMultiple = result['allowsMultiple']
			delimiter = result['delimiter']

			logicaldbname = self.logicalDBTable.getNamebyKey(logicaldbkey)
			adb = ActualDB(actualdbname, actualdbkey, logicaldbname, 
                           logicaldbkey, active, url, allowsMultiple, delimiter)
			if not self.DBbyName.has_key(logicaldbname):
				self.DBbyName[logicaldbname] = {}
			self.DBbyName[logicaldbname][actualdbname] = adb 
			if not self.DBbyKey.has_key(logicaldbkey):
				self.DBbyKey[logicaldbkey] = {}
			self.DBbyKey[logicaldbkey][actualdbkey] = adb 


	def getDBbyKeys(self, LogicalDBKey, ActualDBKey=None):
		"""
		# requires:
		#    LogicalDBKey: integer.
		#    ActualDBKey: integer.
		# effects: If LogicalDBKey is a valid key in this table, and 
		#          ActualDBKey is not provided, returns a list of ActualDB
		#          objects with the associated LogicalDBKey. The list may be
		#          empty.
		#
		#          If both keys are provided, a single ActualDB object is 
        	#          returned.
		#
		#          If no match exists, None is returned.
		# returns: a list of ActualDB objects | an empty list | None	
		# exceptions: none
		"""
		if ActualDBKey is None:
			if self.DBbyKey.has_key(LogicalDBKey):
				rl = []
				for adbkey in self.DBbyKey[LogicalDBKey].keys():
					rl.append(self.DBbyKey[LogicalDBKey][adbkey])
				return rl 
			else:
				return [] 
		else:
			if self.DBbyKey.has_key(LogicalDBKey):
				dbdict = self.DBbyKey[LogicalDBKey]
				if dbdict.has_key(ActualDBKey):
					return dbdict[ActualDBKey]
				else:
					return None
			else:
				return None


	def getDBbyNames(self, LogicalDBName, ActualDBName=None):
		"""
		# Identical to getDBbyKeys, except that Logical/ActualDB names 
		# instead of keys are used as parameters.
		"""
		if ActualDBName is None:
			if self.DBbyName.has_key(LogicalDBName):
				rl = []
				for adbname in self.DBbyName[LogicalDBName].keys():
					rl.append(self.DBbyName[LogicalDBName][adbname])
				return rl 
			else:
				return None
		else:
			if self.DBbyName.has_key(LogicalDBName):
				dbdict = self.DBbyName[LogicalDBName]
				if dbdict.has_key(ActualDBName):
					return dbdict[ActualDBName]
				else:
					return None
			else:
				return None


	def getDBbyOrganism(self, organismKey):
		"""
		# requires: _Sp
		# effects: finds all LogicalDBs that have a matching
		#	_Organism_key, then find the appropriate ActualDB
		#	based on that LogicalDB.
		#
		#	Note: there should be only one ActualDB for all 
		#	organism-specific logical databases at this time.
		#	If this isn't the case, an exception is raised.
		#
		#	This method also assumes that there is only one
		#	Logical DB for a given organism.  This is done because
		#	this was the current behavior of MGIlink.py, for which
		#	this method was created.  If there is more than one
		#	logical database for the same organism, a warning is
		#	generated, and one is chosen arbitrarily. 
		#
		# returns: A single ActualDB that has an associated LogicalDB
		#	which is organism specific and whose associated
		#	organism key matches organismKey.
		# exceptions: NoLogicalDBforOrganism,
		#	MultLogicalDBsforOrganism
		"""

		ldbkeys = self.logicalDBTable.dbkeys()
		names = []
		for ldbkey in ldbkeys:
			ldb = self.logicalDBTable.getDBbyKey(ldbkey)
			if ldb.getOrganismKey() == organismKey:
				names.append(ldb.getName())
	
		numldbs = len(names)

		if numldbs > 1:
			raise MultLogicalDBsforOrganism, organismKey
		elif numldbs == 0:
			raise NoLogicalDBforOrganism, organismKey

		# numldbs == 1
		ldbname = names[0]
		adblist = self.getDBbyNames(ldbname)

		if adblist is None:
			raise NoActualDBforOrganism, organismKey

		numadbs = len(adblist)
		if numadbs > 1:
			raise MultActualDBsforOrganism, organismKey
		elif numadbs == 0:
			raise NoActualDBforOrganism, organismKey
		else:  # numadb == 1
			return adblist[0]

	# method alias for backward compatability

	getDBbySpecies = getDBbyOrganism

# Functions
# =========

def get_LogicalActualDBTables():
	"""
	# requires: nothing.
	# effects: Creates two initialized objects LogicalDBTable and ActualDBTable.
	#          Both active and non-active ActualDBs are included in the 
	#          ActualDBTable.
	# returns: a tuple: (LogicalDBTable, ActualDBTable)
	# exceptions: none
	"""		
	ldbTable = LogicalDBTable()
	# read from the ACC_ActualDB table in the database
	adbTable = ActualDBTable(ldbTable)

	return (ldbTable, adbTable)


def parse_id( s ):
	"""Given an accession ID expression, returns a nice datastructure.
	#
	# See parse_expr() for more info.
	#
	"""

	return parse_expr( s )


def sortActualDBsByName(a,b):
	# sorts a list of ActualDB objects in ascending order by name
	aname = a.getName()
	bname = b.getName()
	if aname < bname:
		return -1
	elif aname > bname:
		return 1
	else: # aname == bname:
		return 0


def get_source( LogicalDB, Acc_ID, actualDBTable):
	"""Returns HTML containing links to appropriate DBs.
	#
	# LogicalDB - Name of the LogicalDB ('MGI', 'GDB', 'Sequence DB', etc.)
	# Acc_ID - A string or list of strings that are accession IDs in MGD.
	# actualDBTable - an instance of the ActualDBTable class. Note that
	#                 this is a required argument now.
	#
	"""

	if type(Acc_ID) == type(''):
		Acc_ID = [Acc_ID]

	adblist = actualDBTable.getDBbyNames(LogicalDB)
	#debug("adblist: %s" % `adblist`)
	adblist.sort(sortActualDBsByName)
	
	links = []

	for adb in adblist:  # note these are objects, not names now
		if adb.getLogicalDBName() == 'MGI':
			html = 'MGI' 
		else:
			url = adb.getURL() 
			delimiter = adb.getDelimiter() 
			adbname = adb.getName()
			if url is None:
				html = adbname
			elif delimiter is None:
				url = re.sub('@@@@', Acc_ID[0], url)
				html = '<A HREF="%s">%s</A>' % (url, adbname)
			else:
				url = re.sub('@@@@', string.joinfields(Acc_ID, delimiter), url)
				html = '<A HREF="%s">%s</A>' % (url, adbname)
		links.append( html )
	s = string.joinfields( links, ', ' )
	s = '(' + s + ')'

	return s



def get_links(_Object_key, MGIType=None, LogicalDB=None, view='Acc_View',
		preferred=1):
	"""Returns a Python dictionary of accession IDs for given _Object_key.
	#
	# The dictionary keys are accession IDs, the values are HTML strings
	# containing links to various databases.
	#
	# Requires:
	#	_Object_key -- An integer representing the DB key.
	#	MGIType -- 'Reference', 'Marker', 'Segment', 'Experiment' or
	#		None.
	#	LogicalDB -- 'MGI', 'Sequence DB', etc. or None.
	#	view -- The name of the view to use for looking up accession
	#		IDs.  This might be necessary for, say, probes that
	#		have no reference (PRB_AccNoRefs_View?).
	#	preferred -- a 0|1|None flag indicating whether preferred or
	#		non-preferred accIDs should be returned.  That is, rows
	#		in ACC_Accession where preferred=1 or preferred=0.  A
	#		value of None means to ignore the preferred column
	#		altogether.
	#
	"""
	command = 'select accID, LogicalDB, private from %s where _Object_key = %d\n' % (view, _Object_key)

	if preferred is not None:
		command = command + 'and preferred = %d\n' % preferred

	if MGIType is not None:
		command = command + 'and MGIType = \'%s\'\n' % MGIType

	if LogicalDB is not None:
		command = command + 'and LogicalDB = \'%s\'\n' % LogicalDB

	results = sql(command, 'auto')

	logicalDBTable, actualDBTable = get_LogicalActualDBTables()

	accIDs = {}
	for result in results:
		accID = result['accID']
		LogicalDB = result['LogicalDB']
		private = result['private']
		if private == 1:
			accIDs[get_source(LogicalDB, accID, actualDBTable)] = ''
		else:
			accIDs[accID] = get_source(LogicalDB, accID, actualDBTable) 
	return accIDs


# Alias that will go away soon! (Don't use)
get_accIDs = get_links


def get_accID(_Object_key, MGIType=None, LogicalDB=None, view='Acc_View',
		preferred=1):
	"""Returns accession ID, list of accession IDs or none for _Object_key.
	#
	# Requires:
	#	Arguments are the same as get_links().
	#
	# Implentation note:
	#	This is just a wrapper around get_links for now.  Obviously, it
	#	could be implemented a little more efficiently.  :-)
	#
	"""
	accIDs = get_accIDs(_Object_key, MGIType, LogicalDB, view, preferred)
	keys = accIDs.keys()
	if len(keys) == 1:
		return keys[0]
	elif len(keys) > 1:
		return keys
	else: # if keys = []
		return None


def get_Accession_key(_Object_key, MGIType=None, LogicalDB=None,
		view="ACC_View"):
        """Returns _Accession_key(s) for a given _Object_key.
 	#
	# Requires:
	#	_Object_key -- An integer representing the DB key.
	#	MGIType -- 'Reference', 'Marker', 'Segment' or 'Experiment'.
	#	LogicalDB -- A string representing the LogicalDB ('MGI',
	#		'Sequence DB'...)
	#	view -- The view/table to use.
	#
        """
	command = 'select _Accession_key from %s where _Object_key = %d\n' % (view, _Object_key)

	if MGIType is not None:
		command = command + 'and MGIType = \'%s\'\n' % MGIType

	if LogicalDB is not None:
		command = command + 'and LogicalDB = \'%s\'\n' % LogicalDB

	results = sql(command, 'auto')

	if len(results) == 1:
		_Accession_key = results[0]['_Accession_key']
	elif len(results) > 1:
		_Accession_key = []
		for result in results:
			_Accession_key.append(result['_Accession_key'])
	else:
		_Accession_key = None

	return _Accession_key
 

def get_Object_key( accID, MGIType=None, _MGIType_key=None ):
	"""Returns _Object_key, list of _Object keys or None for given accID.
	#
	# Requires:
	#	accID -- A string.
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

	results = sql(command, 'auto')

	if len(results) == 1:
		_Object_key = results[0]['_Object_key']
	elif len(results) > 1:
		_Object_key = []
		for result in results:
			_Object_key.append(result['_Object_key'])
	else:
		_Object_key = None

	return _Object_key


def build_sql( search, table=None ):
	"""Constructs the part of an SQL query that deals with accession IDs.
	#
	# Requires:
	#	search -- An accession ID search expression
	#		('J:1000..2000,MGI:12345')
	#	table -- The name (or shorthand) of the accession table.
	#
	# Example:
	#
	#	Given search='J:1000' and table='a', build_sql returns:
	#
	#		'a.prefixPart=\'J:\' and a.numericPart=1000'
	#
	"""

	# determine what (if anything) will be prepended to each column name
	if table is None:
		pre = ''
	else:
		pre = '%s.' % table

	id = parse_id( search )
	if type(id) == type(''):
		return id

	where_list = []
	for prefixPart in id.keys():
		sets = []

		ranges = []
		for numericPart in id[prefixPart]:
			if type(numericPart) == type(1):
				sets.append(numericPart)
			elif type(numericPart) == type((0,0)):
				ranges.append(numericPart)
		if len(sets) == 0:
			where_list.append(
				'(%sprefixPart=\'%s\'' % \
					(pre, prefixPart) \
				+ ' and %snumericPart is null)' % pre)
		elif len(sets) == 1:
			if prefixPart:
				where_list.append(
					'(%sprefixPart=\'%s\'' % \
						(pre, prefixPart) \
					+ ' and %snumericPart=%s)' % \
						(pre, sets[0]) )
			else:
				where_list.append(
					'(%sprefixPart is null' % pre\
					+ ' and %snumericPart=%s)' % \
						(pre, sets[0]) )
		elif len(sets) > 1:
			s = str(sets)
			s = re.sub( '\[', '(', s )
			s = re.sub( '\]', ')', s )
			if prefixPart:
				where_list.append(
					'(%sprefixPart=\'%s\'' % \
					(pre, prefixPart) \
					+ ' and %snumericPart in %s)' % \
					(pre, s) )
			else:
				where_list.append(
					'(%sprefixPart is null' % pre \
					+ ' and %snumericPart in %s)' % \
					(pre, s) )

		for range in ranges:
			if prefixPart:
				where_list.append(
					'(%sprefixPart=\'%s\'' % \
						(pre, prefixPart) \
					+ ' and %snumericPart' % pre \
					+ ' between %d and %d)' % range)
			else:
				where_list.append(
					'(%sprefixPart is null' % pre \
					+ ' and %snumericPart' % pre \
					+ ' between %d and %d)' % range)


	where = '(%s)' % string.joinfields( where_list, ' or ' ) \
		+ ' and %sprivate = 0' % pre
	return where


def get_MGIType_key( MGIType ):
	"""Returns the _MGIType_key for a given MGIType or None if invalid Type.
	#
	# Requires:
	#	MGIType -- A string representing the object type ('Marker',
	#		'Segment'...)
	#
	"""
	command = 'select _MGIType_key from ACC_MGIType where name = \'%s\'' % (MGIType)

	results = sql(command, 'auto')
	if results:
		_MGIType_key = results[0]['_MGIType_key']
	else:
		_MGIType_key = None

	return _MGIType_key


def get_LogicalDB_key( LogicalDB ):
	"""Returns the _LogicalDB_key for a given LogicalDB or None if invalid.
	#
	# Requires:
	#	LogicalDB -- A string representing the LogicalDB('MGI',
	#		'Sequence DB'...)
	"""
	command = 'select _LogicalDB_key from ACC_LogicalDB where name = \'%s\'' % (LogicalDB)

	results = sql(command, 'auto')
	if results:
		_LogicalDB_key = results[0]['_LogicalDB_key']
	else:
		_LogicalDB_key = None

	return _LogicalDB_key


def get_MGIType( _MGIType_key ):
	"""Returns the MGIType for a given _MGIType_key or None if invalid.
	#
	# Returns 'Marker', 'Segment', 'Experiment', 'Reference' or None.
	#
	# Requires:
	#	_MGIType_key -- An integer.
	#
	"""
	command = 'select name from ACC_MGIType where _MGIType_key = %d' % (_MGIType_key)

	results = sql(command, 'auto')
	if results:
		MGIType = results[0]['name']
	else:
		MGIType = None

	return MGIType


def get_LogicalDB( _LogicalDB_key ):
	"""Returns the LogicalDBfor a given _LogicalDB_key.
	#
	# Returns a string ('MGI', 'Sequence DB', etc.) if valid, None
	# otherwise.
	#
	# Requires:
	#	_LogicalDB_key -- An integer.
	#
	"""

	command = 'select name from ACC_LogicalDB where _LogicalDB_key = %d' % (_LogicalDB_key)

	results = sql(command, 'auto')
	if results:
		LogicalDB = results[0]['name']
	else:
		LogicalDB = None

	return LogicalDB


def get_jnumID(_Refs_key):
	"""Returns a jnumID for a given _Refs_key.
	#
	# Requires:
	#	_Refs_key - An integer.
	#
	"""
	accIDs = get_accID(
		_Refs_key,
		MGIType='Reference',
		LogicalDB='MGI',
		)

	# If no J Number return None
	jnumID = None
	for accID in accIDs:
		if string.find( accID, 'J:' ) == 0:
			jnumID = accID
			break

	return jnumID

##################################################
# routines to parse accession number query expressions
# (formerly in accqpars.py)
#
# Purpose: routines to parse accession number query expressions.
# Externally called routines:
#	parse_expr() (see function spec, below)

# Here is the query expression grammar:
#
# (acc number query expr)
# acc_expr        : single_acc_expr
#                 : single_acc_expr sep_char acc_expr
# 
# (one or more separator char)
# sep_char        : " "
#                 : ","
#                 : sep_char sep_char
# 
# (acc number expression w/ one prefix, no spaces or commas)
# single_acc_expr : simple_accnum
#                 : simple_accnum tail
# 
# (simple, single acc number (prefix + numeric part))
# simple_accnum   : <string w/o ".."  "+" and spaces>
# 
# (something that follows a number and starts w/ "+" or "..")
# tail            : range_tail
#                 : plus_tail
# 
# (something that follows a number and starts w/ "..")
# range_tail      : ".." number
#                 : ".." number plus_tail
# 
# (something that follows a number and starts w/ "+")
# plus_tail       : "+" number
#                 : "+" number tail

# Implementation:
# straight forward recursive descent parsing based on the above grammar,
#   except parse_expr() pulls apart single_acc_exprs at the sep_chars and
#   then does recursive descent on each individual single_acc_expr
#   independently.
#
# The string to parse is kept in the global CurStringToParse string variable.
#    each parsing routine removes what it parses from CurStringToParse.
# Errors are handled by each parsing routine returning a special code.
#    (we tried using a pgmr defined exception, but ran into problems w/
#     the web interface exception traceback mechanism)

CurStringToParse = ""	# the current string to parse, shared by the parsing
			#  routines below

DefaultErrorMsg = "Error:  Invalid accession ID query."
			# the default error msg to use for syntax errors

def parse_expr (s	# string, the query expression to parse
		):
    # Purpose: Parse an acc number query expression 's'.
    # Returns: If no errors,
    #		dictionary whose keys are the prefixparts of 's',
    #		    the value of each key is a list consisting of numeric
    #		    parts (for individual acc numbers), and pairs (tuples)
    #		    for ranges.
    #	       If syntax error in 's',
    #		string containing an error msg.
    # Assumes: Nothing
    # Example: For s= "MGI:123+345..350+355 G432,789 MGI:654 9876 FOO",
    #          returns: { "MGI:" : [123, (345,350), 355, 654],
    #			  "G"    : [432,],
    #			  ""     : [789, 9876],
    #			  "FOO"  : []}

    global CurStringToParse
    retval = {}		# return value, assume no errors, start w/ empty dict

    # set single_accnum_exprs[] to list of individual separated exprs from s
    single_accnum_exprs = s.split(',')

    for sae in single_accnum_exprs:		# for each single_accnum_expr
	CurStringToParse = sae

	(prefix, numeric) = simple_accnum()

	if ( not retval.has_key( prefix) ):	# new prefix
	    retval[ prefix] = []		# init to empty list
	
	retval[ prefix].append( numeric)	# add this number to list

	if ( CurStringToParse != "" ):	# have a tail to parse
	    msg = tail( retval[ prefix]) # parse tail
	    if ( msg is not None ):		#  tail found an error
		retval = msg
		break
    #end for

    return (retval)
# end parse_expr() 

def simple_accnum (
    ):
    # Purpose: Parse from CurStringToParse the prefix and 1st numeric part.
    # Returns: pair (tuple) consisting of:
    #		prefix (string)	- the prefix part of the 1st accnum in 's'
    #		numeric (int or None if acc num has no numeric part)
    # Assumes: CurStringToParse is set.
    # Effects: removes prefix and numeric part from CurStringToParse.

    global CurStringToParse

    # set endnum to the index in CurStringToParse of the first "+" or the
    #   first ".."
    # (There must be an easier way to do this w/ regexprs, but I can't see
    #   one, the problem is that the stuff before the first ".." can contain
    #   a "."!)
    #
    thelen = len(CurStringToParse)

    firstplus_re = re.search( "\+", CurStringToParse);  # find the first "+"

    if (firstplus_re is None):		# no plus found
        firstplus = thelen +1
    
    endnum = firstplus			# assume "+" is before any ".."s
    
    firstdotdot_re = re.search( "\.\.", CurStringToParse);  # find first ".."

    if (firstdotdot_re is None):	# no ".." found
        firstdotdot = thelen +1
    
    if (firstdotdot < endnum):		# ".." before "+"
        endnum = firstdotdot
    ## end set endnum
    
    accnum = CurStringToParse[0:endnum]
    CurStringToParse = CurStringToParse[endnum:]

    return (split_accnum(accnum))
# end simple_accnum() 

def split_accnum(accnum	# accession number
    ):

    # set prefix to the prefix part, numeric to the numeric part

    matchpre = re.compile( "^((.*[^0-9])?)([0-9]*)")
				# group(1) = prefix (or "")
				# group(3) = numeric part (or "")
				# .*      anything
				# [^0-9]  non-digit
				# \(.*[^0-9]\)? optional prefix
				# \([0-9]*\)  optional numeric part

    match_result = matchpre.match(accnum)
    prefix = match_result.group(1)
    numeric = match_result.group(3)

    if (numeric != ""):			# have a none null numeric part
        numeric = string.atoi( numeric)	# convert it to int
    else:				# have a null numeric part
        numeric = None
    
    return (prefix, numeric)
# end split_accnum()

def tail ( vallist	# list of numeric parts and range pairs seen so far.
    ):
    # Purpose: Parse a tail expression (starting w/ ".." or "+") from
    #		CurStringToParse.
    # Returns: None if no error, string holding error msg if syntax error.
    # Assumes: If CurStringToParse starts w/ "..", then the 1st number
    #		of the range is the last value in vallist[].
    # Effects: Removes the parsed tail from CurStringToParse.
    #	       Updates vallist[] to hold the parsed tail.

    global CurStringToParse

    if ( CurStringToParse[0:2] == ".."):
        return (range_tail( vallist))
    elif ( CurStringToParse[0] == "+"):
	return (plus_tail( vallist))
    else:
	return (DefaultErrorMsg)
# end tail() 

def range_tail ( vallist # list of numeric parts and range pairs seen so far.
    ):
    # Purpose: Parse a range_tail expression (starting w/ "..")
    # Returns: None if no error, string holding error msg if syntax error.
    # Assumes: First two chars in CurStringToParse are "..".
    #	       Last value in vallist[] is the first value in the range.
    # Effects: Removes the "..<number>" from CurStringToParse.
    #	       Converts the last value in vallist[] to a tuple (pair)
    #		representing the range.

    global CurStringToParse

    CurStringToParse = CurStringToParse[2:]

    secondnumber = number()
    if (type(secondnumber) == types.StringType):	# number() found error
        return ("Error: Invalid accession ID range.")

    firstnumber  = vallist[-1]
    if (firstnumber == None):		# had "prefix..number"
        return ("Invalid accession number range.")
    else:
        vallist[-1] = (firstnumber, secondnumber)
    
    if ( CurStringToParse != ""):
	if ( CurStringToParse[0] == "+"):
	    return (plus_tail( vallist))
	else:
	    return (DefaultErrorMsg)
    return (None)
# end range_tail() 

def plus_tail ( vallist # list of numeric parts and range pairs seen so far.
    ):
    # Purpose: Parse a plus_tail expression (starting w/ "+").
    # Returns: None if no error, string holding error msg if syntax error.
    # Assumes: First char in CurStringToParse is "+".
    # Effects: Removes the "+<number>" from CurStringToParse.
    #	       Appends the number to the vallist.

    global CurStringToParse

    CurStringToParse = CurStringToParse[1:]
    thenumber = number()
    if (type(thenumber) == types.StringType):	# number() found error
        return (DefaultErrorMsg)
    vallist.append( thenumber)
    
    if ( CurStringToParse != ""):
        return (tail( vallist))
    
    return (None)
# end plus_tail() 

def number (
    ):
    # Purpose: Parse a number expression from CurStringToParse.
    # Returns: integer (if number found),
    #	       string w/ errmsg if number not found.
    # Assumes: nothing
    # Effects: removes the "<number>" from CurStringToParse.

    global CurStringToParse

    numre = re.compile( "^([0-9]+)" )
    numre_result = numre.match(CurStringToParse)

    if ( numre_result is None ):	# num not found!
        return (DefaultErrorMsg)
    else:						# num found
	numstr = numre_result.group( 1 )
	CurStringToParse = CurStringToParse[ len(numstr):]
        return (string.atoi( numstr))
# end number() 

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
# Copyright © 1996, 1999, 2002 by The Jackson Laboratory
# All Rights Reserved
#

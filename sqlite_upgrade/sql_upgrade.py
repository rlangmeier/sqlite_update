# -*- coding: utf-8 -*-
"""Automate create and upgrade a SQLite database schema with the help of 'user_version'

author: Robert Langmeier
date: 2018-09-09

Based on
    https://levlaz.org/sqlite-db-migrations-with-pragma-user_version/

Sql script file name format, proposed pattern:
    ^(\d+)_(full|upgrade|mandatory)_{schema_name}_(.*).sql$
    
Regex Groups:
    Version number
    Type of script (full, upgrade or mandatory)
    Schema or Db name (valid variable are: db_name, db_ext and schema_name)
    Description

user_version:
    is always 0 when the database is created

"""

__version__ = '1.0'
__author__ = 'Robert Langmeier'

# %%

import os
import sys
import logging
import glob
import re
import sqlite3 as sqlite

from . import log

__all__ = ["SqliteSchemaUpgrade"]


# %%

class SqliteSchemaUpgrade:
    """
    """

    def __init__(self, db_full_name):
        """Open or create the SQLite database
        """
        
        # Split database name
        db_path, db_name_ext = os.path.split(db_full_name)
        db_name, db_ext = os.path.splitext(db_name_ext)

        self.db_full_name = db_full_name
        self.db_path = db_path
        self.db_name = db_name
        self.db_ext = db_ext

        # Must be a directory
        if not os.path.isdir(self.db_path):
            raise FileNotFoundError("'{}' must be a directory".format(self.db_path))

        if os.path.isfile(self.db_full_name):
            self.conn = sqlite.connect(self.db_full_name)
        else:
            if os.path.isdir(self.db_full_name):
                raise IsADirectoryError("'{}' is a directory".format(self.db_full_name))

            # db does not exist, create an empty one
            # user_version will alwys be 0 in this case
            self.conn = sqlite.connect(self.db_full_name)

        # extract current version
        user_version = self.get_user_version()
        log.debug("db='{}' user_version={}".format(self.db_full_name, user_version))


    def __del__(self):
        self.conn.close()


    def get_user_version(self):
        """Return the version of the last executed SQL script"""
        r = self.conn.cursor().execute('PRAGMA user_version').fetchone()
        return r[0]


    def search_sql_scripts(self, schema_name,
                           sql_script_path,
                           sql_script_recurse=False,
                           sql_script_pattern=r'^(\d+)_(full|upgrade|mandatory)_{schema_name}_(.*).sql$'):
        """Get the list of all SQL scripts in the path that follow the pattern definition.
        Search recursivly in subdirectories if specified.
        
        
        schema_name: database schema name
        sql_script_path: search SQL scripts in this path
        sql_script_recurse: when True, search also in subdirectories
        sql_script_pattern: search SQL scripts that follow this pattern
        """
        
        self.schema_name = schema_name
        self.sql_script_path = os.path.abspath(sql_script_path)
        self.sql_script_pattern = sql_script_pattern

        # Must be a directory
        if not os.path.isdir(self.sql_script_path):
            raise FileNotFoundError("'{}' must be a directory".format(self.sql_script_path))

        # Search file that follow this pattern
        pattern = self.sql_script_pattern.format(db_name=self.db_name, 
                                                 db_ext=self.db_ext, 
                                                 schema_name=self.schema_name)
        repattern = re.compile(pattern)
        if repattern.groups != 3:
            raise ValueError("3 capturing groups are expected in the pattern")

        self.script_files = []
        for root, dirs, files in os.walk(self.sql_script_path):
            for file in files:
                m = repattern.match(file)
                if m:
                    self.script_files.append([int(m.group(1)),
                                              file,
                                              m.group(2),
                                              m.group(3),
                                              os.path.join(root, file)])
            if not sql_script_recurse:
                break

        # Enforce global sorting of all versions
        self.script_files.sort()

        # Check version number uniqueness
        lst_ver = [r[0] for r in self.script_files]
        if len(set(lst_ver)) != len(lst_ver):
            raise Exception("Script versions are not unique")

        # Check script types
        set_types = set([r[2] for r in self.script_files])
        if set_types.difference({'full','upgrade','mandatory'}):
            raise Exception("Script types are only 'full', 'upgrade' or 'mandatory'")

        if self.script_files:

            # Check full script presence in the first place of the list
            if self.script_files[0][2] != 'full':
                raise Exception("The first sql script should be a 'full' schema")

            # Check that's only one full script type
            if len([r[0] for r in self.script_files if r[2] == 'full']) > 1:
                raise Exception("Only one 'full' schema allowed")

        else:
            
            raise Exception("No SQL script found for '{}' pattern".format(pattern))


    def get_new_scripts(self):
        
        # Search scripts types to be executed
        user_version = self.get_user_version()
        scripts = [r for r in self.script_files if r[0] > user_version]
        return scripts


    def is_upgrade_mandatory(self):
        
        script_types = [r[2] for r in self.get_new_scripts()]
        return 'mandatory' in script_types


    def is_upgrade_available(self):
        
        len_scripts = len(self.get_new_scripts())
        return len_scripts > 0


    def create_migrate_db(self, exec_one=False):
        """Apply new SQL scripts based on user_version
        """
        
        # Search scripts to be executed
        scripts = self.get_new_scripts()

        # Iterate trough scripts and execute them
        for ver, file, schema, desc, path in scripts:
            
            log.debug("db='{}' apply='{}'".format(self.db_full_name, file))
            
            with open(path, 'rt') as f:
                self.conn.cursor().executescript(f.read())
                user_version = self.get_user_version()
                if user_version < ver:

                    # force user_version to the expected version
                    self.conn.cursor().execute('PRAGMA user_version={}'.format(ver))
                    user_version = self.get_user_version()

                    # warning
                    log.warning("db='{}' '{}' doesn't update user_version correctly".format(self.db_full_name, file))
            
            if exec_one:
                break

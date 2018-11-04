# -*- coding: utf-8 -*-
"""This package allows you to create or update a database schema.

Usage:
    import sqlite_upgrade
    
    # Open or create the database
    sql_inst = sqlite_upgrade.SqliteSchemaUpgrade('mydb.db')
    
    # Search all scripts 
    sql_inst.search_sql_scripts('SchemaTest', 'tests_data')
    
    # Apply all scripts that have not been played
    sql_inst.create_migrate_db()

    del sql_inst
"""

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from .sql_upgrade import *

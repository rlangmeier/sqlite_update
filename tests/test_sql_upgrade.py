# -*- coding: utf-8 -*-
"""Test script for the creation or the upgrade of a sqlite database schema 

author: Robert Langmeier
date: 2018-09-09
"""

import os
import sys
import logging
import unittest

import sqlite_upgrade


def remove_file(file):
    if os.path.isfile(file):
        os.remove(file)


class TestSqliteUpgrade(unittest.TestCase):
 
    def setUp(self):
        self.db1_name = r'tests_data\Test1.db'
        remove_file(self.db1_name)
        self.sql = sqlite_upgrade.SqliteSchemaUpgrade(self.db1_name)
    
    def tearDown(self):
        del self.sql
 
    def test_create_update_1(self):
        self.sql.search_sql_scripts('SchemaTest', 'tests_data')
        self.sql.create_migrate_db()
        self.assertEqual(self.sql.get_user_version(), 2)
        
    def test_create_update_2_1(self):
        self.sql.search_sql_scripts('SchemaTest', 'tests_data')
        self.sql.create_migrate_db()
        self.assertFalse(self.sql.is_upgrade_available())

    def test_create_update_2_2(self):
        self.sql.search_sql_scripts('SchemaTest', 'tests_data')
        self.sql.create_migrate_db()
        self.sql.search_sql_scripts('SchemaTest', 'tests_data', sql_script_recurse=True)
        self.assertTrue(self.sql.is_upgrade_available())

    def test_create_update_3_1(self):
        self.sql.search_sql_scripts('SchemaTest', 'tests_data')
        self.sql.create_migrate_db()
        self.assertFalse(self.sql.is_upgrade_mandatory())

    def test_create_update_3_2(self):
        self.sql.search_sql_scripts('SchemaTest', 'tests_data')
        self.sql.create_migrate_db()
        self.sql.search_sql_scripts('SchemaTest', 'tests_data', sql_script_recurse=True)
        self.assertTrue(self.sql.is_upgrade_mandatory())

    def test_create_update_4(self):
        self.sql.search_sql_scripts('SchemaTest', 'tests_data', sql_script_recurse=True)
        self.sql.create_migrate_db()
        self.assertEqual(self.sql.get_user_version(), 5)


if __name__ == "__main__":

    # Prepare logger
    logger = logging.getLogger('sqlite_upgrade')

    # We are testing and debuging, we only want one handler, so we clear all handlers
    logger.handlers = []
    
    # log level
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    fh = logging.FileHandler(r'tests_data\test.log')

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(fh)

    logger.warning('Test sqlite_upgrade')

    unittest.main()

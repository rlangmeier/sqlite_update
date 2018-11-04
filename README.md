# sqlite_upgrade

This package allows you to automate create and update a database schema.

Sample usage for this package is:
```
import sqlite_upgrade

# Open or create the database
sql_inst = sqlite_upgrade.SqliteSchemaUpgrade('mydb.db')

# Search all scripts 
sql_inst.search_sql_scripts('SchemaTest', 'tests_data')

# Apply all scripts that have not been played
sql_inst.create_migrate_db()

del sql_inst
```


## 1. [DATABASE MIGRATION GUIDELINE USING ALEIMBIC] (https://medium.com/@johnidouglasmarangon/using-migrations-in-python-sqlalchemy-with-alembic-docker-solution-bd79b219d6a)

## 2. [DATABASE RELATIONSHIPS TIPS](https://medium.com/@mandyranero/one-to-many-many-to-many-and-one-to-one-sqlalchemy-relationships-8415927fe8aa)
1. Initiate alembic migration

    ```shell
    alembic init migrations
    ```
2. Check if alembic is set up correctly

    ```shell
    alembic current
    ```
3. Generate first migrations
 
    ```shell
   alembic revision --autogenerate -m "Create a baseline migrations"
    ```
4. Run migration

    ```shell
    alembic upgrade head
    ```

### usefull comands

1. Check if alembic current head is in sync with base metadata

    ```shell
    alembic check
    ```
2. View the sql to be run

    ```shell
    alembic upgrade --sql head
    ```

### Useful tips
- To unblock a database after a partial migration was applied I follow these steps:

- **STEPS**
1. Determine which of the operations were applied.
2. Delete everything from the upgrade() function.
3. Edit the downgrade() function so that it only contains the reverse of the operations that were applied to your database.
4. Run flask db upgrade. This is going to succeed because now you are running an empty upgrade. The database version will be upgraded.
5. Run flask db downgrade. This will undo those partial changes that were applied earlier, and reset the database version back to the last good state.
6. Delete the migration script and try again with batch mode enabled.
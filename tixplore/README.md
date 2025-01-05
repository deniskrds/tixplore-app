## create db
aerich init -t app.databases.TORTOISE_ORM
aerich init-db
aerich migrate
aerich upgrade

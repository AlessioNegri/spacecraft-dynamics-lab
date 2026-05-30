cls

pyinstaller server.spec
rem pyinstaller --onefile --add-data "routers;routers" --add-data "schemas;schemas" --add-data "tasks;tasks" start.py
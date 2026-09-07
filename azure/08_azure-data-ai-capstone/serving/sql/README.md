# Azure SQL serving path

Run `schema.sql` in Query Editor or SSMS/Azure Data Studio. Then install the optional SQL dependency and load local Gold data:

```powershell
poetry install --with sql
poetry run python -m serving.sql.load_gold
```

The connection string can use `Authentication=ActiveDirectoryInteractive` so you do not have to store a SQL password in `.env`.

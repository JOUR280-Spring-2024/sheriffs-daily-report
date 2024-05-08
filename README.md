# Sheriff's Office Daily Report

This scraper extracts data from the Sheriff's [Office Daily Report](https://www.co.champaign.il.us/sheriff/publicdocuments.php) in Champaign County.

There are three types of reports in the web page above. We focused on the reports titled "Division of Corrections Daily Report".
Specifically, we extracted the table `Facility Population` (page 1) and `Custody Status` (page 2).

The data is stored as a SQLite database named `sheriff_daily_reports.sqlite`.

The code can be run every day to add new records to the database. Previous records are retained and new
records are added.

If you end up using this database in a news report, please give credit to Farrah Anderson.
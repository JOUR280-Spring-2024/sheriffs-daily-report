from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String
import pdfplumber
import requests
import pendulum
from bs4 import BeautifulSoup
from sqlalchemy.dialects.sqlite import insert

engine = create_engine('sqlite:///sheriff_daily_reports.sqlite')

metadata = MetaData()
custody_status_table = Table('custody_status', metadata,
                             Column('date', String, primary_key=True),
                             Column('custody_status', String, primary_key=True),
                             Column('count', Integer))
facility_table = Table('facility_count', metadata,
                       Column('date', String, primary_key=True),
                       Column('satellite_jail', Integer),
                       Column('out_of_facility', Integer))
metadata.create_all(engine)

session = requests.Session()
url = "https://www.co.champaign.il.us/sheriff/publicdocuments.php"
response = session.get(url)
soup = BeautifulSoup(response.text, "html.parser")

for link in soup.select("a"):
    if "ArchivedReports" in link["href"]:
        new_url = "https://www.co.champaign.il.us/sheriff/" + link['href']
        new_file = requests.get(new_url)
        new_filename = link.text
        with open(f"./report.pdf", "wb") as f:
            f.write(new_file.content)
        pdf = pdfplumber.open("./report.pdf")
        if "Division of Corrections Daily Report" in pdf.pages[0].extract_text():
            print(link['href'])
            page = pdf.pages[1]
            text = page.extract_text()
            new_text = text.split("\n")
            date = new_text[4]
            parsed_date = pendulum.from_format(date, 'dddd, MMMM DD, YYYY')
            formatted_date = parsed_date.to_date_string()
            data = new_text[6:-3]
            with engine.connect() as connection:
                for item in data:
                    count = item.split(' ')[-1]
                    custody_status = item.split(' ')[0:-1]
                    custody_status = " ".join(custody_status)
                    insert_query = insert(custody_status_table).values(custody_status=custody_status,
                                                                       date=formatted_date,
                                                                       count=count)
                    connection.execute(insert_query.on_conflict_do_nothing(index_elements=['custody_status', 'date']))
                connection.commit()
            page = pdf.pages[0]
            cropped_page = page.crop((36, 162, 36 + 178, 162 + 100))
            text = cropped_page.extract_text()
            list_text = text.split("\n")
            with engine.connect() as connection:
                satellite_jail = list_text[1].split(' ')[-1]
                out_of_facility = list_text[2].split(' ')[-1]
                insert_query = insert(facility_table).values(date=formatted_date,
                                                             satellite_jail=satellite_jail,
                                                             out_of_facility=out_of_facility)
                connection.execute(insert_query.on_conflict_do_nothing(index_elements=['date']))
                connection.commit()

import urllib.request  # using urllib, refered to its documentation for usage and error handling
import urllib.error
import bs4
import json
import numpy as np
import statistics
from datetime import datetime
import sys
from prettytable import (
    PrettyTable,
)  # using prettytable for formatting data output to user https://pypi.org/project/prettytable/

DEFAULT_ULR_FOR_DATA_FETCH = "https://questionnaire-148920.appspot.com/swe/data.html"
EXPECTED_TABLE_NAME = "salaries-table"
EXPECTED_TABLE_COLUMN_PLAYER_SALARY = ".player-salary"
EXPECTED_TABLE_COLUMN_PLAYER_YEAR = ".player-year"
EXPECTED_TABLE_COLUMN_PLAYER_LEVEL = ".player-level"
EXPECTED_TABLE_COLUMN_PLAYER_NAME = ".player-name"
MAX_NUM_OF_CLI_ARGS = 2


def default_data_fetch():
    try:
        return parse_salary_data(urllib.request.urlopen(DEFAULT_ULR_FOR_DATA_FETCH))
    except (urllib.error.HTTPError, urllib.error.URLError) as req_error:
        print("Failure fetching data with error: {}".format(req_error))


def get_and_parse_data(script_args):
    try:
        if len(script_args) > 1:
            response = urllib.request.urlopen(script_args[1])
            if response is not None:
                return parse_salary_data(response)
            else:
                return None
        else:
            return default_data_fetch()
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as req_error:
        print("Defaulting URL due to error with value provided: {} ".format(req_error))
        return default_data_fetch()


def parse_salary_data(html_data):
    # using BeautifulSoup here which I decided to use after reviewing in StackOverflow for suggestions on html parsers
    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/ and https://stackoverflow.com/questions/11709079/parsing-html-using-python
    salaries_table = bs4.BeautifulSoup(html_data.read(), "html.parser").find(
        "table", {"id": EXPECTED_TABLE_NAME}
    )
    if salaries_table is not None:
        salary_records = salaries_table.find_all("tr")
        if salary_records is not None:
            parsed_salaries_list = []
            bad_records_list = []
            for record in salary_records:
                process_data(parsed_salaries_list, bad_records_list, record)
                
            write_bad_records_to_file(bad_records_list)
            write_dataset_info(salary_records, parsed_salaries_list)
            return parsed_salaries_list
    print("No data with expected format found to parse")
    return None

def process_data(parsed_salaries, bad_records, record):
    player_salary = extract_table_column_value(
                    record, EXPECTED_TABLE_COLUMN_PLAYER_SALARY
                )
    player_level = extract_table_column_value(
                    record, EXPECTED_TABLE_COLUMN_PLAYER_LEVEL
                )
    year_of_salary_record = extract_table_column_value(
                    record, EXPECTED_TABLE_COLUMN_PLAYER_YEAR
                )

    if (
        player_salary is not None
                    and is_player_level_mlb(player_level)
                    and is_right_year_of_salary(year_of_salary_record)
    ):
        player_salary = player_salary.replace("$", "")
        player_salary = player_salary.replace(",", "")
        if player_salary.isnumeric():
            parsed_salaries.append(int(player_salary))
        else:
            bad_records.append(create_bad_record(record))
    else:
        bad_records.append(create_bad_record(record))


def sort_and_calculate_offer_value(salaries):
    # using numpy for sorting array
    #https://numpy.org/doc/stable/reference/generated/numpy.sort.html
    sorted_salaries = -np.sort(-np.array(salaries))
    return statistics.mean(sorted_salaries[:125])


def create_bad_record(bad_record):
    return {
        "playerName": extract_table_column_value(
            bad_record, EXPECTED_TABLE_COLUMN_PLAYER_NAME
        ),
        "salary": extract_table_column_value(
            bad_record, EXPECTED_TABLE_COLUMN_PLAYER_SALARY
        ),
        "level": extract_table_column_value(
            bad_record, EXPECTED_TABLE_COLUMN_PLAYER_LEVEL
        ),
        "year": extract_table_column_value(
            bad_record, EXPECTED_TABLE_COLUMN_PLAYER_YEAR
        ),
    }


def write_dataset_info(salary_records, parsed_salaries):
    if salary_records is not None and parsed_salaries is not None:
        filename = "data-set-info-" + str(datetime.now()).replace(" ", "-") + ".txt"
        dataset_info = (
            "Number of records in original dataset: "
            + str(len(salary_records))
            + "\n"
            + "Number of valid salary records in dataset: "
            + str(len(parsed_salaries))
            + "\n"
            + "Number of records lost to formatting errors: "
            + str(len(salary_records) - len(parsed_salaries))
            + "\n"
        )

        dataset_info_table = PrettyTable(["Dataset Info", "Value"])
        dataset_info_table.add_row(
            ["Number of records in original dataset", str(len(salary_records))]
        )
        dataset_info_table.add_row(
            ["Number of valid salary records in dataset", str(len(parsed_salaries))]
        )
        dataset_info_table.add_row(
            [
                "Number of records lost to formatting errors",
                str(len(salary_records) - len(parsed_salaries)),
            ]
        )
        print(dataset_info_table)
        file = open(filename, "a")
        file.write(dataset_info)
        file.close()


def write_bad_records_to_file(bad_records):
    if bad_records is not None:
        filename = "bad-data-" + str(datetime.now()).replace(" ", "-") + ".json"
        file = open(filename, "a")
        file.write(json.dumps(bad_records) + "\n")
        file.close()


def is_player_level_mlb(player_level):
    return player_level is not None and player_level.casefold() == "MLB".casefold()


def is_right_year_of_salary(year_of_salary_record):
    return year_of_salary_record is not None and year_of_salary_record == "2016"


def extract_table_column_value(data_record, column_name):
    try:
        return data_record.select_one(column_name).text
    except AttributeError:
        return None


# cleaning CLI arguments from whitespace
def clean_cli_arguments():
    for i in range(len(sys.argv)):
        sys.argv[i].replace(" ", "")


####
clean_cli_arguments()

if len(sys.argv) <= MAX_NUM_OF_CLI_ARGS:
    salaries = get_and_parse_data(sys.argv)
    if salaries is not None:
        table = PrettyTable(["Upcoming Qualifiying Offer Value"])
        table.add_row(["${:,}".format(sort_and_calculate_offer_value(salaries))])
        print(table)

else:
    print("Program only accepts one user provided argument")

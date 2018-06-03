import os
import pathlib
from collections import OrderedDict, deque
from pprint import pprint

import pandas as pd

# Utility constants
file_suffix = ['short', 'full']
float_precision = 3

# dictionaries to convert dict names to xl naming conventions
schemas = [
    {  # short
        'B3F_id': 'B3F ID',
        'name': 'Name',
        'type': 'Type',
        'desc': 'Description',
        'loc': 'Location Path',
        'cls': 'Classe di Resistenza CLS',
        'status': 'Status',
        'n_issues': '# Issues',
        'n_open_issues': '# Open Issues',
        'n_checklists': '# Checklists',
        'n_open_checklists': '# Open Checklists',
        'date_created': 'Date Created',
        'contractor': 'Appaltatore',
        'completion_percentage': 'Percentuale di Completamento',
        'pillar_number': 'n° pilasto',
        'superficial_quality': 'Qualità superficiale getto',
        'phase': 'Fase',
        'temperature': 'Temperatura getto',
        'moisture': 'Umidità getto',
        'pressure': 'Pressione getto',
        'record_timestamp': 'Record_TS',
        'BIM_id': 'BIM Object ID'
    }, {  # full
        'BIM_id': 'BIM Object ID',
        'temperature': 'Temperatura getto',
        'moisture': 'Umidità getto',
        'pressure': 'Pressione getto',
        'phase': 'Fase',
        'begin_timestamp': 'Begin_TS',
        'end_timestamp': 'End_TS'
    }]


def list_avg(data):
    """Evaluates the average of the list"""
    return float(sum(data)) / len(data)


def extract_data(log, file_detail):
    """Extracts summarized info from a batch of data"""
    summarized_log = OrderedDict()

    BIM_id = log[-1]['BIM_id']

    avg_temperature = list_avg([l['temperature'] for l in log])
    avg_moisture = list_avg([l['moisture'] for l in log])
    avg_pressure = list_avg([l['pressure'] for l in log])

    summarized_log['BIM_id'] = BIM_id
    summarized_log['temperature'] = round(avg_temperature, float_precision)
    summarized_log['moisture'] = round(avg_moisture, float_precision)
    summarized_log['pressure'] = round(avg_pressure, float_precision)

    if file_detail == file_suffix[0]:  # short
        phase = log[-1]['phase']
        timestamp = log[-1]['timestamp']

        summarized_log['phase'] = phase
        summarized_log['timestamp'] = timestamp

    elif file_detail == file_suffix[1]:  # full
        begin_ts = log[0]['begin_timestamp']
        end_ts = log[-1]['end_timestamp']

        summarized_log['begin_timestamp'] = begin_ts
        summarized_log['end_timestamp'] = end_ts
    return summarized_log


def convert_dict_keys(old_dict, conversion_table):
    """Converts a dictionary to an equal dictionary,
    changing the keys according to the given conversion table"""
    converted_dict = OrderedDict()

    for key, value in old_dict.items():
        try:
            converted_key = conversion_table[key]
            converted_dict[converted_key] = value
        except KeyError:
            # if the key is not contained in the conversion table, drop that element
            continue
    return converted_dict


def read_data_from_spreadsheet(file_name):
    """Reads data from the given spreadsheet"""
    sheet_path = pathlib.Path.cwd().parent.joinpath('res', file_name)

    # loads data in a dataframe with the structure "moisture", "pressure", "temperature"
    xl_df = pd.read_excel(open(os.fspath(sheet_path), 'rb'), sheet_name='Sheet1')
    xl_df = xl_df.to_dict()
    data = {
        'Moisture': [],
        'Pressure': [],
        'Temperature': []
    }

    for param, values in xl_df.items():
        deque_values = deque(list(values.values()))
        deque_values.reverse()
        data[param] = deque_values
    return data


def append_summary(log, file_detail):
    """Generates and writes the summarized line on the full log file"""
    # Setting the right path to the spreadsheet
    sheet_path = pathlib.Path.cwd().parent.parent.joinpath('res', 'report-' + file_detail + '-test.xlsx')
    # print("Updating file at: " + os.fspath(sheet_path))

    # Loading previous Excel data into dataframe
    xl_df = pd.read_excel(open(os.fspath(sheet_path), 'rb'), sheet_name='Sheet1')

    # data pre-processing, summarize the list of dicts in a single dict
    summarized_log = extract_data(log, file_detail)
    log_list = []

    # Key conversion of the dictionary in order to match with the schema on the destination file
    schema_index = file_suffix.index(file_detail)
    converted_log = convert_dict_keys(summarized_log, conversion_table=schemas[schema_index])
    log_list.append(converted_log)

    # Update previous dataframe with the new row
    new_row = pd.DataFrame.from_dict(log_list)
    new_df = pd.concat([xl_df, new_row], ignore_index=True)

    # Avoid sorting columns when concatenating dataframes
    new_df = new_df.reindex_axis(xl_df.columns, axis=1)
    # pprint(new_df)

    # Write update dataframe to Excel spreadsheet
    writer = pd.ExcelWriter(os.fspath(sheet_path))
    new_df.to_excel(writer, 'Sheet1', index=False)
    writer.save()

    # leave for debug purpose
    df_check = pd.read_excel(open(os.fspath(sheet_path), 'rb'), sheet_name='Sheet1')
    pprint(df_check)


if __name__ == '__main__':
    pprint(read_data_from_spreadsheet(file_name='test_input1.xlsx'))

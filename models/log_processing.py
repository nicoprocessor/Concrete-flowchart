from collections import OrderedDict

# Utility constants
file_suffix = ['short', 'full']
float_precision = 3

# dictionaries to convert dict names to Excel naming conventions
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
        'phase': 'Phase',
        'temperature': 'Flow Temperature',
        'moisture': 'Flow Moisture',
        'pressure': 'Flow Pressure',
        'record_timestamp': 'Timestamp',
        'BIM_id': 'BIM Object ID'
    }, {  # full
        'BIM_id': 'BIM Object ID',
        'temperature': 'Flow Temperature',
        'moisture': 'Flow Moisture',
        'pressure': 'Flow Pressure',
        'phase': 'Phase',
        'status': 'Status',
        'begin_timestamp': 'Begin Timestamp',
        'end_timestamp': 'End Timestamp'
    }]


def list_avg(data):
    """Evaluates the average of the list
    :rtype: float
    """
    return float(sum(data)) / len(data)


def extract_average_from_batch(log, file_detail):
    """Extracts summarized info from a batch of data
    :rtype: dict
    """
    summarized_log = {
        'BIM_id': log[-1]['BIM_id'],
        'phase': log[-1]['phase'],
        'status': log[-1]['status']
    }

    if file_detail == file_suffix[0]:  # shorts
        summarized_log['B3F_id'] = log[-1]['B3F_id'],
        summarized_log['name'] = log[-1]['name'],
        summarized_log['type'] = log[-1]['type'],
        summarized_log['desc'] = log[-1]['desc'],
        summarized_log['loc'] = log[-1]['loc'],
        summarized_log['cls'] = log[-1]['cls'],
        summarized_log['status'] = log[-1]['status'],
        summarized_log['n_issues'] = log[-1]['n_issues'],
        summarized_log['n_open_issues'] = log[-1]['n_open_issues'],
        summarized_log['n_checklists'] = log[-1]['n_checklists'],
        summarized_log['n_open_checklists'] = log[-1]['n_open_checklists'],
        summarized_log['date_created'] = log[-1]['date_created'],
        summarized_log['contractor'] = log[-1]['contractor'],
        summarized_log['completion_percentage'] = log[-1]['completion_percentage'],
        summarized_log['pillar_number'] = log[-1]['pillar_number'],
        summarized_log['superficial_quality'] = log[-1]['superficial_quality'],
        summarized_log['record_timestamp'] = log[-1]['record_timestamp']
        summarized_log['temperature'] = log[-1]['temperature']
        summarized_log['moisture'] = log[-1]['moisture']
        summarized_log['pressure'] = log[-1]['pressure']

    elif file_detail == file_suffix[1]:  # full
        # eval averages
        summarized_log['temperature'] = round(list_avg([l['temperature'] for l in log]), float_precision)
        summarized_log['moisture'] = round(list_avg([l['moisture'] for l in log]), float_precision)
        summarized_log['pressure'] = round(list_avg([l['pressure'] for l in log]), float_precision)
        summarized_log['begin_timestamp'] = log[0]['begin_timestamp']
        summarized_log['end_timestamp'] = log[-1]['end_timestamp']

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

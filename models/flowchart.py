import datetime
import time

import data_converter
from rpi_conf import RPiConfigs

file_suffix = ['short', 'full', 'test']

log_full = []  # report completo, ad alta frequenza di campionamento
log_short = []  # report sintetico

short_schema_keys = ['B3F_id', 'name', 'type', 'desc', 'loc', 'cls', 'status', 'n_issues', 'n_open_issues',
                     'n_checklists', 'n_open_checklists', 'date_created', 'contractor', 'completion_percentage',
                     'pillar_number', 'superficial_quality', 'phase', 'temperature', 'moisture', 'pressure',
                     'record_timestamp', 'BIM_id']

urgency_labels = ['safe', 'warning']
process_params = ['moisture', 'temperature', 'pressure']

# wait for user to grant the access to the new phase or get there automatically
wait_for_input = True

# tolerance on expected values (safe)
moisture_safe_tolerance = 2
temperature_safe_tolerance = 2
pressure_safe_tolerance = 2

# tolerance on expected values (warning)
moisture_warning_tolerance = 10
temperature_warning_tolerance = 10
pressure_warning_tolerance = 10

# durata delay tra letture successive (in secondi)
casting_read_delay = 10
maturation_read_delay = 10

# delay tra due salvataggi successivi (in secondi)
full_report_sampling_rate = 60
short_report_sampling_rate = 300

# for future implementations
short_report_casting_sampling_rate = 5 * 60  # 5 minutes
short_report_casting_sampling_rate = 24 * 60 * 60  # 1 day

# expected values during casting
expected_moisture_casting = 50
expected_temperature_casting = 28
expected_pressure_casting = 10

# expected values at maturation phase
expected_moisture_maturation = 50
expected_temperature_maturation = 30
expected_pressure_maturation = 10

# RPi setup configuration
rpi = RPiConfigs(green_LED_pin=1, yellow_LED_pin=2, red_LED_pin=3)

params_expected_values = {'moisture':
                              {'casting': expected_moisture_casting,
                               'maturation': expected_moisture_maturation},
                          'temperature':
                              {'casting': expected_temperature_casting,
                               'maturation': expected_temperature_maturation},
                          'pressure':
                              {'casting': expected_pressure_casting,
                               'maturation': expected_pressure_maturation},
                          }

params_tolerances = {'moisture':
                         {'safe': moisture_safe_tolerance,
                          'warning': moisture_warning_tolerance},
                     'temperature':
                         {'safe': temperature_safe_tolerance,
                          'warning': temperature_warning_tolerance},
                     'pressure':
                         {'safe': pressure_safe_tolerance,
                          'warning': pressure_warning_tolerance},
                     }


def check_param_in_range(param_key, param_value, phase, urgency_label):
    """checks if the given parameter with his value is in the range allowed,
    based on the phase of the process and the urgency"""
    return float(param_value) < abs(
        params_expected_values[param_key][phase] - params_tolerances[param_key][urgency_label])


def check_params(current_params, phase, urgency_label):
    """Checks if the current parameters are close enough to the expected value,
     otherwise returns a warning"""
    cumulative_or_check = 0

    for key, value in current_params:
        param_check = check_param_in_range(param_key=key, param_value=value,
                                           phase=phase, urgency_label=urgency_label)
        cumulative_or_check = cumulative_or_check or param_check
    return cumulative_or_check


def sensor_input_params():
    """Queries the RPi sensors in order to update the parameters that have to be monitored"""
    # TODO trovare soluzione per sensore di pressione
    detected_moisture = rpi.read_humidity[1]
    detected_temperature = rpi.read_temperature[1]
    detected_pressure = rpi.read_humidity[1]
    return detected_moisture, detected_temperature, detected_pressure


def user_input_params():
    """Asks the user to enter the parameters manually"""
    input_moisture = float(input("Enter current moisture: "))
    input_temperature = float(input("Enter current temperature: "))
    input_pressure = float(input("Enter current pressure: "))
    return input_moisture, input_temperature, input_pressure


def update_params(use_sensors=True):
    """Updates the current parameters using the chosen channel"""
    if use_sensors:
        return sensor_input_params()
    else:
        return user_input_params()


def init_plant(B3F_id, name, type, desc, loc, cls, status, n_issues, n_open_issues, n_checklists,
               n_open_checklists, date_created, contractor, completion_percentage, pillar_number,
               superficial_quality, BIM_id):
    """Initializes the plant filling fields that will not be changed during the monitoring session"""
    plant = {'B3F_id': B3F_id,
             'name': name,
             'type': type,
             'desc': desc,
             'loc': loc,
             'cls': cls,
             'status': status,
             'n_issues': n_issues,
             'n_open_issues': n_open_issues,
             'n_checklists': n_checklists,
             'n_open_checklists': n_open_checklists,
             'date_created': date_created,
             'contractor': contractor,
             'completion_percentage': completion_percentage,
             'pillar_number': pillar_number,
             'superficial_quality': superficial_quality,
             'BIM_id': BIM_id}
    return plant


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def save_full_report(log_full):
    """Save short report to Excel spreadsheet"""
    print("Saving full report to spreadsheet")
    data_converter.append_summary(log_full, file_detail=file_suffix[1])


def save_short_report(plant_instance, BIM_id, phase, status, record_timestamp, moisture, temperature, pressure):
    """Save short report to Excel spreadsheet"""
    # Merge dictionaries
    short_report_data = {'BIM_id': BIM_id,
                         'phase': phase,
                         'status': status,
                         'record_timestamp': record_timestamp,
                         'moisture': moisture,
                         'temperature': temperature,
                         'pressure': pressure}
    # merged_short_report = {**plant_instance, **short_report_data}
    merged_short_report = merge_two_dicts(plant_instance, short_report_data)

    print("Saving short report to spreadsheet")
    log_short.append(merged_short_report)
    data_converter.append_summary(log_short, file_detail=file_suffix[0])


def monitoring_phase(plant, current_phase, use_sensors=True):
    """Monitoring session under a specific phase"""
    current_params = {
        'moisture': 0.0,
        'temperature': 0.0,
        'pressure': 0.0
    }

    print(
        "Phase: {}\n"
        "Expected moisture at {}: {}\n"
        "Expected temperature at {}: {}\n"
        "Expected pressure at {}: {}\n".format(current_phase, current_phase,
                                               expected_moisture_casting, current_phase,
                                               expected_temperature_casting, current_phase,
                                               expected_pressure_casting))

    # first read
    current_params['moisture'], \
    current_params['temperature'], \
    current_params['pressure'] = update_params(use_sensors)

    start_time_full_report = time.time()
    start_time_short_report = time.time()

    while check_params(current_params, phase=current_phase, urgency_label='safe'):
        print("Parameters at {} are not as expected\n"
              "Moisture: {}\n"
              "Temperature: {}\n"
              "Pressure: {}\n".format(current_phase, current_params['moisture'],
                                      current_params['temperature'], current_params['pressure']))

        # checks if the params are close to the expected value or if the cast has to be stopped
        if check_params(current_params, phase=current_phase, urgency_label='warning'):
            # still good
            rpi.switch_off_all()
            rpi.change_LED_status(action='ON', LED_color='y')
        else:  # stop concrete casting
            rpi.switch_off_all()
            rpi.change_LED_status(action='ON', LED_color='r')
            return False

        # invia dati a operatore -> ferma il getto
        # invia dati a DL
        # invia dati a centrale di betonaggio

        # parameters update
        current_params['moisture'], \
        current_params['temperature'], \
        current_params['pressure'] = update_params(use_sensors)

        # update log-full
        log_full.append({'BIM_id': plant['BIM_id'],
                         'phase': current_phase,
                         'status': 'Bad',
                         'begin_timestamp': start_time_full_report,
                         'end_timestamp': time.time(),
                         'moisture': current_params['moisture'],
                         'temperature': current_params['temperature'],
                         'pressure': current_params['pressure']})

        # evaluate ETA
        end_time = time.time()
        full_report_elapsed_time = end_time - start_time_full_report
        short_report_elapsed_time = end_time - start_time_short_report

        if full_report_elapsed_time > full_report_sampling_rate:
            # save to full report file
            save_full_report(log_full)
            start_time_full_report = 0
            log_full = []

        if short_report_elapsed_time > short_report_sampling_rate:
            # save to short report file
            save_short_report(plant_instance, BIM_id=plant_instance['BIM_id'],
                              phase=current_phase, status='Bad', record_timestamp=datetime.datetime.now(),
                              moisture=current_params['moisture'], temperature=current_params['temperature'],
                              pressure=current_params['pressure'])
            start_time_short_report = 0
            log_short = []

        # monitoring delay
        if current_phase == 'casting':
            time.sleep(casting_read_delay)
        else:
            time.sleep(maturation_read_delay)
    return True


def monitoring_session(plant, use_sensors=True):
    current_params = {
        'moisture': 0.0,
        'temperature': 0.0,
        'pressure': 0.0
    }

    start_time = time.time()
    phases = ['casting', 'maturation']

    for current_phase in phases:
        # monitoring
        result = monitoring_phase(plant, current_phase, use_sensors)

        # if something went wrong, stop the entire monitoring system
        if not result:
            return False

        # update data with the change of status
        if current_phase == 'casting':
            # casting parameters levels as expected
            print("Parameters at casting are as expected. Moving to concrete maturation phase.")
            if wait_for_input:
                input("Press any key to proceed to the next phase")
        else:  # maturation - last phase
            # maturation level required reached
            print("Level of maturation required is satisfied. You can now remove the formwork.")

        # parameters update
        current_params['moisture'], \
        current_params['temperature'], \
        current_params['pressure'] = update_params(use_sensors)

        log_full = []
        log_full.append({'BIM_id': plant['BIM_id'],
                         'phase': current_phase,
                         'status': 'OK',
                         'begin_timestamp': start_time,
                         'end_timestamp': datetime.datetime.now(),
                         'moisture': current_params['moisture'],
                         'temperature': current_params['temperature'],
                         'pressure': current_params['pressure']})

        save_full_report(log_full)
        save_short_report(plant, BIM_id=plant['BIM_id'],
                          phase=current_phase, status='OK', record_timestamp=datetime.datetime.now(),
                          moisture=current_params['moisture'], temperature=current_params['temperature'],
                          pressure=current_params['pressure'])
        # Reset logs
        log_short = []
        log_full = []


if __name__ == '__main__':
    # Init the monitoring system
    # Order of the parameters is not important since they are filled using params name.
    # Just pay attention if there's any parameter missing.
    plant_instance = init_plant(B3F_id='3d0f5ea4-1394-46d0-b0b1-ba0ea9af8379',
                                name='Pilastro in calcestruzzo - Rettangolare',
                                type='Pilastro',
                                desc='nan',
                                loc='via Merezzate, Milano>E10>P1',
                                cls='C25/30',
                                status='Ordered',
                                n_issues='0',
                                n_open_issues='0',
                                n_checklists='1',
                                n_open_checklists='1',
                                date_created='Timestamp(\'2018-04-21 05:24:39\')',
                                contractor='Appaltatore 1',
                                completion_percentage='50',
                                pillar_number='112',
                                superficial_quality='Bassa',
                                BIM_id='40e526d7-263a-4f74-b935-1359b190b926')
    result = monitoring_session(plant=plant_instance, use_sensors=True)
    print(result)

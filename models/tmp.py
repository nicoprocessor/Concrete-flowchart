import datetime

from log_processing import extract_average_from_batch
from server_connection import send_log_to_server

file_suffix = ['short', 'full', 'test']
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

# delay between two saving operations (in iterations)
short_report_iterations_delay = 10
full_report_iterations_delay = 5

# delay between two queries (in seconds)
casting_read_delay = 5
maturation_read_delay = 5

# delay between two queries (in seconds)
full_report_sampling_rate = 30  # 30 seconds
short_report_sampling_rate = 180  # 3 minutes

# for future implementations
short_report_casting_sampling_rate = 5 * 60  # 5 minutes
# short_report_casting_sampling_rate = 24 * 60 * 60  # 1 day

# expected values during casting
expected_moisture_casting = 20
expected_temperature_casting = 28
expected_pressure_casting = 20

# expected values at maturation phase
expected_moisture_maturation = 20
expected_temperature_maturation = 40
expected_pressure_maturation = 20

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
    """Checks if the given parameter with his value is in the range allowed,
    based on the phase of the process and the urgency"""
    return True if ((float(param_value) < params_expected_values[param_key][phase] +
                     params_tolerances[param_key][urgency_label])
                    and (float(param_value) > params_expected_values[param_key][phase] -
                         params_tolerances[param_key][urgency_label])) \
        else False


def check_params(current_params, phase, urgency_label):
    """Checks if the current parameters are close enough to the expected value,
     otherwise returns a warning"""
    for key, value in current_params.items():
        param_check = check_param_in_range(param_key=key, param_value=value,
                                           phase=phase, urgency_label=urgency_label)
        if not param_check:
            return False
    return True


def user_input_params():
    """Asks the user to enter the parameters manually"""
    input_moisture = float(input("Enter current moisture: "))
    input_temperature = float(input("Enter current temperature: "))
    input_pressure = float(input("Enter current pressure: "))
    return input_moisture, input_temperature, input_pressure


def update_params():
    return user_input_params()


def status_light_output(color):
    print("Turning ON LED: " + color)


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def save_full_report(log_full):
    print("Saving full report to spreadsheet")
    summarized_log = extract_average_from_batch(log=log_full, file_detail=file_suffix[1])
    send_log_to_server(payload=summarized_log, file_detail=file_suffix[1])
    print("Saved!")


def save_short_report(plant, bim_id, phase, status, record_timestamp,
                      moisture, temperature, pressure):
    """Save short report to Excel spreadsheet"""
    # Merge dictionaries
    short_report_data = {'BIM_id': bim_id,
                         'phase': phase,
                         'status': status,
                         'record_timestamp': record_timestamp,
                         'moisture': moisture,
                         'temperature': temperature,
                         'pressure': pressure}
    merged_short_report = merge_two_dicts(plant, short_report_data)

    print("Saving short report to spreadsheet")
    short_report = extract_average_from_batch([merged_short_report], file_detail=file_suffix[0]);
    send_log_to_server(payload=short_report, file_detail=file_suffix[0])
    print("Saved!")


def monitoring_phase(plant, current_phase):
    """Monitoring session under a specific phase"""
    log_full = []

    current_params = {
        'moisture': 0.0,
        'temperature': 0.0,
        'pressure': 0.0
    }

    if current_phase == 'casting':  # casting phase
        print(
            "Phase: {}\n"
            "Expected moisture at {}: {}\n"
            "Expected temperature at {}: {}\n"
            "Expected pressure at {}: {}\n"
            "Params safe margin: {}\n"
            "Exit condition: {}\n".format(current_phase.capitalize(),
                                          current_phase.capitalize(),
                                          expected_moisture_casting,
                                          current_phase.capitalize(),
                                          expected_temperature_casting,
                                          current_phase.capitalize(),
                                          expected_pressure_casting,
                                          moisture_safe_tolerance,
                                          moisture_warning_tolerance))
    else:  # maturations phase
        print(
            "Phase: {}\n"
            "Expected moisture at {}: {}\n"
            "Expected temperature at {}: {}\n"
            "Expected pressure at {}: {}\n"
            "Params safe margin: {}\n"
            "Exit condition: {}\n".format(current_phase.capitalize(),
                                          current_phase.capitalize(),
                                          expected_moisture_maturation,
                                          current_phase.capitalize(),
                                          expected_temperature_maturation,
                                          current_phase.capitalize(),
                                          expected_pressure_maturation,
                                          moisture_safe_tolerance,
                                          moisture_warning_tolerance))

    # first read
    current_params['moisture'], \
    current_params['temperature'], \
    current_params['pressure'] = update_params()

    # start timers
    iterations_full_report = 0
    iterations_short_report = 0

    # uncomment if using sensors
    start_time_full_report = datetime.datetime.now()
    start_time_short_report = datetime.datetime.now()

    while not check_params(current_params, phase=current_phase, urgency_label='safe'):
        print("Parameters at {} are not as expected\n".format(current_phase.capitalize()))

        # checks if the params are close to the expected value or if the cast has to be stopped
        if check_params(current_params, phase=current_phase, urgency_label='warning'):
            # still good
            print("Parameters are still under control")
            status_light_output('Y')
            iterations_full_report += 1
            iterations_short_report += 1

        else:  # stop the entire program
            print("Something went wrong during the {} phase!".format(current_phase))
            status_light_output('R')
            return False

        # parameters update
        current_params['moisture'], \
        current_params['temperature'], \
        current_params['pressure'] = update_params()

        # update log-full
        log_full.append({'BIM_id': plant['BIM_id'],
                         'phase': current_phase.capitalize(),
                         'status': current_phase.capitalize() + ': Bad',
                         'begin_timestamp': start_time_full_report,
                         'end_timestamp': datetime.datetime.now(),
                         'moisture': current_params['moisture'],
                         'temperature': current_params['temperature'],
                         'pressure': current_params['pressure']})

        # evaluate ETA
        end_time = datetime.datetime.now()

        # datetime.timedelta(minutes, seconds, microseconds)
        # full_report_elapsed_time = end_time - start_time_full_report
        # short_report_elapsed_time = end_time - start_time_short_report

        if iterations_full_report == full_report_iterations_delay:
            # save to full report file
            save_full_report(log_full)

            # reset timers
            start_time_full_report = datetime.datetime.now()
            iterations_full_report = 0
            log_full = []

        if iterations_short_report == short_report_iterations_delay:
            # save to short report file
            save_short_report(plant,
                              bim_id=plant['BIM_id'],
                              phase=current_phase.capitalize(),
                              status=current_phase.capitalize() + ': Bad',
                              record_timestamp=datetime.datetime.now(),
                              moisture=current_params['moisture'],
                              temperature=current_params['temperature'],
                              pressure=current_params['pressure'])

            # reset timers
            start_time_short_report = datetime.datetime.now()
            iterations_short_report = 0

        # uncomment this if using sensors
        # if full_report_elapsed_time.seconds > full_report_sampling_rate:
        #     # save to full report file
        #     save_full_report(log_full)
        #
        #     # reset timer and clear log
        #     start_time_full_report = 0
        #     log_full = []

        # if short_report_elapsed_time.seconds > short_report_sampling_rate:
        #     # save to short report file
        #     save_short_report(plant, bim_id=plant['BIM_id'],
        #                       phase=current_phase.capitalize(),
        #                       status=current_phase.capitalize() + ': Bad',
        #                       record_timestamp=datetime.datetime.now(),
        #                       moisture=current_params['moisture'],
        #                       temperature=current_params['temperature'],
        #                       pressure=current_params['pressure'])
        #     # reset timer and clear log
        #     start_time_short_report = 0

        # monitoring delay
        # if current_phase == 'casting':
        #     time.sleep(casting_read_delay)
        # else:
        #     time.sleep(maturation_read_delay)
    return True


def monitoring_session(plant):
    """Monitors the phase of the work, sends feedback and returns True when the work is done"""
    current_params = {
        'moisture': 0.0,
        'temperature': 0.0,
        'pressure': 0.0
    }

    start_time = datetime.datetime.now()
    phases = ['casting', 'maturation']

    for current_phase in phases:
        # monitoring
        result = monitoring_phase(plant, current_phase)

        # if something went wrong, stop the entire monitoring system
        if not result:
            return False
        else:  # status: OK
            # update data with the change of status
            if current_phase == 'casting':
                # casting parameters levels as expected
                print("Parameters at casting are as expected. Moving to concrete maturation phase.")

                # green light
                status_light_output('G')

                if wait_for_input:
                    input("Press any key to proceed to the next phase")
            else:  # maturation - last phase
                # maturation level required reached
                print("Level of maturation required is satisfied. You can now remove the formwork.")

                # green light
                status_light_output('G')

                # parameters update
                current_params['moisture'],\
                current_params['temperature'], \
                current_params['pressure'] = update_params()

                # now the phase status will be OK since we moved to the next phase (parameters are as expected)
                phase_change_record = {'BIM_id': plant['BIM_id'],
                                       'phase': current_phase.capitalize(),
                                       'status': current_phase.capitalize() + ': OK',
                                       'begin_timestamp': start_time,
                                       'end_timestamp': datetime.datetime.now(),
                                       'moisture': current_params['moisture'],
                                       'temperature': current_params['temperature'],
                                       'pressure': current_params['pressure']}

                # save to Excel spreadsheet before passing to the next phase
                save_full_report([phase_change_record])
                save_short_report(plant,
                                  bim_id=plant['BIM_id'],
                                  phase=current_phase.capitalize(),
                                  status=current_phase.capitalize() + ': OK',
                                  record_timestamp=datetime.datetime.now(),
                                  moisture=current_params['moisture'],
                                  temperature=current_params['temperature'],
                                  pressure=current_params['pressure'])

                return True

        # parameters update
        current_params['moisture'], current_params['temperature'], current_params['pressure'] = update_params()

        # now the phase status will be OK since we moved to the next phase (parameters are as expected)
        phase_change_record = {'BIM_id': plant['BIM_id'],
                               'phase': current_phase.capitalize(),
                               'status': current_phase.capitalize() + ': OK',
                               'begin_timestamp': start_time,
                               'end_timestamp': datetime.datetime.now(),
                               'moisture': current_params['moisture'],
                               'temperature': current_params['temperature'],
                               'pressure': current_params['pressure']}

        # save to Excel spreadsheet before passing to the next phase
        save_full_report([phase_change_record])
        save_short_report(plant,
                          bim_id=plant['BIM_id'],
                          phase=current_phase.capitalize(),
                          status=current_phase.capitalize() + ': OK',
                          record_timestamp=datetime.datetime.now(),
                          moisture=current_params['moisture'],
                          temperature=current_params['temperature'],
                          pressure=current_params['pressure'])


def init_plant(b3f_id, name, type, desc, loc, cls, status, n_issues, n_open_issues, n_checklists,
               n_open_checklists, date_created, contractor, completion_percentage, pillar_number,
               superficial_quality, bim_id):
    """Initializes the plant filling fields that will not be changed during the monitoring session"""
    plant = {'B3F_id': b3f_id,
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
             'BIM_id': bim_id}
    return plant


if __name__ == '__main__':
    # Init the monitoring system
    # Just pay attention if there's any parameter missing.
    # All these parameters will be moved in the app section, when you want to start monitoring a new project
    # Since they are all static and they don't change during time
    bim_id = str(input("Please enter the BIM id for your project: "))

    plant_instance = init_plant(b3f_id='3d0f5ea4-1394-46d0-b0b1-ba0ea9af8379',
                                name='Pilastro in calcestruzzo - Rettangolare',
                                type='Pilastro',
                                desc='n\\a',
                                loc='via Merezzate, Milano>E10>P1',
                                cls='C25/30',
                                status='Ordered',
                                n_issues='0',
                                n_open_issues='0',
                                n_checklists='1',
                                n_open_checklists='1',
                                date_created='2018-04-21 05:24:39',
                                contractor='Appaltatore 1',
                                completion_percentage='50',
                                pillar_number='112',
                                superficial_quality='Bassa',
                                bim_id=bim_id)

    result = monitoring_session(plant=plant_instance)
    # print(result)

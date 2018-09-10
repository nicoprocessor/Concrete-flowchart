import requests

heroku_root_url = 'https://concrete-flowchart.herokuapp.com/'
localhost_root_url = 'http://127.0.0.1:4999/'
file_suffix = ['short', 'full']


def send_log_to_server(payload, file_detail):
    if file_detail == file_suffix[0]:  # short
        url = heroku_root_url + 'short_summary'
    else:  # full
        url = heroku_root_url + 'full_summary'

    # print("Request type: " + file_detail)
    # print("Payload type: " + str(type(payload)))

    r = requests.get(url=url, params=payload)
    print("Sending request to: " + r.url)

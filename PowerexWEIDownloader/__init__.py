import logging
import calendar
import re
import datetime
import requests

import azure.functions as func

def main(mytimer: func.TimerRequest, outputBlob: func.Out[str]) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)

    get_session_cookie_uri = (
        "https://noms.wei-pipeline.com/reports/ci_report/launch.php?menuitem=200"
    )
    post_request_uri = "https://noms.wei-pipeline.com/reports/ci_report/server/request.php"
    get_data_uri = (
        "https://noms.wei-pipeline.com/reports/ci_report/server/streamReport.php?jrId="
    )
    start_date_value = datetime.datetime.today().replace(day=1).strftime("%d-%b-%Y")
    end_date_value = (
        datetime.datetime.today()
        .replace(day=calendar.monthrange(datetime.datetime.today().year, datetime.datetime.today().month)[1])
        .strftime("%d-%b-%Y")
    )
    with requests.Session() as session:

        session.get(get_session_cookie_uri)

        payload = {
            "ReportProc": "SCHPR050",
            "p_ci_id": "200",
            "p_opun": "PL",
            "p_gas_day_from": start_date_value,
            "p_gas_day_to": end_date_value,
            "P_ZONE": "-1",
            "p_gas_cycle_st": "SYNQ",
            "p_output_option": "CSV",
        }

        response = session.post(post_request_uri, data=payload)

        jr_id = re.search("jr_[0-9]*", response.text).group(0)

        get_jr_id_data_uri = get_data_uri + jr_id

        response = session.get(get_jr_id_data_uri)

        outputBlob.set(str(response.text))

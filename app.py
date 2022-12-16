from flask import Flask, redirect, request, make_response, render_template

from src.strava.client import create_strava_client
from src.strava.helpers import download_all_activities
from src.summits.visited import calculate_summit_history
from src.visualisation.map import plot_activities
from src.visualisation.bar_chart import compute_compleation_report
from src.summits.summits import PersistentLocalFileSummitReference
import time

import uuid

app = Flask(__name__)

client = create_strava_client()

database = {}


@app.route("/")
def summit_map():
    authentication_requested = request.args.get('authorise') == 'true'
    authorisation_code = request.args.get('code')
    one_time_token = request.cookies.get('ott')
    # If a token has been provided, resolve athlete ID and invalidate the token.
    athlete_id = database.pop(one_time_token, None)

    if athlete_id is not None:
        print(f'Generating map for athlete {athlete_id}')
        # If an athlete ID has been resolved, the user has authenticated. Generate the map.
        summit_report_page = generate_summit_report(athlete_id)
        response = make_response(summit_report_page)
        response.set_cookie('ott', '', expires=0)  # Prompt users browser to delete the token
        return response

    if not authentication_requested and authorisation_code is None:
        # This is the first visit to the page, present a login button
        return render_template('login.html', login=True)

    if authentication_requested:
        # Login requested, redirect to strava for authentication. Strava will redirect to this page
        # and supply an authorisation code.
        return redirect(client.authorisation.generate_authorisation_url(redirect_uri='http://127.0.0.1:5000/',
                                                                        scope='read_all,activity:read_all,activity:write'))
    if authorisation_code is not None:
        # Strava has provided an auth code -store it, and store the user ID alongside a one-time-token.
        # Return the token to the user as a cookie, allow the user to request map generation.
        athlete_id = client.authorisation.post_athlete_auth_code(authorisation_code)
        print(f'athlete {athlete_id} authenticated')
        one_time_token = str(uuid.uuid4().int)
        database.update({one_time_token: athlete_id})
        print(database)
        response = make_response(render_template('login.html'))
        response.set_cookie(key='ott', value=one_time_token)
        return response


def generate_summit_report(athlete_id: int):
    start = time.time()
    all_activities = download_all_activities(client=client,
                                             athlete_id=athlete_id)
    athlete_data = client.get_athlete_info(athlete_id)
    athlete_name = f"{athlete_data['firstname']} {athlete_data['lastname']}"
    print(f'Download time: {time.time() - start}')
    summit_reference_datasource = PersistentLocalFileSummitReference('./database.pkl')
    start = time.time()
    dataset = calculate_summit_history(activities=all_activities, reference_source=summit_reference_datasource)
    print(f'Calc time: {time.time() - start}')
    visited_summits = dataset.loc[dataset['latest_visit'].notnull()]
    unvisited_summits = dataset.loc[dataset['latest_visit'].isnull()]

    map = plot_activities(activities=all_activities,
                          visited_summits=visited_summits,
                          unvisited_summits=unvisited_summits)
    report = compute_compleation_report(dataset)
    return render_template('/display.html',
                           athlete=athlete_name,
                           map=map._repr_html_(),
                           report_df=report.iloc[::-1])


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

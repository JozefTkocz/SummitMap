import pandas as pd
from typing import List
from src.strava.helpers import interpolate_polyline

from src.summits.locator import find_visited_summits
from src.utils import CoordinateSet

from src.strava.helpers import Activity, Route
from src.summits.summits import SummitReference


def calculate_summit_history(activities: List[Activity],
                             reference_source: SummitReference):
    visit_col = []
    date_col = []
    activity_id_col = []
    distance_proximity = 100
    sampling_distance_inverse = 2 / distance_proximity

    for activity in activities:
        sample_points = int(activity.distance * sampling_distance_inverse)
        route = interpolate_polyline(activity.route,
                                     interpolation_points=sample_points)

        visited_summits = find_visited_summits(reference_source,
                                               CoordinateSet(latitude=route['lat'],
                                                             longitude=route['lng']),
                                               distance_proximity=distance_proximity)

        visit_col += list(visited_summits['Number'].values)
        date_col += [pd.to_datetime(activity.date)] * len(visited_summits)
        activity_id_col += [activity.id] * len(visited_summits)

    visits = pd.DataFrame({
        'activity': activity_id_col,
        'date': date_col,
        'visited_summits': visit_col
    })

    latest_visit = visits.groupby('visited_summits')['date'].max().dt.date
    latest_visit.name = 'latest_visit'
    summit_dataset = reference_source.load().merge(latest_visit, left_on='Number', right_index=True, how='left')
    return summit_dataset

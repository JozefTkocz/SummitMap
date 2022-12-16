import pandas as pd
from stravaclient import StravaClient
from typing import List, Dict
import numpy as np
from scipy.interpolate import interp1d
import polyline
from dataclasses import dataclass
import datetime as dt


class Route(pd.DataFrame):
    def __init__(self, lat: np.array, lng: np.array):
        super(Route, self).__init__(data={
            'lat': lat,
            'lng': lng
        })

    @property
    def latitude(self):
        return self['lat'].values

    @property
    def longitude(self):
        return self['lng'].values

    @classmethod
    def from_polyline(cls, polyline_str: Dict):
        coords = np.array(polyline.decode(polyline_str)).T
        if len(coords) == 2:
            return Route(lat=coords[0], lng=coords[1])
        else:
            return Route(lat=np.array([]), lng=np.array([]))


@dataclass
class Activity:
    id: int
    date: dt.date
    route: Route
    distance: float
    moving_time: int
    elapsed_time: int

    @classmethod
    def from_json(cls, strava_activity: Dict) -> 'Activity':
        return Activity(id=strava_activity['id'],
                        date=pd.to_datetime(strava_activity['start_date']),
                        route=Route.from_polyline(strava_activity['map']['summary_polyline']),
                        distance=strava_activity['distance'],
                        moving_time=strava_activity['moving_time'],
                        elapsed_time=strava_activity['elapsed_time'])


def download_all_activities(client: StravaClient, athlete_id: int) -> List[Activity]:
    all_activities = []
    page = 1
    end = False

    while not end:
        print(f'requesting page {page}')
        activities = client.list_activities(athlete_id=athlete_id,
                                            page=page,
                                            per_page=200)

        if not len(activities):
            end = True
        else:
            all_activities += activities
            page += 1

    final_activities = []
    for activity in all_activities:
        final_activities.append(Activity.from_json(activity))

    return final_activities


def extract_polyline(strava_activity: Dict) -> pd.DataFrame:
    return pd.DataFrame(polyline.decode(strava_activity['map']['summary_polyline']), columns=['lat', 'lng'])


def interpolate_polyline(route_df: pd.DataFrame, interpolation_points: int) -> pd.DataFrame:
    route_df = route_df.drop_duplicates()
    if len(route_df) < 2:
        return pd.DataFrame(columns=['lat', 'lng'])

    route_df = route_df.drop_duplicates()
    # Define some points:
    points = np.array([route_df['lat'].values,
                       route_df['lng'].values]).T  # a (no_points x no_dim) array

    # Linear length along the line:
    distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
    distance = np.insert(distance, 0, 0) / distance[-1]

    alpha = np.linspace(0, 1, interpolation_points)
    interpolator = interp1d(distance, points, kind='slinear', axis=0)
    interpolated_points = interpolator(alpha)
    return pd.DataFrame(interpolated_points, columns=['lat', 'lng'])

import folium
import pandas as pd
from typing import List

from src.strava.helpers import Activity
from src.visualisation.classification_mappings import summit_visualisation_config as summit_config


class SummitMap:
    def __init__(self):
        self.map = folium.Map(tiles="Stamen Terrain")

    def add_polyine(self, polyline: pd.DataFrame):
        if len(polyline):
            folium.PolyLine(polyline, color="blue", weight=3.5, opacity=.5).add_to(self.map)

    def add_visited_summits(self, summits: pd.DataFrame, color: str):
        for idx, summit in summits.iterrows():
            last_visit = summit['latest_visit']
            height = summit['Metres']
            name = summit['Name']

            folium.CircleMarker(
                radius=7.5,
                location=(summit['Latitude'], summit['Longitude']),
                popup=f'{name} ({height} m)<br>Last visited: {last_visit}',
                color='black',
                opacity=0.5,
                fill_color=color,
                fill=True,
                fill_opacity=1.
            ).add_to(self.map)

    def add_unvisited_summits(self, summits: pd.DataFrame, color: str):
        for idx, summit in summits.iterrows():
            folium.CircleMarker(
                radius=7.5,
                location=(summit['Latitude'], summit['Longitude']),
                popup=f"{summit['Name']} ({summit['Metres']} m)",
                color=color,
                fill_color=color,
                fill_opacity=0.3,
                opacity=0.5
            ).add_to(self.map)


def plot_activities(activities: List[Activity],
                    visited_summits: pd.DataFrame,
                    unvisited_summits: pd.DataFrame):
    map = SummitMap()
    for activity in activities:
        map.add_polyine(activity.route)

    for classification, config in summit_config.items():
        visited_summits_of_classification = visited_summits.loc[visited_summits[classification] == 1]
        map.add_visited_summits(color=config.color,
                                summits=visited_summits_of_classification)

        unvisited_summits_of_classification = unvisited_summits.loc[unvisited_summits[classification] == 1]
        map.add_unvisited_summits(color=config.color,
                                  summits=unvisited_summits_of_classification)

    return map.map


def generate_summit_map():
    pass

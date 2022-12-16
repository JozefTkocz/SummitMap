import numpy as np
import pandas as pd
from typing import Union
from src.summits.summits import SummitReference
from src.utils import CoordinateSet
from typing import Tuple

EARTH_RADIUS = 6371.


def find_visited_summits(summit_reference_data: SummitReference,
                         gpx_trail: CoordinateSet,
                         distance_proximity: float = 20,
                         search_window_width: Union[float, None] = 0.1) -> pd.DataFrame:
    """
    Given a GPX trail, extract from the reference data source all entries corresponding to summits that were visited,
    where a visit is an approach within distance_proximity of the summit location.

    :param summit_reference_data: Reference data source defining the summit information
    :param gpx_trail: CoordinateSet corresponding to a GPX trail
    :param distance_proximity: maximum approach distance in metres required to qualify a visit to a summit
    :param search_window_width: A margin in decimal degrees applied around the extent of the gpx_trail coordinates, used
    to reduce the summit search area. If None, the whole of the reference dataset is searched for visited summits.
    :return: pd.DataFrame loaded from summit reference, corresponding to the visited summits only.
    """

    candidate_summits = trim_search_area(summit_reference_data=summit_reference_data,
                                         gpx_trail=gpx_trail,
                                         search_window_width=search_window_width)
    if not len(candidate_summits):
        return candidate_summits

    candidate_summit_coords = CoordinateSet(longitude=candidate_summits[summit_reference_data.longitude_column],
                                            latitude=candidate_summits[summit_reference_data.latitude_column])

    nearest_hill_distance, nearest_hill_index = nearest_neighbour_search(coordinates=gpx_trail,
                                                                         reference_points=candidate_summit_coords)
    gpx_data = pd.DataFrame({'Latitude': gpx_trail.latitude,
                             'Longitude': gpx_trail.longitude})

    gpx_data['nearest_hill_index'] = nearest_hill_index
    gpx_data['nearest_hill_distance'] = nearest_hill_distance
    gpx_data = gpx_data.loc[gpx_data['nearest_hill_distance'] < distance_proximity]
    return candidate_summits.iloc[gpx_data['nearest_hill_index']].drop_duplicates()


def trim_search_area(summit_reference_data: SummitReference,
                     gpx_trail: CoordinateSet,
                     search_window_width: Union[float, None]) -> pd.DataFrame:
    """
    Reduce the search space by filtering the summit reference dataset to a region of interest only.

    :param gpx_trail: GPX coordinates used to define the region of interest
    :param summit_reference_data: SummitReference datasource to be filtered
    :param search_window_width: value in decimal degrees defining the margin to be applied around the GPX trail to
    filter out summits that could not have been visited. If None, all summits are retained as candidates.
    :return: pd.DataFrame loaded from the summit reference source, filtered to the search area of interest only.
    """
    lat_max, lat_min = np.amax(gpx_trail.latitude), np.amin(gpx_trail.latitude)
    lng_max, lng_min = np.amax(gpx_trail.longitude), np.amin(gpx_trail.longitude)
    lng_window = lng_min - search_window_width, lng_max + search_window_width
    lat_window = lat_min - search_window_width, lat_max + search_window_width
    candidate_summits = summit_reference_data.load(latitude_window=lat_window,
                                                   longitude_window=lng_window)
    return candidate_summits


def haversine_distance(lon1: Union[np.array, float],
                       lat1: Union[np.array, float],
                       lon2: Union[np.array, float],
                       lat2: Union[np.array, float]) -> Union[np.array, float]:
    """
    Calculate the great circle distance between two points on the earth (coordinates specified in radians). See
    here for further details: https://en.wikipedia.org/wiki/Haversine_formula

    :param lon1: longitude coordinate of point 1
    :param lat1: latitude coordinate of point 1
    :param lon2: longitude coordinate of point 2
    :param lat2: latitude coordinate of point 2
    :return: great circle distance between point 1 and point 2 in metres.
    """
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.square(np.sin(0.5 * dlat)) + np.cos(lat1) * np.cos(lat2) * np.square(np.sin(0.5 * dlon))
    c = 2 * np.arcsin(np.sqrt(a))
    return c * EARTH_RADIUS * 1000.


def nearest_neighbour_search(coordinates: CoordinateSet, reference_points: CoordinateSet) -> Tuple[np.array, np.array]:
    """
    For each coordinate in coordinates, find the closest coordinate from reference points.

    :param coordinates: CoordinateSet of input coordinates
    :param reference_points: CoordinateSet defining the search space for nearest neighbours to the coordinates argument
    :return: tuple containing the distances to the nearest neighbours, and the indices of the nearest neighbours
    """
    coords_rad = CoordinateSet(latitude=np.radians(coordinates.latitude),
                               longitude=np.radians(coordinates.longitude))

    refs_rad = CoordinateSet(latitude=np.radians(reference_points.latitude),
                             longitude=np.radians(reference_points.longitude))

    coord_latitude, ref_latitude = np.meshgrid(coords_rad.latitude, refs_rad.latitude, sparse=True)
    coord_longitude, ref_longitude = np.meshgrid(coords_rad.longitude, refs_rad.longitude, sparse=True)

    distance_matrix = haversine_distance(ref_longitude, ref_latitude, coord_longitude, coord_latitude)

    minimum_indices = np.argmin(distance_matrix, axis=0)
    distances = distance_matrix[minimum_indices, range(coordinates.length)]

    return distances, minimum_indices

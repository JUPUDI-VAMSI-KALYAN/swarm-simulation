"""Geographic coordinate system for India and Indian Ocean simulation."""

import math
from typing import Tuple, Optional
from src.core.vector2d import Vector2D


class GeoCoordinate:
    """Represents a geographic coordinate (latitude, longitude)."""

    def __init__(self, latitude: float, longitude: float):
        """
        Initialize geographic coordinate.

        Args:
            latitude: Latitude in degrees (-90 to 90, positive = north)
            longitude: Longitude in degrees (-180 to 180, positive = east)
        """
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"GeoCoordinate(lat={self.latitude:.2f}, lon={self.longitude:.2f})"


class MapProjection:
    """Converts between geographic coordinates and screen coordinates."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        projection: str = "mercator"
    ):
        """
        Initialize map projection.

        Args:
            screen_width: Width of screen in pixels
            screen_height: Height of screen in pixels
            min_lat: Minimum latitude of map region
            max_lat: Maximum latitude of map region
            min_lon: Minimum longitude of map region
            max_lon: Maximum longitude of map region
            projection: Projection type ("mercator", "equirectangular")
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.projection = projection

    def geo_to_screen(self, latitude: float, longitude: float) -> Vector2D:
        """
        Convert geographic coordinates to screen coordinates.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees

        Returns:
            Vector2D screen position
        """
        if self.projection == "mercator":
            lat = self._mercator_lat(latitude)
        else:
            lat = latitude

        x = (longitude - self.min_lon) / (self.max_lon - self.min_lon) * self.screen_width
        y = (max(lat, self.min_lat) - self.min_lat) / (self.max_lat - self.min_lat) * self.screen_height
        y = self.screen_height - y

        return Vector2D(x, y)

    def screen_to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """
        Convert screen coordinates to geographic coordinates.

        Args:
            x: X position on screen
            y: Y position on screen

        Returns:
            Tuple of (latitude, longitude)
        """
        lon = x / self.screen_width * (self.max_lon - self.min_lon) + self.min_lon
        y_norm = self.screen_height - y
        lat = y_norm / self.screen_height * (self.max_lat - self.min_lat) + self.min_lat

        if self.projection == "mercator":
            lat = self._inverse_mercator_lat(lat)

        return lat, lon

    def _mercator_lat(self, lat: float) -> float:
        """Convert latitude to Mercator projection."""
        lat_rad = math.radians(lat)
        return math.log(math.tan(lat_rad / 2 + math.pi / 4)) * 180 / math.pi

    def _inverse_mercator_lat(self, mercator_lat: float) -> float:
        """Convert Mercator projection back to latitude."""
        mercator_rad = mercator_lat * math.pi / 180
        return math.degrees(2 * math.atan(math.exp(mercator_rad)) - math.pi / 2)


class IndiaMap:
    """India map with major cities, states, and strategic locations."""

    CITIES = {
        "delhi": GeoCoordinate(28.6139, 77.2090),
        "mumbai": GeoCoordinate(19.0760, 72.8777),
        "chennai": GeoCoordinate(13.0827, 80.2707),
        "kolkata": GeoCoordinate(22.5726, 88.3639),
        "bangalore": GeoCoordinate(12.9716, 77.5946),
        "hyderabad": GeoCoordinate(17.3850, 78.4867),
        "pune": GeoCoordinate(18.5204, 73.8567),
        "ahmedabad": GeoCoordinate(23.0225, 72.5714),
        "jaipur": GeoCoordinate(26.9124, 75.7873),
        "lucknow": GeoCoordinate(26.8467, 80.9462),
        "guwahati": GeoCoordinate(26.1445, 91.7362),
        "srinagar": GeoCoordinate(34.0837, 74.7973),
        "kochi": GeoCoordinate(9.9312, 76.2673),
        "vizag": GeoCoordinate(17.6868, 83.2185),
        "bhubaneswar": GeoCoordinate(20.2961, 85.8245),
        "chandigarh": GeoCoordinate(30.7333, 76.7794),
    }

    BORDER_POINTS = [
        (37.5, 77.5),
        (37.0, 74.0),
        (35.5, 71.0),
        (34.5, 70.0),
        (34.0, 71.0),
        (33.0, 70.5),
        (32.5, 69.0),
        (31.0, 69.0),
        (29.5, 69.0),
        (28.0, 69.0),
        (27.0, 70.0),
        (26.0, 70.5),
        (25.0, 70.5),
        (24.0, 70.5),
        (23.5, 70.5),
        (23.0, 70.5),
        (22.5, 70.0),
        (22.0, 70.0),
        (21.5, 69.5),
        (21.0, 69.5),
        (20.5, 69.5),
        (20.0, 69.0),
        (19.5, 68.5),
        (19.0, 68.0),
        (18.5, 67.5),
        (18.0, 67.0),
        (17.5, 67.0),
        (16.5, 66.5),
        (16.0, 66.5),
        (15.5, 66.5),
        (15.0, 66.0),
        (14.5, 66.0),
        (14.0, 65.5),
        (13.5, 65.0),
        (13.0, 64.5),
        (12.5, 64.5),
        (12.0, 64.0),
        (11.5, 64.0),
        (11.0, 63.5),
        (10.5, 63.0),
        (10.0, 62.5),
        (9.5, 62.5),
        (9.0, 62.0),
        (8.5, 62.0),
        (8.0, 62.0),
        (7.5, 62.5),
        (7.0, 62.5),
        (6.5, 62.0),
        (6.0, 62.0),
        (6.0, 61.5),
        (6.5, 61.0),
        (7.0, 60.5),
        (7.5, 60.0),
        (8.0, 59.5),
        (8.5, 59.5),
        (9.0, 59.0),
        (9.5, 58.5),
        (10.0, 58.0),
        (10.5, 57.5),
        (11.0, 57.0),
        (11.5, 56.5),
        (12.0, 56.0),
        (13.0, 56.0),
        (14.0, 55.5),
        (15.0, 55.0),
        (16.0, 54.5),
        (17.0, 54.0),
        (18.0, 54.0),
        (19.0, 54.0),
        (20.0, 53.5),
        (21.0, 53.0),
        (22.0, 53.0),
        (23.0, 53.0),
        (24.0, 53.5),
        (25.0, 53.5),
        (26.0, 53.5),
        (27.0, 54.0),
        (28.0, 54.5),
        (29.0, 55.0),
        (30.0, 55.5),
        (31.0, 55.5),
        (32.0, 55.5),
        (33.0, 55.5),
        (34.0, 56.0),
        (35.0, 56.5),
        (36.0, 57.0),
        (37.0, 57.5),
        (37.5, 77.5),
    ]

    STRATEGIC_LOCATIONS = {
        "kashmir": GeoCoordinate(34.5, 74.5),
        "punjab": GeoCoordinate(31.0, 75.0),
        "rajasthan": GeoCoordinate(27.0, 74.0),
        "gujarat": GeoCoordinate(23.0, 72.0),
        "maharashtra": GeoCoordinate(19.5, 77.5),
        "madhya_pradesh": GeoCoordinate(23.5, 80.0),
        "uttar_pradesh": GeoCoordinate(27.0, 81.0),
        "west_bengal": GeoCoordinate(24.0, 88.0),
        "odisha": GeoCoordinate(20.5, 85.0),
        "andhra_pradesh": GeoCoordinate(15.5, 80.0),
        "tamil_nadu": GeoCoordinate(11.0, 78.5),
        "karnataka": GeoCoordinate(14.5, 76.0),
        "kerala": GeoCoordinate(10.5, 76.0),
        "assam": GeoCoordinate(26.5, 92.5),
        "arunachal": GeoCoordinate(28.0, 94.0),
        "nagaland": GeoCoordinate(26.0, 94.5),
        "mizoram": GeoCoordinate(23.5, 92.5),
        "lakshadweep": GeoCoordinate(10.5, 72.5),
        "andaman": GeoCoordinate(12.5, 92.5),
    }


class IndianOceanMap:
    """Indian Ocean map with maritime zones and strategic points."""

    REGION_BOUNDARIES = {
        "arabian_sea": (5.0, 30.0, 45.0, 78.0),
        "bay_of_bengal": (5.0, 23.0, 80.0, 100.0),
        "indian_ocean": (-60.0, 35.0, 20.0, 147.0),
        "laccadive_sea": (8.0, 18.0, 68.0, 78.0),
        "andaman_sea": (6.0, 18.0, 92.0, 102.0),
    }

    STRATEGIC_POINTS = {
        "suez": (31.0, 32.5),
        " Aden": (12.5, 45.0),
        "muscat": (23.5, 58.5),
        "mumbai_port": (18.5, 72.5),
        "kochi_port": (9.5, 76.0),
        "chennai_port": (13.0, 80.5),
        "kolkata_port": (22.0, 88.5),
        "colombo": (6.5, 79.5),
        "male": (4.0, 73.5),
        "d Diego_garcia": (-7.0, 72.0),
        "mahe": (-4.5, 55.5),
        "maldives": (3.0, 73.0),
        "sri_lanka": (7.5, 81.0),
        "jakarta": (-6.0, 106.5),
        "singapore": (1.5, 104.0),
        "malacca": (2.0, 102.0),
        "sumatra": (0.5, 101.0),
    }

    SHIPPING_ROUTES = [
        ["suez", "aden", "muscat", "mumbai_port"],
        ["mumbai_port", "kochi_port", "colombo", "male", "maldives"],
        ["kolkata_port", "chennai_port", "colombo", "singapore"],
        ["singapore", "malacca", "jakarta"],
        ["suez", "mahe", "d Diego_garcia", "maldives"],
    ]


class GeoSimulator:
    """Main geographic simulator that handles India and Indian Ocean maps."""

    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """
        Initialize geographic simulator.

        Args:
            screen_width: Width of simulation screen
            screen_height: Height of simulation screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.india_projection = MapProjection(
            screen_width, screen_height,
            min_lat=6.0, max_lat=38.0,
            min_lon=45.0, max_lon=100.0,
            projection="equirectangular"
        )

        self.indian_ocean_projection = MapProjection(
            screen_width, screen_height,
            min_lat=-60.0, max_lat=35.0,
            min_lon=20.0, max_lon=147.0,
            projection="equirectangular"
        )

    def get_india_map(self) -> MapProjection:
        """Get India map projection."""
        return self.india_projection

    def get_indian_ocean_map(self) -> MapProjection:
        """Get Indian Ocean map projection."""
        return self.indian_ocean_projection

    def get_india_border_points(self) -> list:
        """Get India border points as screen coordinates."""
        return [
            self.india_projection.geo_to_screen(lat, lon)
            for lat, lon in IndiaMap.BORDER_POINTS
        ]

    def get_city_screen_position(self, city_name: str) -> Optional[Vector2D]:
        """Get screen position of a city by name."""
        city = IndiaMap.CITIES.get(city_name.lower())
        if city:
            return self.india_projection.geo_to_screen(city.latitude, city.longitude)
        return None

    def get_ocean_point_screen_position(self, point_name: str) -> Optional[Vector2D]:
        """Get screen position of an ocean point by name."""
        coords = IndianOceanMap.STRATEGIC_POINTS.get(point_name.lower())
        if coords:
            return self.indian_ocean_projection.geo_to_screen(coords[0], coords[1])
        return None

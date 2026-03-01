"""Map renderer for India and Indian Ocean."""

from typing import Optional
import pygame
from src.environment.geo_maps import IndiaMap, IndianOceanMap, GeoSimulator
from src.core.vector2d import Vector2D
from config.settings import COLOR_MAP_LAND, COLOR_MAP_WATER, COLOR_MAP_BORDER


class IndiaMapRenderer:
    """Renders India map with cities and regions."""

    def __init__(self, geo_sim: GeoSimulator):
        """
        Initialize India map renderer.

        Args:
            geo_sim: Geographic simulator instance
        """
        self.geo_sim = geo_sim
        self.india_projection = geo_sim.india_projection
        self.border_points = geo_sim.get_india_border_points()

    def render(self, screen: pygame.Surface) -> None:
        """Render India map on screen."""
        points = [(p.x, p.y) for p in self.border_points]
        
        if len(points) >= 3:
            pygame.draw.polygon(screen, COLOR_MAP_LAND, points)
            pygame.draw.polygon(screen, COLOR_MAP_BORDER, points, 3)

    def render_cities(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Render major cities."""
        for city_name, geo_coord in IndiaMap.CITIES.items():
            pos = self.india_projection.geo_to_screen(
                geo_coord.latitude, geo_coord.longitude
            )
            pygame.draw.circle(screen, (255, 50, 50), (int(pos.x), int(pos.y)), 5)
            
            text = font.render(city_name.upper(), True, (200, 200, 200))
            screen.blit(text, (pos.x + 8, pos.y - 8))

    def render_region_labels(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Render region/state labels."""
        for region, geo_coord in IndiaMap.STRATEGIC_LOCATIONS.items():
            pos = self.india_projection.geo_to_screen(
                geo_coord.latitude, geo_coord.longitude
            )
            text = font.render(region.replace("_", " ").title(), True, (150, 150, 150))
            screen.blit(text, (pos.x - 20, pos.y))


class IndianOceanRenderer:
    """Renders Indian Ocean map with maritime zones."""

    def __init__(self, geo_sim: GeoSimulator):
        """
        Initialize Indian Ocean renderer.

        Args:
            geo_sim: Geographic simulator instance
        """
        self.geo_sim = geo_sim
        self.ocean_projection = geo_sim.indian_ocean_projection

    def render(self, screen: pygame.Surface) -> None:
        """Render Indian Ocean map on screen."""
        screen.fill(COLOR_MAP_WATER)

        for point_name, coords in IndianOceanMap.STRATEGIC_POINTS.items():
            pos = self.ocean_projection.geo_to_screen(coords[0], coords[1])
            pygame.draw.circle(screen, (100, 150, 200), (int(pos.x), int(pos.y)), 4)

        for route in IndianOceanMap.SHIPPING_ROUTES:
            for i in range(len(route) - 1):
                start_coords = IndianOceanMap.STRATEGIC_POINTS[route[i]]
                end_coords = IndianOceanMap.STRATEGIC_POINTS[route[i + 1]]
                
                start_pos = self.ocean_projection.geo_to_screen(
                    start_coords[0], start_coords[1]
                )
                end_pos = self.ocean_projection.geo_to_screen(
                    end_coords[0], end_coords[1]
                )
                
                pygame.draw.line(
                    screen, (80, 120, 180),
                    (int(start_pos.x), int(start_pos.y)),
                    (int(end_pos.x), int(end_pos.y)), 1
                )

    def render_maritime_zones(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Render maritime zone labels."""
        zone_centers = {
            "Arabian Sea": (17.0, 65.0),
            "Bay of Bengal": (14.0, 90.0),
            "Laccadive Sea": (13.0, 73.0),
            "Andaman Sea": (12.0, 97.0),
        }

        for zone_name, (lat, lon) in zone_centers.items():
            pos = self.ocean_projection.geo_to_screen(lat, lon)
            text = font.render(zone_name, True, (100, 130, 170))
            screen.blit(text, (pos.x - 40, pos.y - 10))

    def render_ports(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Render major ports."""
        port_names = [
            "mumbai_port", "kochi_port", "chennai_port", "kolkata_port",
            "colombo", "singapore", "jakarta"
        ]

        for port_name in port_names:
            coords = IndianOceanMap.STRATEGIC_POINTS.get(port_name)
            if coords:
                pos = self.ocean_projection.geo_to_screen(coords[0], coords[1])
                pygame.draw.circle(screen, (255, 150, 0), (int(pos.x), int(pos.y)), 6)
                
                text = font.render(port_name.replace("_", " ").title(), True, (255, 200, 100))
                screen.blit(text, (pos.x + 10, pos.y - 10))


class MapManager:
    """Manages different map types for simulation."""

    MAP_INDIA = "india"
    MAP_INDIAN_OCEAN = "indian_ocean"

    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """
        Initialize map manager.

        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.geo_sim = GeoSimulator(screen_width, screen_height)
        
        self.india_renderer = IndiaMapRenderer(self.geo_sim)
        self.ocean_renderer = IndianOceanRenderer(self.geo_sim)

        self.current_map = self.MAP_INDIA

    def set_map(self, map_name: str) -> None:
        """Set current map."""
        self.current_map = map_name

    def get_current_projection(self):
        """Get current map projection."""
        if self.current_map == self.MAP_INDIA:
            return self.geo_sim.india_projection
        return self.geo_sim.indian_ocean_projection

    def render(self, screen: pygame.Surface) -> None:
        """Render current map."""
        if self.current_map == self.MAP_INDIA:
            self.india_renderer.render(screen)
        else:
            self.ocean_renderer.render(screen)

    def render_overlays(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Render map overlays (cities, ports, etc.)."""
        if self.current_map == self.MAP_INDIA:
            self.india_renderer.render_cities(screen, font)
            self.india_renderer.render_region_labels(screen, font)
        else:
            self.ocean_renderer.render_maritime_zones(screen, font)
            self.ocean_renderer.render_ports(screen, font)

    def geo_to_screen(self, latitude: float, longitude: float) -> Vector2D:
        """Convert geo coordinates to screen position."""
        return self.get_current_projection().geo_to_screen(latitude, longitude)

    def screen_to_geo(self, x: float, y: float) -> tuple:
        """Convert screen position to geo coordinates."""
        return self.get_current_projection().screen_to_geo(x, y)

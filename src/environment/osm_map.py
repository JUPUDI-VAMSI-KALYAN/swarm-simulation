"""Real OpenStreetMap renderer for India and Indian Ocean."""

import os
import tempfile
from typing import Optional
import smopy
import pygame
from src.core.vector2d import Vector2D


class OSMMapRenderer:
    """Loads and renders real OpenStreetMap tiles for India and Indian Ocean."""

    CACHE_DIR = os.path.join(tempfile.gettempdir(), "swarm_sim_maps")
    
    # Map regions (lat_min, lon_min, lat_max, lon_max)
    REGIONS = {
        "india": (6.0, 68.0, 36.0, 98.0),
        "indian_ocean": (-30.0, 30.0, 35.0, 120.0),
        "india_detailed": (6.5, 68.5, 35.5, 97.0),
    }

    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """
        Initialize OSM map renderer.

        Args:
            screen_width: Width of screen in pixels
            screen_height: Height of screen in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.maps = {}
        self.current_map = None
        self.current_region = "india"
        
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def load_map(self, region_name: str, zoom: int = 5) -> Optional[pygame.Surface]:
        """
        Load OSM map for a region.

        Args:
            region_name: Name of region ("india", "indian_ocean")
            zoom: Zoom level (0-19)

        Returns:
            Pygame surface with map image
        """
        if region_name not in self.REGIONS:
            return None
            
        if region_name in self.maps:
            return self.maps[region_name]
        
        print(f"Loading OpenStreetMap for {region_name}... (this may take a moment)")
        
        try:
            bbox = self.REGIONS[region_name]
            map_data = smopy.Map(bbox, z=zoom)
            
            img = map_data.to_pil()
            
            img = img.resize((self.screen_width, self.screen_height), resample=pygame.image.smoothing if hasattr(pygame.image, 'smoothing') else 0)
            
            surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            surface = surface.convert()
            
            self.maps[region_name] = surface
            print(f"Map loaded: {region_name}")
            return surface
            
        except Exception as e:
            print(f"Error loading map: {e}")
            return None

    def set_region(self, region_name: str) -> None:
        """Set current map region."""
        self.current_region = region_name
        if region_name not in self.maps:
            self.load_map(region_name)
        self.current_map = self.maps.get(region_name)

    def get_surface(self) -> Optional[pygame.Surface]:
        """Get current map surface."""
        if self.current_map is None:
            self.set_region(self.current_region)
        return self.current_map

    def geo_to_screen(self, latitude: float, longitude: float) -> Vector2D:
        """
        Convert geo coordinates to screen position.
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Screen position as Vector2D
        """
        if self.current_map is None:
            self.set_region(self.current_region)
            
        if self.current_region == "india":
            bbox = self.REGIONS["india"]
        else:
            bbox = self.REGIONS["indian_ocean"]
        
        lat_min, lon_min, lat_max, lon_max = bbox
        
        x = (longitude - lon_min) / (lon_max - lon_min) * self.screen_width
        y = (lat_max - latitude) / (lat_max - lat_min) * self.screen_height
        
        return Vector2D(x, y)

    def render(self, screen: pygame.Surface) -> None:
        """Render the map to screen."""
        map_surface = self.get_surface()
        if map_surface:
            screen.blit(map_surface, (0, 0))


class OSMMapManager:
    """Manages OSM maps for different simulation scenarios."""

    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """Initialize OSM map manager."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.india_renderer = OSMMapRenderer(screen_width, screen_height)
        self.indian_ocean_renderer = OSMMapRenderer(screen_width, screen_height)
        
        self.indian_ocean_renderer.set_region("indian_ocean")

    def get_renderer(self, map_type: str) -> OSMMapRenderer:
        """Get renderer for map type."""
        if map_type == "indian_ocean":
            return self.indian_ocean_renderer
        return self.india_renderer

    def geo_to_screen(self, latitude: float, longitude: float, map_type: str = "india") -> Vector2D:
        """Convert geo to screen coordinates."""
        return self.get_renderer(map_type).geo_to_screen(latitude, longitude)


def preload_maps():
    """Preload all maps in background."""
    india = OSMMapRenderer(1280, 720)
    india.set_region("india")
    
    ocean = OSMMapRenderer(1280, 720)
    ocean.set_region("indian_ocean")
    
    return india, ocean

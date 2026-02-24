"""2D Vector mathematics for physics simulation."""

import math


class Vector2D:
    """2D vector for position, velocity, and force calculations."""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        """Vector addition."""
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        """Vector subtraction."""
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, scalar):
        """Scalar multiplication."""
        if isinstance(scalar, (int, float)):
            return Vector2D(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        """Right scalar multiplication."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        """Scalar division."""
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero")
            return Vector2D(self.x / scalar, self.y / scalar)
        return NotImplemented

    def __repr__(self):
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

    def copy(self):
        """Return a copy of this vector."""
        return Vector2D(self.x, self.y)

    def magnitude(self):
        """Calculate the magnitude (length) of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_squared(self):
        """Calculate magnitude squared (faster, avoids sqrt)."""
        return self.x * self.x + self.y * self.y

    def normalize(self):
        """Return a normalized copy (magnitude = 1)."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def limit(self, max_magnitude):
        """Return a copy limited to max magnitude."""
        mag_sq = self.magnitude_squared()
        max_sq = max_magnitude * max_magnitude

        if mag_sq > max_sq:
            mag = math.sqrt(mag_sq)
            return Vector2D(self.x / mag * max_magnitude, self.y / mag * max_magnitude)
        return self.copy()

    def distance(self, other):
        """Calculate distance to another vector."""
        if isinstance(other, Vector2D):
            dx = self.x - other.x
            dy = self.y - other.y
            return math.sqrt(dx * dx + dy * dy)
        return NotImplemented

    def distance_squared(self, other):
        """Calculate distance squared (faster, avoids sqrt)."""
        if isinstance(other, Vector2D):
            dx = self.x - other.x
            dy = self.y - other.y
            return dx * dx + dy * dy
        return NotImplemented

    def dot(self, other):
        """Dot product with another vector."""
        if isinstance(other, Vector2D):
            return self.x * other.x + self.y * other.y
        return NotImplemented

    def angle_to(self, other):
        """Calculate angle to another vector in radians."""
        if isinstance(other, Vector2D):
            mag1 = self.magnitude()
            mag2 = other.magnitude()
            if mag1 == 0 or mag2 == 0:
                return 0
            dot_product = self.dot(other)
            cos_angle = dot_product / (mag1 * mag2)
            # Clamp to [-1, 1] to handle floating point errors
            cos_angle = max(-1, min(1, cos_angle))
            return math.acos(cos_angle)
        return NotImplemented

    def rotate(self, radians):
        """Return a rotated copy (counterclockwise)."""
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def perpendicular(self):
        """Return a perpendicular vector (90 degrees counterclockwise)."""
        return Vector2D(-self.y, self.x)

    def clamp_magnitude(self, min_mag, max_mag):
        """Return a copy with magnitude clamped between min and max."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)

        if mag < min_mag:
            return self.normalize() * min_mag
        elif mag > max_mag:
            return self.normalize() * max_mag
        return self.copy()

    def to_tuple(self):
        """Convert to tuple (x, y)."""
        return (self.x, self.y)

    def to_int_tuple(self):
        """Convert to integer tuple for drawing."""
        return (int(self.x), int(self.y))

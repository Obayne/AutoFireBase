"""Professional CAD units system with precision control.

This module provides a comprehensive units system for CAD applications,
supporting common architectural and engineering units with proper
conversion and formatting capabilities.
"""

from __future__ import annotations

from enum import Enum


class Units(Enum):
    """Supported unit systems for CAD applications."""

    FEET = "feet"
    INCHES = "inches"
    MILLIMETERS = "mm"
    CENTIMETERS = "cm"
    METERS = "m"
    POINTS = "points"  # 1/72 inch, for paper space

    def to_base_factor(self) -> float:
        """Get conversion factor to base units (feet).

        Returns:
            Multiplication factor to convert to feet
        """
        return {
            Units.FEET: 1.0,
            Units.INCHES: 1.0 / 12.0,
            Units.MILLIMETERS: 1.0 / 304.8,
            Units.CENTIMETERS: 1.0 / 30.48,
            Units.METERS: 1.0 / 0.3048,
            Units.POINTS: 1.0 / 864.0,  # 1/72 inch = 1/864 feet
        }[self]

    def from_base_factor(self) -> float:
        """Get conversion factor from base units (feet).

        Returns:
            Multiplication factor to convert from feet
        """
        return 1.0 / self.to_base_factor()

    def display_name(self) -> str:
        """Get display name for UI."""
        return {
            Units.FEET: "Feet",
            Units.INCHES: "Inches",
            Units.MILLIMETERS: "Millimeters",
            Units.CENTIMETERS: "Centimeters",
            Units.METERS: "Meters",
            Units.POINTS: "Points",
        }[self]

    def abbreviation(self) -> str:
        """Get standard abbreviation."""
        return {
            Units.FEET: "ft",
            Units.INCHES: "in",
            Units.MILLIMETERS: "mm",
            Units.CENTIMETERS: "cm",
            Units.METERS: "m",
            Units.POINTS: "pt",
        }[self]

    def symbol(self) -> str:
        """Get symbol for formatting."""
        return {
            Units.FEET: "'",
            Units.INCHES: '"',
            Units.MILLIMETERS: "mm",
            Units.CENTIMETERS: "cm",
            Units.METERS: "m",
            Units.POINTS: "pt",
        }[self]


class UnitConverter:
    """Handles conversion between different unit systems."""

    def __init__(self, base_units: Units = Units.FEET):
        """Initialize converter with base units.

        Args:
            base_units: Base units for internal calculations
        """
        self.base_units = base_units
        self._base_factor = base_units.to_base_factor()

    def to_base(self, value: float, from_units: Units) -> float:
        """Convert value to base units.

        Args:
            value: Value in source units
            from_units: Source units

        Returns:
            Value in base units
        """
        return value * from_units.to_base_factor() / self._base_factor

    def from_base(self, value: float, to_units: Units) -> float:
        """Convert value from base units.

        Args:
            value: Value in base units
            to_units: Target units

        Returns:
            Value in target units
        """
        return value * self._base_factor / to_units.to_base_factor()

    def convert(self, value: float, from_units: Units, to_units: Units) -> float:
        """Convert between any two unit systems.

        Args:
            value: Value in source units
            from_units: Source units
            to_units: Target units

        Returns:
            Value in target units
        """
        if from_units == to_units:
            return value

        # Convert through base units
        base_value = self.to_base(value, from_units)
        return self.from_base(base_value, to_units)


class Precision:
    """Controls precision and rounding for CAD calculations."""

    def __init__(self, decimal_places: int = 6, tolerance: float = 1e-12):
        """Initialize precision control.

        Args:
            decimal_places: Number of decimal places for display
            tolerance: Tolerance for equality comparisons
        """
        self.decimal_places = decimal_places
        self.tolerance = tolerance
        self._round_factor = 10**decimal_places

    def round_value(self, value: float) -> float:
        """Round value to specified precision.

        Args:
            value: Value to round

        Returns:
            Rounded value
        """
        return round(value, self.decimal_places)

    def are_equal(self, a: float, b: float) -> bool:
        """Test if two values are equal within tolerance.

        Args:
            a: First value
            b: Second value

        Returns:
            True if values are equal within tolerance
        """
        return abs(a - b) < self.tolerance

    def snap_to_grid(self, value: float, grid_size: float) -> float:
        """Snap value to grid.

        Args:
            value: Value to snap
            grid_size: Grid spacing

        Returns:
            Snapped value
        """
        if grid_size <= 0:
            return value
        return round(value / grid_size) * grid_size


class Formatter:
    """Formats measurements for display in various unit systems."""

    def __init__(self, units: Units, precision: Precision):
        """Initialize formatter.

        Args:
            units: Display units
            precision: Precision control
        """
        self.units = units
        self.precision = precision

    def format_distance(self, value: float) -> str:
        """Format distance value for display.

        Args:
            value: Distance value in current units

        Returns:
            Formatted string
        """
        if self.units == Units.FEET:
            return self._format_feet_inches(value)
        elif self.units == Units.INCHES:
            return self._format_inches(value)
        else:
            rounded = self.precision.round_value(value)
            symbol = self.units.symbol()
            return f"{rounded}{symbol}"

    def format_area(self, value: float) -> str:
        """Format area value for display.

        Args:
            value: Area value in current units squared

        Returns:
            Formatted string
        """
        rounded = self.precision.round_value(value)
        symbol = self.units.symbol()
        return f"{rounded} {symbol}²"

    def format_coordinate(self, x: float, y: float) -> str:
        """Format coordinate pair for display.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Formatted coordinate string
        """
        x_str = self.format_distance(x)
        y_str = self.format_distance(y)
        return f"({x_str}, {y_str})"

    def _format_feet_inches(self, feet: float) -> str:
        """Format value as feet and inches (architectural style).

        Args:
            feet: Value in feet

        Returns:
            Formatted string like "10'-6 3/4\""
        """
        if abs(feet) < self.precision.tolerance:
            return '0"'

        sign = "-" if feet < 0 else ""
        feet = abs(feet)

        whole_feet = int(feet)
        remaining_inches = (feet - whole_feet) * 12.0

        if remaining_inches < self.precision.tolerance:
            if whole_feet == 0:
                return '0"'
            return f"{sign}{whole_feet}'"

        # Format inches with fractional part
        inches_str = self._format_inches_with_fractions(remaining_inches)

        if whole_feet == 0:
            return f"{sign}{inches_str}"
        else:
            return f"{sign}{whole_feet}'-{inches_str}"

    def _format_inches(self, inches: float) -> str:
        """Format value as inches only.

        Args:
            inches: Value in inches

        Returns:
            Formatted string
        """
        if abs(inches) < self.precision.tolerance:
            return '0"'

        return self._format_inches_with_fractions(inches)

    def _format_inches_with_fractions(self, inches: float) -> str:
        """Format inches with fractional parts.

        Args:
            inches: Value in inches

        Returns:
            Formatted string like "6 3/4\"" or "0.75\""
        """
        sign = "-" if inches < 0 else ""
        inches = abs(inches)

        whole_inches = int(inches)
        fractional_part = inches - whole_inches

        # Try to represent as common fractions
        fraction_str = self._decimal_to_fraction(fractional_part)

        if fraction_str:
            if whole_inches == 0:
                return f'{sign}{fraction_str}"'
            else:
                return f'{sign}{whole_inches} {fraction_str}"'
        else:
            # Use decimal representation
            rounded = self.precision.round_value(inches)
            return f'{sign}{rounded}"'

    def _decimal_to_fraction(self, decimal: float) -> str | None:
        """Convert decimal to common architectural fraction.

        Args:
            decimal: Decimal value between 0 and 1

        Returns:
            Fraction string or None if no good match
        """
        if decimal < self.precision.tolerance:
            return None

        # Common architectural fractions (denominator: numerator)
        fractions = {
            64: [
                1,
                3,
                5,
                7,
                9,
                11,
                13,
                15,
                17,
                19,
                21,
                23,
                25,
                27,
                29,
                31,
                33,
                35,
                37,
                39,
                41,
                43,
                45,
                47,
                49,
                51,
                53,
                55,
                57,
                59,
                61,
                63,
            ],
            32: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31],
            16: [1, 3, 5, 7, 9, 11, 13, 15],
            8: [1, 3, 5, 7],
            4: [1, 3],
            2: [1],
        }

        tolerance = 1.0 / 128.0  # 1/128 inch tolerance

        for denominator in [64, 32, 16, 8, 4, 2]:
            for numerator in fractions[denominator]:
                fraction_value = numerator / denominator
                if abs(decimal - fraction_value) < tolerance:
                    # Simplify fraction
                    return self._simplify_fraction(numerator, denominator)

        return None

    def _simplify_fraction(self, numerator: int, denominator: int) -> str:
        """Simplify fraction to lowest terms.

        Args:
            numerator: Fraction numerator
            denominator: Fraction denominator

        Returns:
            Simplified fraction string
        """

        def gcd(a: int, b: int) -> int:
            while b:
                a, b = b, a % b
            return a

        g = gcd(numerator, denominator)
        num = numerator // g
        den = denominator // g

        return f"{num}/{den}"


class UnitSystem:
    """Complete unit system for CAD applications."""

    def __init__(
        self,
        display_units: Units = Units.FEET,
        base_units: Units = Units.FEET,
        precision: Precision | None = None,
    ):
        """Initialize unit system.

        Args:
            display_units: Units for display and input
            base_units: Units for internal calculations
            precision: Precision control (default: 6 decimal places)
        """
        self.display_units = display_units
        self.base_units = base_units
        self.precision = precision or Precision()

        self.converter = UnitConverter(base_units)
        self.formatter = Formatter(display_units, self.precision)

    def set_display_units(self, units: Units) -> None:
        """Change display units.

        Args:
            units: New display units
        """
        self.display_units = units
        self.formatter = Formatter(units, self.precision)

    def set_precision(self, decimal_places: int) -> None:
        """Change precision.

        Args:
            decimal_places: Number of decimal places
        """
        self.precision = Precision(decimal_places, self.precision.tolerance)
        self.formatter = Formatter(self.display_units, self.precision)

    def parse_distance(self, text: str) -> float | None:
        """Parse distance string to value in display units.

        Args:
            text: Input string (e.g., "10'-6\"", "3.5", "100mm")

        Returns:
            Value in display units, or None if parsing fails
        """
        text = text.strip()
        if not text:
            return None

        try:
            # Try simple decimal first
            return float(text)
        except ValueError:
            pass

        # Try feet-inches format
        feet_inches = self._parse_feet_inches(text)
        if feet_inches is not None:
            if self.display_units == Units.FEET:
                return feet_inches
            else:
                return self.converter.convert(feet_inches, Units.FEET, self.display_units)

        # Try with unit suffix
        for unit in Units:
            symbol = unit.symbol()
            abbrev = unit.abbreviation()

            if text.endswith(symbol) or text.endswith(abbrev):
                value_str = text[: -len(symbol)] if text.endswith(symbol) else text[: -len(abbrev)]
                try:
                    value = float(value_str.strip())
                    return self.converter.convert(value, unit, self.display_units)
                except ValueError:
                    pass

        return None

    def _parse_feet_inches(self, text: str) -> float | None:
        """Parse feet-inches format to feet.

        Args:
            text: Input like "10'-6\"", "10'", "6\"", "10'-6 3/4\""

        Returns:
            Value in feet, or None if parsing fails
        """
        text = text.strip()

        # Handle negative values
        negative = text.startswith("-")
        if negative:
            text = text[1:].strip()

        feet = 0.0
        inches = 0.0

        # Split on feet marker
        if "'" in text:
            parts = text.split("'", 1)
            try:
                feet = float(parts[0].strip())
            except ValueError:
                return None

            if len(parts) > 1:
                inch_part = parts[1].strip()
                if inch_part.startswith("-"):
                    inch_part = inch_part[1:].strip()

                if inch_part and inch_part != '"':
                    parsed_inches = self._parse_inches_part(inch_part)
                    if parsed_inches is None:
                        return None
                    inches = parsed_inches
        else:
            # Just inches
            if text.endswith('"'):
                text = text[:-1]
            parsed_inches = self._parse_inches_part(text)
            if parsed_inches is None:
                return None
            inches = parsed_inches

        result = feet + inches / 12.0
        return -result if negative else result

    def _parse_inches_part(self, text: str) -> float | None:
        """Parse inches part with fractions.

        Args:
            text: Input like "6", "6.5", "6 3/4", "3/4"

        Returns:
            Value in inches, or None if parsing fails
        """
        text = text.strip()
        if text.endswith('"'):
            text = text[:-1].strip()

        if not text:
            return 0.0

        # Check for fraction
        if "/" in text:
            if " " in text:
                # Whole number and fraction
                parts = text.split(" ", 1)
                try:
                    whole = float(parts[0])
                    frac = self._parse_fraction(parts[1])
                    if frac is None:
                        return None
                    return whole + frac
                except ValueError:
                    return None
            else:
                # Just fraction
                return self._parse_fraction(text)
        else:
            # Just decimal
            try:
                return float(text)
            except ValueError:
                return None

    def _parse_fraction(self, text: str) -> float | None:
        """Parse fraction like "3/4".

        Args:
            text: Fraction string

        Returns:
            Decimal value or None if parsing fails
        """
        if "/" not in text:
            return None

        parts = text.split("/", 1)
        if len(parts) != 2:
            return None

        try:
            numerator = float(parts[0].strip())
            denominator = float(parts[1].strip())
            if denominator == 0:
                return None
            return numerator / denominator
        except ValueError:
            return None


# Default system instances
DEFAULT_IMPERIAL = UnitSystem(Units.FEET, Units.FEET)
DEFAULT_METRIC = UnitSystem(Units.MILLIMETERS, Units.METERS)

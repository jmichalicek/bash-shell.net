"""
Parser for BeerXML format to create RecipePage drafts.

This module provides utilities to parse BeerXML data and create RecipePage instances
with related fermentables, hops, yeasts, and misc ingredients.

BeerXML specification: https://www.beerxml.com/beerxml.htm
"""

import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import Any


class BeerXMLParseError(Exception):
    """Exception raised when parsing BeerXML fails."""

    pass


def parse_beerxml(xml_content: str) -> dict[str, Any]:
    """
    Parse BeerXML content and extract recipe data.

    Args:
        xml_content: String containing BeerXML data

    Returns:
        Dictionary containing parsed recipe data suitable for creating a RecipePage

    Raises:
        BeerXMLParseError: If XML is invalid or required fields are missing
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise BeerXMLParseError(f"Invalid XML: {e}") from e

    # Find the first RECIPE element
    recipe = root.find("RECIPE")
    if recipe is None:
        # Maybe the root is already a RECIPE
        if root.tag == "RECIPE":
            recipe = root
        else:
            raise BeerXMLParseError("No RECIPE element found in XML")

    return _parse_recipe(recipe)


def _get_text(element: ET.Element, tag: str, default: str = "") -> str:
    """Get text content of a child element."""
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else default


def _get_decimal(element: ET.Element, tag: str, default: Decimal | None = None) -> Decimal | None:
    """Get decimal value from a child element."""
    text = _get_text(element, tag)
    if not text:
        return default
    try:
        return Decimal(text)
    except (ValueError, TypeError):
        return default


def _get_int(element: ET.Element, tag: str, default: int | None = None) -> int | None:
    """Get integer value from a child element."""
    text = _get_text(element, tag)
    if not text:
        return default
    try:
        return int(float(text))  # float first in case of "60.0"
    except (ValueError, TypeError):
        return default


def _kg_to_pounds(kg: Decimal) -> Decimal:
    """Convert kilograms to pounds."""
    return kg * Decimal("2.20462262")


def _kg_to_ounces(kg: Decimal) -> Decimal:
    """Convert kilograms to ounces."""
    return _kg_to_pounds(kg) * Decimal("16")


def _liters_to_gallons(liters: Decimal) -> Decimal:
    """Convert liters to gallons."""
    return liters * Decimal("0.264172")


def _parse_recipe_type(type_str: str) -> str:
    """Convert BeerXML TYPE to RecipePage recipe_type."""
    from bash_shell_net.on_tap.models import RecipeType

    type_map = {
        "Extract": RecipeType.EXTRACT,
        "Partial Mash": RecipeType.PARTIAL_MASH,
        "All Grain": RecipeType.ALL_GRAIN,
    }
    return type_map.get(type_str, RecipeType.ALL_GRAIN)


def _parse_fermentable_type(type_str: str) -> str:
    """Convert BeerXML fermentable TYPE to RecipeFermentable type."""
    from bash_shell_net.on_tap.models import FermentableType

    type_map = {
        "Grain": FermentableType.GRAIN,
        "Sugar": FermentableType.SUGAR,
        "Extract": FermentableType.LIQUID_EXTRACT,
        "Dry Extract": FermentableType.DRY_EXTRACT,
        "Adjunct": FermentableType.ADJUNCT,
    }
    return type_map.get(type_str, FermentableType.GRAIN)


def _parse_hop_use(use_str: str) -> str:
    """Convert BeerXML hop USE to RecipeHop use_step."""
    use_map = {
        "Boil": "boil",
        "Dry Hop": "dryhop",
        "Mash": "mash",
        "First Wort": "firstwort",
        "Aroma": "aroma",
    }
    return use_map.get(use_str, "boil")


def _parse_hop_form(form_str: str) -> str:
    """Convert BeerXML hop FORM to RecipeHop form."""
    form_map = {
        "Pellet": "pellet",
        "Plug": "plug",
        "Leaf": "leaf",
    }
    return form_map.get(form_str, "pellet")


def _parse_yeast_type(form_str: str) -> str:
    """Convert BeerXML yeast FORM to RecipeYeast yeast_type."""
    # BeerXML uses FORM field, not TYPE
    form_map = {
        "Liquid": "liquid",
        "Dry": "dry",
        "Slant": "liquid",
        "Culture": "liquid",
    }
    return form_map.get(form_str, "liquid")


def _parse_misc_type(type_str: str) -> str:
    """Convert BeerXML misc TYPE to RecipeMiscIngredient type."""
    type_map = {
        "Spice": "spice",
        "Fining": "fining",
        "Water Agent": "water_agent",
        "Herb": "herb",
        "Flavor": "flavor",
        "Other": "other",
    }
    return type_map.get(type_str, "other")


def _parse_misc_use(use_str: str) -> str:
    """Convert BeerXML misc USE to RecipeMiscIngredient use_step."""
    use_map = {
        "Boil": "boil",
        "Mash": "mash",
        "Primary": "primary",
        "Secondary": "secondary",
        "Bottling": "bottling",
    }
    return use_map.get(use_str, "boil")


def _parse_recipe(recipe: ET.Element) -> dict[str, Any]:
    """Parse a RECIPE element into a dictionary."""
    name = _get_text(recipe, "NAME", "Untitled Recipe")
    recipe_type = _parse_recipe_type(_get_text(recipe, "TYPE", "All Grain"))
    brewer = _get_text(recipe, "BREWER", "")
    assistant_brewer = _get_text(recipe, "ASST_BREWER", "")

    # BeerXML uses liters, convert to gallons for storage
    batch_size_liters = _get_decimal(recipe, "BATCH_SIZE", Decimal("19"))
    boil_size_liters = _get_decimal(recipe, "BOIL_SIZE", Decimal("23"))
    batch_size = _liters_to_gallons(batch_size_liters or Decimal("19"))
    boil_size = _liters_to_gallons(boil_size_liters or Decimal("23"))

    boil_time = _get_int(recipe, "BOIL_TIME", 60)
    efficiency = _get_int(recipe, "EFFICIENCY")

    # Gravity values
    original_gravity = _get_decimal(recipe, "OG", Decimal("1.000"))
    final_gravity = _get_decimal(recipe, "FG", Decimal("1.000"))
    boil_gravity = _get_decimal(recipe, "BOIL_GRAVITY")

    # Notes
    notes = _get_text(recipe, "NOTES", "")
    taste_notes = _get_text(recipe, "TASTE_NOTES", "")
    if taste_notes:
        notes = f"{notes}\n\nTaste Notes:\n{taste_notes}" if notes else f"Taste Notes:\n{taste_notes}"

    # Parse ingredients
    fermentables = _parse_fermentables(recipe)
    hops = _parse_hops(recipe)
    yeasts = _parse_yeasts(recipe)
    misc_ingredients = _parse_misc_ingredients(recipe)

    from bash_shell_net.on_tap.models import VolumeUnit

    return {
        "title": name,
        "recipe_type": recipe_type,
        "brewer": brewer,
        "assistant_brewer": assistant_brewer,
        "volume_units": VolumeUnit.GALLON,
        "batch_size": batch_size,
        "boil_size": boil_size,
        "boil_time": boil_time,
        "efficiency": efficiency,
        "boil_gravity": boil_gravity,
        "original_gravity": original_gravity or Decimal("1.000"),
        "final_gravity": final_gravity or Decimal("1.000"),
        "ibus_tinseth": Decimal("0"),  # Not calculating, user can update
        "notes": notes,
        "short_description": "",
        "fermentables": fermentables,
        "hops": hops,
        "yeasts": yeasts,
        "miscellaneous_ingredients": misc_ingredients,
    }


def _parse_fermentables(recipe: ET.Element) -> list[dict[str, Any]]:
    """Parse FERMENTABLES section."""
    fermentables_section = recipe.find("FERMENTABLES")
    if fermentables_section is None:
        return []

    result = []
    for fermentable in fermentables_section.findall("FERMENTABLE"):
        name = _get_text(fermentable, "NAME", "Unknown Fermentable")
        # BeerXML uses kg, we'll convert to pounds
        amount_kg = _get_decimal(fermentable, "AMOUNT", Decimal("0"))
        amount_lb = _kg_to_pounds(amount_kg or Decimal("0"))

        fermentable_type = _parse_fermentable_type(_get_text(fermentable, "TYPE", "Grain"))
        color = _get_decimal(fermentable, "COLOR", Decimal("0"))
        origin = _get_text(fermentable, "ORIGIN", "")
        supplier = _get_text(fermentable, "SUPPLIER", "")
        notes = _get_text(fermentable, "NOTES", "")

        result.append(
            {
                "name": name,
                "amount": amount_lb,
                "amount_units": "lb",
                "type": fermentable_type,
                "color": color,
                "maltster": supplier if supplier else origin,
                "notes": notes,
            }
        )

    return result


def _parse_hops(recipe: ET.Element) -> list[dict[str, Any]]:
    """Parse HOPS section."""
    hops_section = recipe.find("HOPS")
    if hops_section is None:
        return []

    result = []
    for hop in hops_section.findall("HOP"):
        name = _get_text(hop, "NAME", "Unknown Hop")
        # BeerXML uses kg, convert to ounces
        amount_kg = _get_decimal(hop, "AMOUNT", Decimal("0"))
        amount_oz = _kg_to_ounces(amount_kg or Decimal("0"))

        alpha_acid = _get_decimal(hop, "ALPHA", Decimal("0"))
        use = _parse_hop_use(_get_text(hop, "USE", "Boil"))
        time = _get_int(hop, "TIME", 0)
        form = _parse_hop_form(_get_text(hop, "FORM", "Pellet"))
        beta_acid = _get_decimal(hop, "BETA")
        notes = _get_text(hop, "NOTES", "")

        result.append(
            {
                "name": name,
                "amount": amount_oz,
                "amount_units": "oz",
                "alpha_acid_percent": alpha_acid or Decimal("0"),
                "use_step": use,
                "use_time": time or 0,
                "form": form,
                "beta_acid_percent": beta_acid,
                "notes": notes,
            }
        )

    return result


def _parse_yeasts(recipe: ET.Element) -> list[dict[str, Any]]:
    """Parse YEASTS section."""
    yeasts_section = recipe.find("YEASTS")
    if yeasts_section is None:
        return []

    result = []
    for yeast in yeasts_section.findall("YEAST"):
        name = _get_text(yeast, "NAME", "Unknown Yeast")
        laboratory = _get_text(yeast, "LABORATORY", "")
        product_id = _get_text(yeast, "PRODUCT_ID", "")

        # Build complete name with lab and product ID if available
        if laboratory and product_id:
            full_name = f"{laboratory} {product_id} - {name}"
        elif laboratory:
            full_name = f"{laboratory} - {name}"
        else:
            full_name = name

        # BeerXML AMOUNT can be weight or volume based on AMOUNT_IS_WEIGHT
        amount = _get_decimal(yeast, "AMOUNT")
        amount_is_weight_str = _get_text(yeast, "AMOUNT_IS_WEIGHT", "FALSE")
        amount_is_weight = amount_is_weight_str.upper() == "TRUE"

        # Convert amount and determine units
        if amount:
            if amount_is_weight:
                # Convert kg to grams
                amount_converted = amount * Decimal("1000")
                amount_units = "g"
            else:
                # Convert liters to fluid oz
                amount_converted = amount * Decimal("33.814")
                amount_units = "fl_oz"
        else:
            amount_converted = None
            amount_units = ""

        yeast_type = _parse_yeast_type(_get_text(yeast, "FORM", "Liquid"))
        add_to_secondary_str = _get_text(yeast, "ADD_TO_SECONDARY", "FALSE")
        add_to_secondary = add_to_secondary_str.upper() == "TRUE"

        notes = _get_text(yeast, "NOTES", "")
        best_for = _get_text(yeast, "BEST_FOR", "")
        if best_for:
            notes = f"Best for: {best_for}\n\n{notes}" if notes else f"Best for: {best_for}"

        result.append(
            {
                "name": full_name,
                "amount": amount_converted,
                "amount_units": amount_units,
                "yeast_type": yeast_type,
                "add_to_secondary": add_to_secondary,
                "notes": notes,
            }
        )

    return result


def _parse_misc_ingredients(recipe: ET.Element) -> list[dict[str, Any]]:
    """Parse MISCS section."""
    miscs_section = recipe.find("MISCS")
    if miscs_section is None:
        return []

    result = []
    for misc in miscs_section.findall("MISC"):
        name = _get_text(misc, "NAME", "Unknown Ingredient")
        misc_type = _parse_misc_type(_get_text(misc, "TYPE", "Other"))
        use_step = _parse_misc_use(_get_text(misc, "USE", "Boil"))
        time = _get_int(misc, "TIME", 0)

        # BeerXML AMOUNT can be weight or volume based on AMOUNT_IS_WEIGHT
        amount = _get_decimal(misc, "AMOUNT")
        amount_is_weight_str = _get_text(misc, "AMOUNT_IS_WEIGHT", "FALSE")
        amount_is_weight = amount_is_weight_str.upper() == "TRUE"

        # Convert amount and determine units
        if amount:
            if amount_is_weight:
                # Convert kg to grams
                amount_converted = amount * Decimal("1000")
                amount_units = "g"
            else:
                # Convert liters to fluid oz
                amount_converted = amount * Decimal("33.814")
                amount_units = "fl_oz"
        else:
            amount_converted = None
            amount_units = ""

        use_for = _get_text(misc, "USE_FOR", "")
        notes = _get_text(misc, "NOTES", "")

        result.append(
            {
                "name": name,
                "type": misc_type,
                "amount": amount_converted,
                "amount_units": amount_units,
                "use_step": use_step,
                "use_time": time or 0,
                "use_for": use_for,
                "notes": notes,
            }
        )

    return result

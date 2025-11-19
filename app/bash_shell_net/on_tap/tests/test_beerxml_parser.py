"""
Tests for BeerXML parser functionality.
"""

from decimal import Decimal

from django.test import TestCase

from bash_shell_net.on_tap.beerxml_parser import BeerXMLParseError, parse_beerxml
from bash_shell_net.on_tap.models import FermentableType, RecipeType, VolumeUnit


class BeerXMLParserTestCase(TestCase):
    """Test the BeerXML parser."""

    def test_parse_basic_recipe(self):
        """Test parsing a basic recipe with required fields."""
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <RECIPES>
            <RECIPE>
                <NAME>Test Recipe</NAME>
                <VERSION>1</VERSION>
                <TYPE>All Grain</TYPE>
                <BREWER>Test Brewer</BREWER>
                <BATCH_SIZE>19.0</BATCH_SIZE>
                <BOIL_SIZE>23.0</BOIL_SIZE>
                <BOIL_TIME>60</BOIL_TIME>
                <EFFICIENCY>75</EFFICIENCY>
                <OG>1.050</OG>
                <FG>1.010</FG>
                <HOPS></HOPS>
                <FERMENTABLES></FERMENTABLES>
                <MISCS></MISCS>
                <YEASTS></YEASTS>
            </RECIPE>
        </RECIPES>
        """

        result = parse_beerxml(xml)

        self.assertEqual(result["title"], "Test Recipe")
        self.assertEqual(result["recipe_type"], RecipeType.ALL_GRAIN)
        self.assertEqual(result["brewer"], "Test Brewer")
        self.assertEqual(result["volume_units"], VolumeUnit.GALLON)
        # Batch size should be converted from liters to gallons (19L ~= 5.02 gal)
        self.assertAlmostEqual(float(result["batch_size"]), 5.02, places=1)
        self.assertEqual(result["boil_time"], 60)
        self.assertEqual(result["efficiency"], 75)
        self.assertEqual(result["original_gravity"], Decimal("1.050"))
        self.assertEqual(result["final_gravity"], Decimal("1.010"))

    def test_parse_recipe_with_fermentables(self):
        """Test parsing recipe with fermentables."""
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <RECIPE>
            <NAME>Test Recipe</NAME>
            <VERSION>1</VERSION>
            <TYPE>All Grain</TYPE>
            <BREWER>Test</BREWER>
            <BATCH_SIZE>19.0</BATCH_SIZE>
            <BOIL_SIZE>23.0</BOIL_SIZE>
            <BOIL_TIME>60</BOIL_TIME>
            <EFFICIENCY>75</EFFICIENCY>
            <FERMENTABLES>
                <FERMENTABLE>
                    <NAME>Pale Malt</NAME>
                    <VERSION>1</VERSION>
                    <TYPE>Grain</TYPE>
                    <AMOUNT>4.5</AMOUNT>
                    <YIELD>78.0</YIELD>
                    <COLOR>3.0</COLOR>
                    <SUPPLIER>Test Maltster</SUPPLIER>
                    <NOTES>Base malt</NOTES>
                </FERMENTABLE>
            </FERMENTABLES>
            <HOPS></HOPS>
            <MISCS></MISCS>
            <YEASTS></YEASTS>
        </RECIPE>
        """

        result = parse_beerxml(xml)

        self.assertEqual(len(result["fermentables"]), 1)
        ferm = result["fermentables"][0]
        self.assertEqual(ferm["name"], "Pale Malt")
        self.assertEqual(ferm["type"], FermentableType.GRAIN)
        # 4.5 kg = ~9.92 lbs
        self.assertAlmostEqual(float(ferm["amount"]), 9.92, places=1)
        self.assertEqual(ferm["amount_units"], "lb")
        self.assertEqual(ferm["color"], Decimal("3.0"))
        self.assertEqual(ferm["maltster"], "Test Maltster")
        self.assertEqual(ferm["notes"], "Base malt")

    def test_parse_recipe_with_hops(self):
        """Test parsing recipe with hops."""
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <RECIPE>
            <NAME>Test Recipe</NAME>
            <VERSION>1</VERSION>
            <TYPE>All Grain</TYPE>
            <BREWER>Test</BREWER>
            <BATCH_SIZE>19.0</BATCH_SIZE>
            <BOIL_SIZE>23.0</BOIL_SIZE>
            <BOIL_TIME>60</BOIL_TIME>
            <HOPS>
                <HOP>
                    <NAME>Cascade</NAME>
                    <VERSION>1</VERSION>
                    <ALPHA>5.5</ALPHA>
                    <AMOUNT>0.028</AMOUNT>
                    <USE>Boil</USE>
                    <TIME>60</TIME>
                    <FORM>Pellet</FORM>
                    <NOTES>Citrus and floral</NOTES>
                </HOP>
            </HOPS>
            <FERMENTABLES></FERMENTABLES>
            <MISCS></MISCS>
            <YEASTS></YEASTS>
        </RECIPE>
        """

        result = parse_beerxml(xml)

        self.assertEqual(len(result["hops"]), 1)
        hop = result["hops"][0]
        self.assertEqual(hop["name"], "Cascade")
        self.assertEqual(hop["alpha_acid_percent"], Decimal("5.5"))
        # 0.028 kg = ~0.99 oz
        self.assertAlmostEqual(float(hop["amount"]), 0.99, places=1)
        self.assertEqual(hop["amount_units"], "oz")
        self.assertEqual(hop["use_step"], "boil")
        self.assertEqual(hop["use_time"], 60)
        self.assertEqual(hop["form"], "pellet")
        self.assertEqual(hop["notes"], "Citrus and floral")

    def test_parse_recipe_with_yeast(self):
        """Test parsing recipe with yeast."""
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <RECIPE>
            <NAME>Test Recipe</NAME>
            <VERSION>1</VERSION>
            <TYPE>All Grain</TYPE>
            <BREWER>Test</BREWER>
            <BATCH_SIZE>19.0</BATCH_SIZE>
            <BOIL_SIZE>23.0</BOIL_SIZE>
            <BOIL_TIME>60</BOIL_TIME>
            <HOPS></HOPS>
            <FERMENTABLES></FERMENTABLES>
            <MISCS></MISCS>
            <YEASTS>
                <YEAST>
                    <NAME>American Ale</NAME>
                    <VERSION>1</VERSION>
                    <TYPE>Ale</TYPE>
                    <FORM>Liquid</FORM>
                    <AMOUNT>0.1</AMOUNT>
                    <LABORATORY>Wyeast</LABORATORY>
                    <PRODUCT_ID>1056</PRODUCT_ID>
                    <NOTES>Clean fermenting</NOTES>
                    <BEST_FOR>American ales</BEST_FOR>
                </YEAST>
            </YEASTS>
        </RECIPE>
        """

        result = parse_beerxml(xml)

        self.assertEqual(len(result["yeasts"]), 1)
        yeast = result["yeasts"][0]
        self.assertEqual(yeast["name"], "Wyeast 1056 - American Ale")
        self.assertEqual(yeast["yeast_type"], "liquid")
        # 0.1 liter = ~3.38 fl oz
        self.assertAlmostEqual(float(yeast["amount"]), 3.38, places=1)
        self.assertEqual(yeast["amount_units"], "fl_oz")
        self.assertIn("Best for: American ales", yeast["notes"])

    def test_parse_recipe_with_misc_ingredient(self):
        """Test parsing recipe with misc ingredients."""
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <RECIPE>
            <NAME>Test Recipe</NAME>
            <VERSION>1</VERSION>
            <TYPE>All Grain</TYPE>
            <BREWER>Test</BREWER>
            <BATCH_SIZE>19.0</BATCH_SIZE>
            <BOIL_SIZE>23.0</BOIL_SIZE>
            <BOIL_TIME>60</BOIL_TIME>
            <HOPS></HOPS>
            <FERMENTABLES></FERMENTABLES>
            <YEASTS></YEASTS>
            <MISCS>
                <MISC>
                    <NAME>Irish Moss</NAME>
                    <VERSION>1</VERSION>
                    <TYPE>Fining</TYPE>
                    <USE>Boil</USE>
                    <TIME>15</TIME>
                    <AMOUNT>0.01</AMOUNT>
                    <AMOUNT_IS_WEIGHT>TRUE</AMOUNT_IS_WEIGHT>
                    <USE_FOR>Clarity</USE_FOR>
                    <NOTES>Add at 15 minutes</NOTES>
                </MISC>
            </MISCS>
        </RECIPE>
        """

        result = parse_beerxml(xml)

        self.assertEqual(len(result["miscellaneous_ingredients"]), 1)
        misc = result["miscellaneous_ingredients"][0]
        self.assertEqual(misc["name"], "Irish Moss")
        self.assertEqual(misc["type"], "fining")
        # 0.01 kg = 10 g
        self.assertEqual(float(misc["amount"]), 10.0)
        self.assertEqual(misc["amount_units"], "g")
        self.assertEqual(misc["use_step"], "boil")
        self.assertEqual(misc["use_time"], 15)
        self.assertEqual(misc["use_for"], "Clarity")

    def test_parse_invalid_xml(self):
        """Test that invalid XML raises BeerXMLParseError."""
        xml = "This is not XML"

        with self.assertRaises(BeerXMLParseError):
            parse_beerxml(xml)

    def test_parse_xml_without_recipe(self):
        """Test that XML without RECIPE element raises BeerXMLParseError."""
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <HOPS>
            <HOP>
                <NAME>Cascade</NAME>
            </HOP>
        </HOPS>
        """

        with self.assertRaises(BeerXMLParseError):
            parse_beerxml(xml)

    def test_parse_recipe_type_conversion(self):
        """Test recipe type conversion."""
        for beerxml_type, expected_type in [
            ("All Grain", RecipeType.ALL_GRAIN),
            ("Extract", RecipeType.EXTRACT),
            ("Partial Mash", RecipeType.PARTIAL_MASH),
        ]:
            xml = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
            <RECIPE>
                <NAME>Test</NAME>
                <VERSION>1</VERSION>
                <TYPE>{beerxml_type}</TYPE>
                <BREWER>Test</BREWER>
                <BATCH_SIZE>19.0</BATCH_SIZE>
                <BOIL_SIZE>23.0</BOIL_SIZE>
                <BOIL_TIME>60</BOIL_TIME>
                <HOPS></HOPS>
                <FERMENTABLES></FERMENTABLES>
                <MISCS></MISCS>
                <YEASTS></YEASTS>
            </RECIPE>
            """

            result = parse_beerxml(xml)
            self.assertEqual(result["recipe_type"], expected_type)

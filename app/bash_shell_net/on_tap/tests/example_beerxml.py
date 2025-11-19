"""
Example BeerXML recipes for testing the import functionality.
"""

# Example 1: Simple Pale Ale
SIMPLE_PALE_ALE = """<?xml version="1.0" encoding="ISO-8859-1"?>
<RECIPES>
  <RECIPE>
    <NAME>Simple American Pale Ale</NAME>
    <VERSION>1</VERSION>
    <TYPE>All Grain</TYPE>
    <BREWER>Test Brewer</BREWER>
    <BATCH_SIZE>18.93</BATCH_SIZE>
    <BOIL_SIZE>22.71</BOIL_SIZE>
    <BOIL_TIME>60</BOIL_TIME>
    <EFFICIENCY>72.0</EFFICIENCY>
    <OG>1.056</OG>
    <FG>1.012</FG>
    <NOTES>A simple American Pale Ale with Cascade hops and a clean American ale yeast.</NOTES>

    <FERMENTABLES>
      <FERMENTABLE>
        <NAME>Pale Malt (2 row) US</NAME>
        <VERSION>1</VERSION>
        <TYPE>Grain</TYPE>
        <AMOUNT>4.5</AMOUNT>
        <YIELD>79.0</YIELD>
        <COLOR>2.0</COLOR>
        <SUPPLIER>Briess</SUPPLIER>
        <NOTES>Base malt for American styles</NOTES>
      </FERMENTABLE>
      <FERMENTABLE>
        <NAME>Crystal 40L</NAME>
        <VERSION>1</VERSION>
        <TYPE>Grain</TYPE>
        <AMOUNT>0.454</AMOUNT>
        <YIELD>74.0</YIELD>
        <COLOR>40.0</COLOR>
        <SUPPLIER>Briess</SUPPLIER>
        <NOTES>Adds body and caramel sweetness</NOTES>
      </FERMENTABLE>
    </FERMENTABLES>

    <HOPS>
      <HOP>
        <NAME>Cascade</NAME>
        <VERSION>1</VERSION>
        <ALPHA>5.5</ALPHA>
        <AMOUNT>0.028</AMOUNT>
        <USE>Boil</USE>
        <TIME>60</TIME>
        <FORM>Pellet</FORM>
        <NOTES>Classic American hop with citrus and floral notes</NOTES>
      </HOP>
      <HOP>
        <NAME>Cascade</NAME>
        <VERSION>1</VERSION>
        <ALPHA>5.5</ALPHA>
        <AMOUNT>0.028</AMOUNT>
        <USE>Boil</USE>
        <TIME>15</TIME>
        <FORM>Pellet</FORM>
        <NOTES>Late addition for aroma</NOTES>
      </HOP>
      <HOP>
        <NAME>Cascade</NAME>
        <VERSION>1</VERSION>
        <ALPHA>5.5</ALPHA>
        <AMOUNT>0.028</AMOUNT>
        <USE>Dry Hop</USE>
        <TIME>10080</TIME>
        <FORM>Pellet</FORM>
        <NOTES>7 days dry hop for aroma</NOTES>
      </HOP>
    </HOPS>

    <YEASTS>
      <YEAST>
        <NAME>American Ale</NAME>
        <VERSION>1</VERSION>
        <TYPE>Ale</TYPE>
        <FORM>Liquid</FORM>
        <AMOUNT>0.100</AMOUNT>
        <LABORATORY>Wyeast Labs</LABORATORY>
        <PRODUCT_ID>1056</PRODUCT_ID>
        <NOTES>Very clean, crisp flavor accentuates hops. Ferments dry.</NOTES>
        <BEST_FOR>American Pale Ales, IPAs, Stouts</BEST_FOR>
      </YEAST>
    </YEASTS>

    <MISCS>
      <MISC>
        <NAME>Irish Moss</NAME>
        <VERSION>1</VERSION>
        <TYPE>Fining</TYPE>
        <USE>Boil</USE>
        <TIME>15</TIME>
        <AMOUNT>0.010</AMOUNT>
        <AMOUNT_IS_WEIGHT>TRUE</AMOUNT_IS_WEIGHT>
        <USE_FOR>Clarity</USE_FOR>
        <NOTES>Add at 15 minutes remaining in boil for improved clarity</NOTES>
      </MISC>
    </MISCS>
  </RECIPE>
</RECIPES>
"""

# Example 2: Extract Recipe
EXTRACT_PORTER = """<?xml version="1.0" encoding="ISO-8859-1"?>
<RECIPE>
  <NAME>Simple Extract Porter</NAME>
  <VERSION>1</VERSION>
  <TYPE>Extract</TYPE>
  <BREWER>Extract Brewer</BREWER>
  <BATCH_SIZE>18.93</BATCH_SIZE>
  <BOIL_SIZE>22.71</BOIL_SIZE>
  <BOIL_TIME>60</BOIL_TIME>
  <OG>1.052</OG>
  <FG>1.013</FG>
  <NOTES>An easy extract porter recipe perfect for beginners.</NOTES>

  <FERMENTABLES>
    <FERMENTABLE>
      <NAME>Light Malt Extract</NAME>
      <VERSION>1</VERSION>
      <TYPE>Extract</TYPE>
      <AMOUNT>2.7</AMOUNT>
      <YIELD>78.0</YIELD>
      <COLOR>8.0</COLOR>
      <NOTES>Light liquid malt extract</NOTES>
    </FERMENTABLE>
    <FERMENTABLE>
      <NAME>Chocolate Malt</NAME>
      <VERSION>1</VERSION>
      <TYPE>Grain</TYPE>
      <AMOUNT>0.227</AMOUNT>
      <YIELD>70.0</YIELD>
      <COLOR>350.0</COLOR>
      <NOTES>Steep for 30 minutes at 155F</NOTES>
    </FERMENTABLE>
  </FERMENTABLES>

  <HOPS>
    <HOP>
      <NAME>Willamette</NAME>
      <VERSION>1</VERSION>
      <ALPHA>4.5</ALPHA>
      <AMOUNT>0.028</AMOUNT>
      <USE>Boil</USE>
      <TIME>60</TIME>
      <FORM>Pellet</FORM>
    </HOP>
  </HOPS>

  <YEASTS>
    <YEAST>
      <NAME>English Ale</NAME>
      <VERSION>1</VERSION>
      <TYPE>Ale</TYPE>
      <FORM>Dry</FORM>
      <AMOUNT>0.011</AMOUNT>
      <AMOUNT_IS_WEIGHT>TRUE</AMOUNT_IS_WEIGHT>
      <NOTES>Classic English ale yeast</NOTES>
    </YEAST>
  </YEASTS>

  <MISCS></MISCS>
</RECIPE>
"""

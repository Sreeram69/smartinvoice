import re
from typing import Dict


def parse_spoken_item(text: str) -> Dict[str, str]:
    """
    Parses a spoken or raw input string into name, count, and price.
    Designed to be flexible with various spoken natural phrasing:
      - "boxes count 10 price 2500"
      - "add 5 chairs for 1200"
      - "item laptop count 2 price 75000"
      - "screws 100 price 500"
    """
    cleaned = text.strip()
    
    # Defaults
    name = ""
    count = "1"
    price = "0"
    
    # 1. Check for explicit "price" or "rupees" / "rs" / "amount" / "for" marker
    # e.g., "price 2500", "for 2500", "2500 rupees", "rs 2500"
    price_pattern = re.search(
        r'(?:price|amount|cost|rate|for|rs\.?|rupees|inr)\s*(?:is|of)?\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)',
        cleaned,
        re.IGNORECASE
    )
    if price_pattern:
        price = price_pattern.group(1)
        # remove the matched price part from string for subsequent parsing
        cleaned = cleaned[:price_pattern.start()] + " " + cleaned[price_pattern.end():]
    else:
        # Check for price at the very end as a number, e.g. "... 2500 rs" or "... 2500"
        trailing_num = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:rupees|rs\.?|inr)?\s*$', cleaned, re.IGNORECASE)
        if trailing_num:
            price = trailing_num.group(1)
            cleaned = cleaned[:trailing_num.start()]

    # 2. Check for explicit "count" or "qty" or "quantity" marker
    # e.g., "count 10", "qty 5", "quantity 20"
    count_pattern = re.search(
        r'(?:count|qty|quantity|nos|pieces|pcs)\s*(?:is|of)?\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?(?:\s*[a-zA-Z]+)?)',
        cleaned,
        re.IGNORECASE
    )
    if count_pattern:
        count = count_pattern.group(1).strip()
        cleaned = cleaned[:count_pattern.start()] + " " + cleaned[count_pattern.end():]
    else:
        # Check for leading number indicating count: "add 10 boxes", "10 boxes"
        leading_count = re.search(r'^(?:add\s+)?([0-9]+(?:\.[0-9]+)?)\s+([a-zA-Z\s]+)', cleaned, re.IGNORECASE)
        if leading_count:
            count = leading_count.group(1).strip()
            cleaned = leading_count.group(2)

    # 3. Clean up the remaining text as the item name
    # Remove leading filler words like "add", "item", "new"
    name = re.sub(r'^(?:add\s+|item\s+|new\s+)+', '', cleaned, flags=re.IGNORECASE).strip()
    # Remove leftover trailing punctuation or words like "for", "at", "price", "count"
    name = re.sub(r'\s+(?:for|at|with|price|count)\s*$', '', name, flags=re.IGNORECASE).strip()
    
    if not name:
        name = "Item"

    return {
        "name": name,
        "count": count,
        "price": price,
        "raw_text": text
    }

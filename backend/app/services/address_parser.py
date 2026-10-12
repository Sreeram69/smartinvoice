import re
from typing import Dict, Any, List, Optional, Tuple

# Known major cities and regions for instant high-confidence recognition
KNOWN_CITIES = {
    'DUBAI', 'ABU DHABI', 'SHARJAH', 'AJMAN', 'FUJAIRAH', 'RAS AL KHAIMAH', 'UMM AL QUWAIN',
    'KAKINADA', 'RAJAHMUNDRY', 'VISAKHAPATNAM', 'VIZAG', 'VIJAYAWADA', 'GUNTUR', 'TIRUPATI',
    'HYDERABAD', 'SECUNDERABAD', 'WARANGAL', 'BENGALURU', 'BANGALORE', 'CHENNAI', 'MUMBAI',
    'PUNE', 'KOLKATA', 'DELHI', 'NEW DELHI', 'AHMEDABAD', 'SURAT', 'JAIPUR', 'LUCKNOW',
    'KOCHI', 'COIMBATORE', 'MADURAI', 'CHANDIGARH', 'INDORE', 'BHOPAL', 'NAGPUR', 'PATNA',
    'COLLIERVILLE', 'NEW YORK', 'LOS ANGELES', 'CHICAGO', 'HOUSTON', 'DALLAS', 'LONDON',
    'SAN FRANCISCO', 'SEATTLE', 'BOSTON', 'AUSTIN', 'ATLANTA'
}

KNOWN_STATES_COUNTRIES = {
    'INDIA', 'UAE', 'U.A.E', 'UNITED ARAB EMIRATES', 'USA', 'U.S.A', 'UNITED STATES',
    'UK', 'U.K', 'UNITED KINGDOM', 'CANADA', 'AUSTRALIA', 'SINGAPORE', 'MALAYSIA',
    'ANDHRA PRADESH', 'AP', 'A.P.', 'TELANGANA', 'TS', 'T.S.', 'TAMIL NADU', 'TN',
    'KARNATAKA', 'MAHARASHTRA', 'KERALA', 'WEST BENGAL', 'WB', 'GUJARAT', 'RAJASTHAN',
    'UTTAR PRADESH', 'UP', 'DELHI', 'PUNJAB', 'HARYANA', 'TENNESSEE', 'NEW YORK', 'NY',
    'CALIFORNIA', 'CA', 'TEXAS', 'TX', 'FLORIDA', 'FL', 'WASHINGTON', 'WA', 'ILLINOIS', 'IL'
}

STREET_WORDS = re.compile(
    r'\b(?:plot|flat|door|d\.?no|h\.?no|fno|bldg|building|floor|suite|apt|apartment|'
    r'room|shop|blvd|boulevard|road|rd|street|st|lane|ave|avenue|cross|colony|col\b|'
    r'nagar|enclave|layout|tower|towers|heights|residency|complex|hospital|near|opp|'
    r'opposite|behind|beside|adjacent|sector|phase|block)\b',
    re.IGNORECASE,
)

STREET_NUMBER_PATTERN = re.compile(r'(?:\d+[-/]\d+|#\d+|\b\d+[A-Za-z]\b|\b\d{2,}\b)')
PHONE_PREFIX = re.compile(
    r'^\s*(?:phone|ph|tel|mobile|mob|cell|contact|call|whatsapp)(?:\s*no\.?)?[:\s.-]*',
    re.IGNORECASE
)
PHONE_INLINE_PATTERN = re.compile(
    r'(?:(?:\b(?:phone|ph|tel|mobile|mob|cell|contact|call|whatsapp)(?:\s*no\.?)?[:\s.-]*))?'
    r'(\+?\d[\d\s\-().]{8,15}\d)\b',
    re.IGNORECASE,
)
GSTIN_PATTERN = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b', re.IGNORECASE)
GSTIN_PREFIX_PATTERN = re.compile(r'(?:GSTIN|GST|TAX\s*ID|VAT|TRN)[:\s-]*([A-Z0-9\-]{8,20})', re.IGNORECASE)
PINCODE_PATTERN = re.compile(r'(?:PIN\s*(?:CODE)?[:\s.-]*)?([1-9]\d{5})(?!\d)', re.IGNORECASE)
ZIPCODE_PATTERN = re.compile(r'\b(\d{5}(?:-\d{4})?)\b')


def is_street_indicator(text: str) -> bool:
    """Returns True if the line strongly indicates a street, building, or address line rather than a city."""
    if STREET_WORDS.search(text):
        return True
    if re.search(r'\b\d+[-/]\d+\b', text) or '#' in text:
        return True
    return False


def extract_phone_from_line(line: str) -> Tuple[str, str]:
    """
    Extracts phone number from a line if present.
    Returns (phone, remaining_cleaned_line).
    """
    m = PHONE_INLINE_PATTERN.search(line)
    if not m:
        return "", line

    raw_phone_match = m.group(1).strip()
    digits_only = re.sub(r'\D', '', raw_phone_match)
    if len(digits_only) < 9 or len(digits_only) > 15:
        return "", line

    # Remove phone and any prefix from the line
    line_without_phone = (line[:m.start()] + line[m.end():]).strip(' :,.-')
    line_without_phone = PHONE_PREFIX.sub('', line_without_phone).strip(' :,.-')

    # Format phone cleanly: keep leading '+' if present
    clean_phone = raw_phone_match
    if line.strip().startswith('+') and not clean_phone.startswith('+'):
        clean_phone = '+' + clean_phone

    return clean_phone, line_without_phone


def extract_gstin_from_line(line: str) -> Tuple[str, str]:
    """
    Extracts GSTIN / Tax ID from a line.
    Returns (gstin, remaining_cleaned_line).
    """
    m = GSTIN_PATTERN.search(line)
    if m:
        gstin = m.group(0).upper()
        line_clean = (line[:m.start()] + line[m.end():]).strip(' :,.-')
        line_clean = re.sub(r'(?:GSTIN|GST|TAX\s*ID)[:\s-]*', '', line_clean, flags=re.I).strip(' :,.-')
        return gstin, line_clean

    m2 = GSTIN_PREFIX_PATTERN.search(line)
    if m2:
        gstin = m2.group(1).strip().upper()
        line_clean = (line[:m2.start()] + line[m2.end():]).strip(' :,.-')
        return gstin, line_clean

    return "", line


def extract_postal_code_from_line(line: str) -> Tuple[str, str]:
    """
    Extracts postal code (6-digit Indian PIN or 5-digit US ZIP).
    Returns (postal_code, remaining_cleaned_line).
    """
    # 1. 6-digit Indian PIN
    m = PINCODE_PATTERN.search(line)
    if m:
        pin = m.group(1)
        line_clean = (line[:m.start()] + line[m.end():]).strip(' :,.-')
        line_clean = re.sub(r'PIN\s*(?:CODE)?[:\s.-]*', '', line_clean, flags=re.I).strip(' :,.-')
        return pin, line_clean

    # 2. 5-digit US ZIP
    m2 = ZIPCODE_PATTERN.search(line)
    if m2:
        pin = m2.group(1)
        line_clean = (line[:m2.start()] + line[m2.end():]).strip(' :,.-')
        return pin, line_clean

    return "", line


def parse_single_address(lines: List[str], fallback_phone: str = "") -> Dict[str, Any]:
    """
    Parses a single party's address lines into:
    name, address_line_1, address_line_2, city, state, postal_code, phone, gstin.
    """
    clean_lines = [l.strip() for l in lines if l and l.strip()]
    if not clean_lines:
        return {
            "name": "",
            "address_line_1": "",
            "address_line_2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "phone": fallback_phone,
            "gstin": "",
        }

    phone = ""
    gstin = ""
    postal_code = ""

    # Phase 1: Scan and strip phone, GSTIN, and postal codes
    retained_lines: List[str] = []
    for l in clean_lines:
        # Extract phone
        p, rem = extract_phone_from_line(l)
        if p and not phone:
            phone = p
        l = rem

        # Extract GSTIN
        g, rem = extract_gstin_from_line(l)
        if g and not gstin:
            gstin = g
        l = rem

        # Extract PIN/ZIP
        pin, rem = extract_postal_code_from_line(l)
        if pin and not postal_code:
            postal_code = pin
        l = rem

        if l and re.search(r'[A-Za-z0-9]', l):
            retained_lines.append(l)

    if not phone and fallback_phone:
        phone = fallback_phone

    if not retained_lines:
        return {
            "name": clean_lines[0] if clean_lines else "",
            "address_line_1": "",
            "address_line_2": "",
            "city": "",
            "state": "",
            "postal_code": postal_code,
            "phone": phone,
            "gstin": gstin,
        }

    # Name is the first non-empty line
    name = retained_lines[0]
    loc_lines = retained_lines[1:]

    city = ""
    state = ""

    # Phase 2: Identify City and State from the bottom lines of loc_lines
    if loc_lines:
        last_line = loc_lines[-1]

        # Check if last line has clear comma/dash separation without street numbers
        if (',' in last_line or ' - ' in last_line) and not is_street_indicator(last_line):
            sep = ',' if ',' in last_line else ' - '
            parts = [p.strip() for p in last_line.split(sep) if p.strip()]
            if len(parts) >= 2:
                city = parts[0]
                state = parts[1]
                loc_lines.pop()
            elif len(parts) == 1:
                city = parts[0]
                loc_lines.pop()
        elif not is_street_indicator(last_line):
            # Check if last line is a single city/state word or matches known cities
            words = last_line.split()
            upper_last = last_line.upper().strip()

            if upper_last in KNOWN_CITIES:
                city = last_line
                loc_lines.pop()
            elif upper_last in KNOWN_STATES_COUNTRIES:
                state = last_line
                loc_lines.pop()
                # Check line above for city
                if loc_lines and not is_street_indicator(loc_lines[-1]):
                    city = loc_lines.pop()
            elif len(words) <= 3 and not any(ch.isdigit() for ch in last_line):
                # Likely a city line like "DUBAI" or "KAKINADA"
                city = last_line
                loc_lines.pop()

    # If city is still empty, scan loc_lines for known cities
    if not city and loc_lines:
        for idx in range(len(loc_lines) - 1, -1, -1):
            line_str = loc_lines[idx]
            for kc in KNOWN_CITIES:
                if re.search(rf'\b{re.escape(kc)}\b', line_str, re.IGNORECASE):
                    city = kc.title()
                    # If this line was JUST the city, remove it from loc_lines
                    if re.sub(rf'\b{re.escape(kc)}\b', '', line_str, flags=re.IGNORECASE).strip(' :,.-') == '':
                        loc_lines.pop(idx)
                    break
            if city:
                break

    # If state is still empty, scan loc_lines for known states / countries
    if not state and loc_lines:
        for idx in range(len(loc_lines) - 1, -1, -1):
            line_str = loc_lines[idx]
            for ks in KNOWN_STATES_COUNTRIES:
                if re.search(rf'\b{re.escape(ks)}\b', line_str, re.IGNORECASE):
                    state = ks
                    if re.sub(rf'\b{re.escape(ks)}\b', '', line_str, flags=re.IGNORECASE).strip(' :,.-') == '':
                        loc_lines.pop(idx)
                    break
            if state:
                break

    # If only 1 line after name, and it contains both street and city (e.g. "16-42-41/3, KAKINADA")
    if not city and len(loc_lines) == 1 and ',' in loc_lines[0]:
        parts = [p.strip() for p in loc_lines[0].split(',') if p.strip()]
        if len(parts) >= 2:
            if is_street_indicator(parts[0]) and not is_street_indicator(parts[1]):
                loc_lines[0] = parts[0]
                city = parts[1]

    # Clean extracted city / state from remaining loc_lines so street address isn't redundant
    if (city or state) and loc_lines:
        for i in range(len(loc_lines)):
            line = loc_lines[i]
            if state:
                line = re.sub(rf'(?:,\s*|\s*-\s*|\s+){re.escape(state)}\b', '', line, flags=re.I).strip(' :,.-')
            if city:
                line = re.sub(rf'(?:,\s*|\s*-\s*|\s+){re.escape(city)}\b', '', line, flags=re.I).strip(' :,.-')
            loc_lines[i] = line
        loc_lines = [l for l in loc_lines if l and re.search(r'[A-Za-z0-9]', l)]

    # Phase 3: Construct address_line_1 and address_line_2 from remaining loc_lines
    addr_1 = ""
    addr_2 = ""
    if len(loc_lines) == 1:
        addr_1 = loc_lines[0]
    elif len(loc_lines) == 2:
        addr_1 = loc_lines[0]
        addr_2 = loc_lines[1]
    elif len(loc_lines) > 2:
        addr_1 = loc_lines[0]
        addr_2 = ", ".join(loc_lines[1:])

    return {
        "name": name,
        "address_line_1": addr_1,
        "address_line_2": addr_2,
        "city": city,
        "state": state,
        "postal_code": postal_code,
        "phone": phone,
        "gstin": gstin,
    }


def parse_address_blocks(text: str) -> Dict[str, Any]:
    """
    Parses raw OCR text into sender (FROM) and customer (TO) address blocks.
    Identifies markers like:
      - 'TO', 'CONSIGNEE', 'CUSTOMER', 'SHIP TO', 'BILL TO', 'DELIVER TO'
      - 'FROM', 'CONSIGNOR', 'SENDER', 'BILLED FROM', 'SHIPPED FROM'
    Extracts phone numbers, postal codes, GSTIN, cities, states, and street addresses.
    """
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    raw_clean = "\n".join(raw_lines)

    # Keywords for section identification
    from_keywords = re.compile(
        r'^\s*[-*•#]?\s*(?:fr[o0]m|sender|consignor|supplier|shipped\s+fr[o0]m|billed\s+fr[o0]m|dispatched\s+fr[o0]m)\b[:\s,.-]*',
        re.IGNORECASE,
    )
    to_keywords = re.compile(
        r'^\s*[-*•#]?\s*(?:t[o0]\b|customer|consignee|ship(?:ped)?\s+t[o0]|bill(?:ed)?\s+t[o0]|deliver(?:ed)?\s+t[o0]|buyer|receiver|recipient)\b[:\s,.-]*',
        re.IGNORECASE,
    )

    from_lines: List[str] = []
    to_lines: List[str] = []
    preamble_lines: List[str] = []
    current_section: Optional[str] = None

    for line in raw_lines:
        if from_keywords.match(line):
            current_section = 'from'
            cleaned = from_keywords.sub('', line).strip(' :,-.;')
            if cleaned and re.search(r'[A-Za-z0-9]', cleaned):
                from_lines.append(cleaned)
            continue
        elif to_keywords.match(line):
            current_section = 'to'
            cleaned = to_keywords.sub('', line).strip(' :,-.;')
            if cleaned and re.search(r'[A-Za-z0-9]', cleaned):
                to_lines.append(cleaned)
            continue

        if current_section == 'from':
            from_lines.append(line)
        elif current_section == 'to':
            to_lines.append(line)
        else:
            preamble_lines.append(line)

    # If preamble lines exist before 'to' and no 'from' marker was found,
    # those preamble lines are the sender (e.g. letterhead at top of invoice)
    if preamble_lines and to_lines and not from_lines:
        from_lines = preamble_lines
        preamble_lines = []

    # If only preamble lines exist (no markers found at all):
    if not from_lines and not to_lines and preamble_lines:
        phone_matches = re.findall(PHONE_INLINE_PATTERN, raw_clean)
        valid_phones = [p for p in phone_matches if len(re.sub(r'\D', '', p)) >= 10]

        if len(valid_phones) >= 2 and len(preamble_lines) >= 4:
            # Two distinct phone numbers indicate two separate addresses
            midpoint = len(preamble_lines) // 2
            from_lines = preamble_lines[:midpoint]
            to_lines = preamble_lines[midpoint:]
        else:
            # Single address label uploaded => assign to customer (TO)
            to_lines = preamble_lines

    sender_dict = parse_single_address(from_lines)
    customer_dict = parse_single_address(to_lines)

    return {
        "sender": sender_dict,
        "customer": customer_dict,
        "raw_text": raw_clean,
        "requires_review": True,
    }

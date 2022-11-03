import re


def new_addr(addr: str|None):
    """
    Correct the spelling of a address if it's an address in the list of abbreviations of the university, keep the postal code if given, otherwise add "Kiel Germany" to the street.
    In that way addresses can be found despite spelling mistakes and abbreviations
    :param addr: the address to be parsed
    :return: a new address
    """

    street = ""
    replaced = False
    if addr:
        # look for the house number
        house_nr = re.search(r'(?<!\d)\d{1,4}(?!\d)', addr)
        house_nr = house_nr.group() if house_nr is not None else ""
        # look for the postal code
        code = re.search(r'\d{5}\s\w+', addr)
        code = code.group() if code is not None else None

        # if the old address contains specific letters, we know the street
        if re.search('ABG| Garten |m Botan', addr, re.IGNORECASE):
            street = 'Am Botanischen Garten '
            replaced = True
        elif re.search('AHS|Arnold|Heller', addr, re.IGNORECASE):
            street = 'Arnold-Heller-Straße '
            replaced = True
        elif re.search(r'^BK[0-9]+|^BK\s|Bremer|skamp', addr, re.IGNORECASE):
            street = 'Bremerskamp '
            replaced = True
        elif re.search('GBS|Gute|tenberg', addr, re.IGNORECASE):
            street = 'Gutenbergstraße '
            replaced = True
        elif re.search('SBS|schau|hauenburge', addr, re.IGNORECASE):
            street = 'Schauenburger Straße '
            replaced = True
        elif re.search(r'^BS[0-9]+|^BS\s|Bos', addr, re.IGNORECASE):
            street = 'Boschstraße '
            replaced = True
        elif re.search(r'^BW[0-9]+|^BW\s', addr, re.IGNORECASE):
            street = 'Breiter Weg '
            replaced = True
        elif re.search(r'^BWS[0-9]+|^BWS\s|swiker|Brunsw', addr, re.IGNORECASE):
            street = 'Brunswiker Straße '
            replaced = True
        elif re.search('CAP|Christia|ian|Albr', addr, re.IGNORECASE):
            street = 'Christian-Albrechts-Platz '
            replaced = True
        elif re.search(r'^DW[0-9]+|^DW\s|stern|broo', addr, re.IGNORECASE):
            street = 'Düsternbrooker Weg '
            replaced = True
        elif re.search(r'^FS[0-9]+|^FS\s|flec', addr, re.IGNORECASE):
            street = 'Fleckenstraße '
            replaced = True
        elif re.search(r'^GW[0-9]+|^GW\s', addr, re.IGNORECASE):
            street = 'Grasweg '
            replaced = True
        elif re.search('HHP|Heinr|hecht|rich-H', addr, re.IGNORECASE):
            street = 'Heinrich-Hecht-Platz '
            replaced = True
        elif re.search(r'^HRS[0-9]+|^HRS\s|wald-|rode|hermann-R', addr, re.IGNORECASE):
            street = 'Hermann-Rodewald-Straße '
            replaced = True
        elif re.search(r'^HS[0-9]+|^HS\s|Hospi', addr, re.IGNORECASE):
            street = 'Hospitalstraße '
            replaced = True
        elif re.search('HWS|Hege|gewi', addr, re.IGNORECASE):
            street = 'Hegewischstraße '
            replaced = True
        elif re.search('JMS|hanna|storf', addr, re.IGNORECASE):
            street = 'Johanna-Mestorf-Straße '
            replaced = True
        elif re.search('KGP|grot', addr, re.IGNORECASE):
            street = 'Klaus-Groth-Platz '
            replaced = True
        elif re.search(r'^KL[0-9]+|^KL\s|Kiell', addr, re.IGNORECASE):
            street = 'Kiellinie '
            replaced = True
        elif re.search('KOS|kobol|boldst', addr, re.IGNORECASE):
            street = 'Koboldstraße '
            replaced = True
        elif re.search(r'^KS[0-9]+|^KS\s|Kai|Ka[is]{2}erstr', addr, re.IGNORECASE):
            street = 'Kaiserstraße '
            replaced = True
        elif re.search(r'^LEG[0-9]+|^LEG\s|Kai', addr, re.IGNORECASE):
            street = 'Legienstraße '
            replaced = True
        elif re.search(r'^LMS[0-9]+|^LMS\s|lude|meyn', addr, re.IGNORECASE):
            street = 'Ludewig-Meyn-Straße '
            replaced = True
        elif re.search(r'^LS[0-9]+|^LS\s|Leibni|niz', addr, re.IGNORECASE):
            street = 'Leibnizstraße '
            replaced = True
        elif re.search(r'^MES[0-9]+|^MES\s|Max-E|eyt', addr, re.IGNORECASE):
            street = 'Max-Eyth-Straße '
            replaced = True
        elif re.search(r'^MS[0-9]+|^MS\s|Micha|eliss', addr, re.IGNORECASE):
            street = 'Michaelisstraße '
            replaced = True
        elif re.search('NFS|neuf|ufeld', addr, re.IGNORECASE):
            street = 'Neufeldtstraße '
            replaced = True
        elif re.search(r'^NW[0-9]+|^NW\s|niem|annsw', addr, re.IGNORECASE):
            street = 'Niemannsweg '
            replaced = True
        elif re.search('OHP|Otto-H|hahn', addr, re.IGNORECASE):
            street = 'Otto-Hahn-Platz '
            replaced = True
        elif re.search(r'^OS[0-9]+|^OS\s|olsh|ausen', addr, re.IGNORECASE):
            street = 'Olshausenstraße '
            replaced = True
        elif re.search(r'^PS[0-9]+|^PS\s|preu|ausen', addr, re.IGNORECASE):
            street = 'Preußerstraße '
            replaced = True
        elif re.search('RFS|rosa|anklin|Schittenhelm', addr, re.IGNORECASE):
            street = 'Rosalind-Franklin-Straße '
            replaced = True
        elif re.search('RHS|rudol.+-H|höb', addr, re.IGNORECASE):
            street = 'Rudolf-Höber-Straße '
            replaced = True
        elif re.search(r'^SW[0-9]+|^SW\s|schwan', addr, re.IGNORECASE):
            street = 'Schwanenweg '
            replaced = True
        elif re.search('WHS|hhofs', addr, re.IGNORECASE):
            street = 'Wischhofstraße '
            replaced = True
        elif re.search(r'^WR[0-9]+|^WR\s|Westring', addr, re.IGNORECASE):
            street = 'Westring '
            replaced = True
        elif re.search(r'^WS[0-9]+|^WS\s|marer|weimarer', addr, re.IGNORECASE):
            street = 'Weimarer Straße '
            replaced = True
        elif re.search(r'WSP|seel|elig|Wilhelm-Se', addr, re.IGNORECASE):
            street = 'Wilhelm-Seelig-Platz '
            replaced = True

        # replace periods with a space
        addr = addr.replace(".", " ")

        # if we found a street reformat the address
        if replaced and code is not None:
            addr = street + house_nr + " " + code
        elif replaced and code is None:
            addr = street + house_nr + " Kiel Germany"
        # if we couldn't find a street in the list but we have a postal code, get the street name 
        # and add the postal code
        elif not replaced and code is not None:
            # if the address start with a postal code, just return the old address
            if addr.startswith(code):
                return addr
            address = re.split(r'\(|,', addr)
            addr = address[0] + " " + code
        else:
            # get the street name and add the string "Kiel Germany"
            address = re.split(r'\(|,', addr)
            addr = address[0] + " Kiel Germany"
        # delete multiple spaces
        addr = re.sub(r'\s+', " ", addr)
        # delete spaces at the start and end of the address
        addr.strip()
    return addr



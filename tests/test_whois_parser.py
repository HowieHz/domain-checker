import datetime

import pytest

from src.utils.defined_types import Err, Ok, ParsedWhoisData
from src.utils.whois_parser import whois_parser

raw_whois_a = (
    "\r\n"
    + "    Domain name:\r\n"
    + "        blahaj.uk\r\n"
    + "\r\n"
    + "    Data validation:\r\n"
    + "        Nominet was not able to match the registrant's name and/or address against a 3rd party source on 15-Feb-2024\r\n"
    + "\r\n"
    + "    Registrar:\r\n"
    + "        Cloudflare, Inc. [Tag = CLOUDFLARE]\r\n"
    + "        URL: https://cloudflare.com\r\n"
    + "\r\n"
    + "    Relevant dates:\r\n"
    + "        Registered on: 12-Feb-2024\r\n"
    + "        Expiry date:  12-Feb-2026\r\n"
    + "        Last updated:  13-Jan-2025\r\n"
    + "\r\n"
    + "    Registration status:\r\n"
    + "        Registered until expiry date.\r\n"
    + "\r\n"
    + "    Name servers:\r\n"
    + "        amanda.ns.cloudflare.com\r\n"
    + "        nero.ns.cloudflare.com\r\n"
    + "\r\n"
    + "    WHOIS lookup made at 19:22:36 02-Feb-2025\r\n"
    + "\r\n"
    + "-- \r\n"
    + "This WHOIS information is provided for free by Nominet UK the central registry\r\n"
    + "for .uk domain names. This information and the .uk WHOIS are:\r\n"
    + "\r\n"
    + "    Copyright Nominet UK 1996 - 2025.\r\n"
    + "\r\n"
    + "You may not access the .uk WHOIS or use any data from it except as permitted\r\n"
    + "by the terms of use available in full at https://www.nominet.uk/whoisterms,\r\n"
    + "which includes restrictions on: (A) use of the data for advertising, or its\r\n"
    + "repackaging, recompilation, redistribution or reuse (B) obscuring, removing\r\n"
    + "or hiding any or all of this notice and (C) exceeding query rate or volume\r\n"
    + "limits. The data is provided on an 'as-is' basis and may lag behind the\r\n"
    + "register. Access may be withdrawn or restricted at any time. \r\n"
)
raw_whois_b = (
    "%%\n"
    + "%% This is the AFNIC Whois server.\n"
    + "%%\n"
    + "%% complete date format: YYYY-MM-DDThh:mm:ssZ\n"
    + "%%\n"
    + "%% Rights restricted by copyright.\n"
    + "%% See "
    + "https://www.afnic.fr/en/domain-names-and-support/everything-there-is-to-know-about-domain-names/find-a-domain-name-or-a-holder-using-whois/\n"
    + "%%\n"
    + "%%\n"
    + "\n"
    + "domain:                        barku.re\r\n"
    + "status:                        ACTIVE\r\n"
    + "eppstatus:                     active\r\n"
    + "hold:                          NO\r\n"
    + "holder-c:                      ANO00-FRNIC\r\n"
    + "admin-c:                       ANO00-FRNIC\r\n"
    + "tech-c:                        TRS360-FRNIC\r\n"
    + "registrar:                     TLD Registrar Solutions Ltd\r\n"
    + "Expiry Date:                   2025-08-12T07:35:59Z\r\n"
    + "created:                       2022-08-12T07:35:59Z\r\n"
    + "last-update:                   2024-08-06T06:05:17.862263Z\r\n"
    + "source:                        FRNIC\r\n"
    + "\r\n"
    + "nserver:                       alex.ns.cloudflare.com\r\n"
    + "nserver:                       rihana.ns.cloudflare.com\r\n"
    + "source:                        FRNIC\r\n"
    + "\r\n"
    + "registrar:                     TLD Registrar Solutions Ltd\r\n"
    + "address:                       35-39 Moorgate\r\n"
    + "address:                       Level 1\r\n"
    + "address:                       EC2R 6AR London\r\n"
    + "country:                       GB\r\n"
    + "phone:                         +44.2034357304\r\n"
    + "e-mail:                        admin@tldregistrarsolutions.com\r\n"
    + "website:                       https://internetbs.net/en/domain-name-registrations/price.html?setCurrency=EUR\r\n"
    + "anonymous:                     No\r\n"
    + "registered:                    2014-11-17T00:00:00Z\r\n"
    + "source:                        FRNIC\r\n"
    + "\r\n"
    + "nic-hdl:                       TRS360-FRNIC\r\n"
    + "type:                          ORGANIZATION\r\n"
    + "contact:                       TLD Registrar Solutions\r\n"
    + "address:                       TLD Registrar Solutions\r\n"
    + "address:                       Saddlers House 44 Gutter Lane\r\n"
    + "address:                       EC2V 6BR London\r\n"
    + "country:                       GB\r\n"
    + "phone:                         +44.2033880600\r\n"
    + "e-mail:                        abuse@tldregistrarsolutions.com\r\n"
    + "registrar:                     TLD Registrar Solutions Ltd\r\n"
    + "changed:                       2025-01-14T09:46:43.85526Z\r\n"
    + "anonymous:                     NO\r\n"
    + "obsoleted:                     NO\r\n"
    + "eppstatus:                     associated\r\n"
    + "eppstatus:                     active\r\n"
    + "eligstatus:                    not identified\r\n"
    + "reachstatus:                   not identified\r\n"
    + "source:                        FRNIC\r\n"
    + "\r\n"
    + "nic-hdl:                       ANO00-FRNIC\r\n"
    + "type:                          PERSON\r\n"
    + "contact:                       Ano Nymous\r\n"
    + "registrar:                     TLD Registrar Solutions Ltd\r\n"
    + "changed:                       2024-09-01T04:24:19.307272Z\r\n"
    + "anonymous:                     YES\r\n"
    + "remarks:                       -------------- WARNING --------------\r\n"
    + "remarks:                       While the registrar knows him/her,\r\n"
    + "remarks:                       this person chose to restrict access\r\n"
    + "remarks:                       to his/her personal data. So PLEASE,\r\n"
    + "remarks:                       don't send emails to Ano Nymous. This\r\n"
    + "remarks:                       address is bogus and there is no hope\r\n"
    + "remarks:                       of a reply.\r\n"
    + "remarks:                       -------------- WARNING --------------\r\n"
    + "obsoleted:                     NO\r\n"
    + "eppstatus:                     associated\r\n"
    + "eppstatus:                     active\r\n"
    + "eligstatus:                    not identified\r\n"
    + "reachstatus:                   not identified\r\n"
    + "source:                        FRNIC\r\n"
    + "\n"
    + ">>> Last update of WHOIS database: 2025-02-02T19:22:37.934827Z <<<\n"
    + "\r\n"
)


@pytest.mark.parametrize(
    "raw_whois, status, domain, registry_expiry_date",
    [
        (
            raw_whois_a,
            "registered",
            "blahaj.uk",
            datetime.datetime(2026, 2, 12, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            raw_whois_b,
            "registered",
            "barku.re",
            datetime.datetime(2025, 8, 12, 7, 35, 59, tzinfo=datetime.timezone.utc),
        ),
    ],
)
def test_whois_parser(raw_whois, status, domain, registry_expiry_date):
    parsed_whois_data: ParsedWhoisData = whois_parser(raw_whois)
    assert parsed_whois_data["status"][1] == status
    assert parsed_whois_data["domain"] == ""
    assert parsed_whois_data["raw"] == raw_whois
    assert parsed_whois_data["registry_expiry_date"].value == registry_expiry_date

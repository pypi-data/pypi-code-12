
import regex

ALPHA_RE = r'(\p{L})'

DIGIT_RE = r'[0-9]'

HEXDIG_RE = r'[0-9a-fA-F]'

'''
   pct-encoded   = "%" HEXDIG HEXDIG
'''
PCT_ENCODED_RE = r'(%{hexdig}{hexdig})'.format(hexdig=HEXDIG_RE)

'''
   unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
'''
UNRESERVED_RE = r'({alpha}|{digit}|-|\.|_|~)'.format(
    alpha=ALPHA_RE,
    digit=DIGIT_RE
    )

'''
   gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
'''
GEN_DELIMS_RE = r'[\:/\?\#\[\]@]'
'''
   sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
                 / "*" / "+" / "," / ";" / "="
'''
SUB_DELIMS_RE = r"[\!$&'()*+,;=]"

'''
   reserved      = gen-delims / sub-delims
'''
RESERVED_RE = r'({gen_delims}|{sub_delims})'.format(
    gen_delims=GEN_DELIMS_RE,
    sub_delims=SUB_DELIMS_RE
    )

'''
   pchar         = unreserved / pct-encoded / sub-delims / ":" / "@"
'''
PCHAR_RE = r'({unreserved}|{pct_encoded}|{sub_delims}|\:\@)'.format(
    unreserved=UNRESERVED_RE,
    pct_encoded=PCT_ENCODED_RE,
    sub_delims=SUB_DELIMS_RE
    )

'''
   query         = *( pchar / "/" / "?" )
'''
QUERY_RE = r'(({pchar}|\/|\?)*)'.format(pchar=PCHAR_RE)

'''
   fragment      = *( pchar / "/" / "?" )
'''
FRAGMENT_RE = r'(({pchar}|\/|\?)*)'.format(pchar=PCHAR_RE)

'''
   segment       = *pchar
'''
SEGMENT_RE = r'({pchar})*'.format(pchar=PCHAR_RE)

'''
   segment-nz    = 1*pchar
'''
SEGMENT_NZ_RE = r'(({pchar}){{1}})'.format(pchar=PCHAR_RE)

'''
   segment-nz-nc = 1*( unreserved / pct-encoded / sub-delims / "@" )
                 ; non-zero-length segment without any colon ":"
'''
SEGMENT_NZ_NC_RE = r'(({unreserved}|{pct_encoded}|{sub_delims}|@){{1}})'.format(
    unreserved=UNRESERVED_RE,
    pct_encoded=PCT_ENCODED_RE,
    sub_delims=SUB_DELIMS_RE
    )

'''
   path-abempty  = *( "/" segment )
'''
PATH_ABEMPTY_RE = r'(\/{segment})*'.format(segment=SEGMENT_RE)

'''
   path-absolute = "/" [ segment-nz *( "/" segment ) ]
'''
PATH_ABSOLUTE_RE = r'(\/({segment_nz}(\/{segment})*)?)'.format(
    segment_nz=SEGMENT_NZ_RE,
    segment=SEGMENT_RE
    )

'''
   path-noscheme = segment-nz-nc *( "/" segment )
'''
PATH_NOSCHEME_RE = r'({segment_nz_nc}(\/{segment})*)'.format(
    segment_nz_nc=SEGMENT_NZ_NC_RE,
    segment=SEGMENT_RE
    )

'''
   path-rootless = segment-nz *( "/" segment )
'''
PATH_ROOTLESS_RE = r'({segment_nz}(\/{segment})*)'.format(
    segment_nz=SEGMENT_NZ_RE,
    segment=SEGMENT_RE
    )

'''
   path-empty    = 0<pchar>
'''
PATH_EMPTY_RE = r'{pchar}{{0}}'.format(pchar=PCHAR_RE)

'''
   path          = path-abempty    ; begins with "/" or is empty
                 / path-absolute   ; begins with "/" but not "//"
                 / path-noscheme   ; begins with a non-colon segment
                 / path-rootless   ; begins with a segment
                 / path-empty      ; zero characters
'''
PATH_RE = (r'({path_abempty}|{path_absolute}|'
           r'{path_noscheme}|{path_rootless}|{path_empty})').format(
    path_abempty=PATH_ABEMPTY_RE,
    path_absolute=PATH_ABSOLUTE_RE,
    path_noscheme=PATH_NOSCHEME_RE,
    path_rootless=PATH_ROOTLESS_RE,
    path_empty=PATH_EMPTY_RE
    )

'''
   reg-name      = *( unreserved / pct-encoded / sub-delims )
'''
REG_NAME_RE = r'(({unreserved}|{pct_encoded}|{sub_delims})*)'.format(
    unreserved=UNRESERVED_RE,
    pct_encoded=PCT_ENCODED_RE,
    sub_delims=SUB_DELIMS_RE
    )

'''
   dec-octet     = DIGIT                 ; 0-9
                 / %x31-39 DIGIT         ; 10-99
                 / "1" 2DIGIT            ; 100-199
                 / "2" %x30-34 DIGIT     ; 200-249
                 / "25" %x30-35          ; 250-255
'''
DEC_OCTET_RE = (r'({digit}|([1-9]{digit})'
                r'|(1{digit}{{2}})|(2[0-4]{digit})|(25[05]))').format(
    digit=DIGIT_RE
    )

'''
   IPv4address   = dec-octet "." dec-octet "." dec-octet "." dec-octet
'''
IPV4ADDRESS_RE = r'({dec_octet}\.{dec_octet}\.{dec_octet}\.{dec_octet})'.format(
    dec_octet=DEC_OCTET_RE
    )

'''
   h16           = 1*4HEXDIG
'''
H16_RE = r'{hexdig}{{1:4}}'.format(hexdig=HEXDIG_RE)

'''
   ls32          = ( h16 ":" h16 ) / IPv4address
'''
LS32_RE = r'(({h16}\:{h16})|{ipv4address})'.format(
    h16=H16_RE,
    ipv4address=IPV4ADDRESS_RE
    )

'''
   IPv6address   =                            6( h16 ":" ) ls32
                 /                       "::" 5( h16 ":" ) ls32
                 / [               h16 ] "::" 4( h16 ":" ) ls32
                 / [ *1( h16 ":" ) h16 ] "::" 3( h16 ":" ) ls32
                 / [ *2( h16 ":" ) h16 ] "::" 2( h16 ":" ) ls32
                 / [ *3( h16 ":" ) h16 ] "::"    h16 ":"   ls32
                 / [ *4( h16 ":" ) h16 ] "::"              ls32
                 / [ *5( h16 ":" ) h16 ] "::"              h16
                 / [ *6( h16 ":" ) h16 ] "::"
'''
IPV6ADDRESS_RE = (
    r'('
    r'({h16}\:){{6}}{ls32}'
    r'\:\:({h16}\:){{5}}{ls32}'
    r'({h16})?\:\:({h16}\:){{4}}{ls32}'
    r'(({h16}\:){{1}}{h16})?\:\:({h16}\:){{3}}{ls32}'
    r'(({h16}\:){{2}}{h16})?\:\:({h16}\:){{2}}{ls32}'
    r'(({h16}\:){{3}}{h16})?\:\:({h16}\:){{1}}{ls32}'
    r'(({h16}\:){{4}}{h16})?\:\:({h16}\:){{0}}{ls32}'
    r'(({h16}\:){{5}}{h16})?\:\:({h16}\:){{0}}{ls32}'
    r'(({h16}\:){{6}}{h16})?\:\:({h16}\:){{0}}{ls32}'
    r')'
    ).format(
        h16=H16_RE,
        ls32=LS32_RE
        )

'''
   IPvFuture     = "v" 1*HEXDIG "." 1*( unreserved / sub-delims / ":" )
'''
IPVFUTURE_RE = r'(v{hexdig}{{1}}\.({unreserved}|{sub_delims}|\:){{1}})'.format(
    hexdig=HEXDIG_RE,
    unreserved=UNRESERVED_RE,
    sub_delims=SUB_DELIMS_RE
    )

'''
   IP-literal    = "[" ( IPv6address / IPvFuture  ) "]"
'''
IP_LITERAL_RE = r'(({ipv6address}|{ipvfuture}))?'.format(
    ipv6address=IPV6ADDRESS_RE,
    ipvfuture=IPVFUTURE_RE
    )

'''
   scheme        = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
'''
SCHEME_RE = r'({alpha}({alpha}|{digit}|\+|\-|\.)*)'.format(
    alpha=ALPHA_RE,
    digit=DIGIT_RE
    )

'''
   userinfo      = *( unreserved / pct-encoded / sub-delims / ":" )
'''
USERINFO_RE = r'(({unreserved}|{pct_encoded}|{sub_delims}|\:)*)'.format(
    unreserved=UNRESERVED_RE,
    pct_encoded=PCT_ENCODED_RE,
    sub_delims=SUB_DELIMS_RE
    )

'''
   host          = IP-literal / IPv4address / reg-name
'''
HOST_RE = r'({ip_literal}|{ipv4address}|{reg_name})'.format(
    ip_literal=IP_LITERAL_RE,
    ipv4address=IPV4ADDRESS_RE,
    reg_name=REG_NAME_RE
)

'''
   port          = *DIGIT
'''
PORT_RE = r'{digit}*'.format(digit=DIGIT_RE)

'''
   authority     = [ userinfo "@" ] host [ ":" port ]
'''
AUTHORITY_RE = r'(({userinfo}\@)?{host}(\:{port})?)'.format(
    userinfo=USERINFO_RE,
    host=HOST_RE,
    port=PORT_RE
    )

'''
   relative-part = "//" authority path-abempty
                 / path-absolute
                 / path-noscheme
                 / path-empty
'''
RELATIVE_PART_RE = (
    r'((\/\/{authority}{path_abempty})|'
    r'{path_absolute}|{path_noscheme}|{path_empty})'
    ).format(
        authority=AUTHORITY_RE,
        path_abempty=PATH_ABEMPTY_RE,
        path_absolute=PATH_ABSOLUTE_RE,
        path_noscheme=PATH_NOSCHEME_RE,
        path_empty=PATH_EMPTY_RE
        )

'''
   relative-ref  = relative-part [ "?" query ] [ "#" fragment ]
'''
RELATIVE_REF_RE = r'({relative_part}(\?{query})?(\#{fragment})?)'.format(
    relative_part=RELATIVE_PART_RE,
    query=QUERY_RE,
    fragment=FRAGMENT_RE
    )

'''
   hier-part     = "//" authority path-abempty
                 / path-absolute
                 / path-rootless
                 / path-empty
'''
HIER_PART_RE = (
    r'((\/\/{authority}{path_abempty})|'
    r'{path_absolute}|{path_rootless}|{path_empty})'
    ).format(
        authority=AUTHORITY_RE,
        path_abempty=PATH_ABEMPTY_RE,
        path_absolute=PATH_ABSOLUTE_RE,
        path_rootless=PATH_ROOTLESS_RE,
        path_empty=PATH_EMPTY_RE
        )

'''
   URI           = scheme ":" hier-part [ "?" query ] [ "#" fragment ]
'''
URI_RE = r'({scheme}\:{hier_part}(\?{query})?(\#{fragment})?)'.format(
    scheme=SCHEME_RE,
    hier_part=HIER_PART_RE,
    query=QUERY_RE,
    fragment=FRAGMENT_RE
    )

'''
   URI-reference = URI / relative-ref
'''
URI_REFERENCE_RE = r'({uri}|{relative_ref})'.format(
    uri=URI_RE,
    relative_ref=RELATIVE_REF_RE
    )

'''
   absolute-URI  = scheme ":" hier-part [ "?" query ]
'''
ABSOLUTE_URI_RE = r'({scheme}\:{hier_part}(\?{query})?)'.format(
    scheme=SCHEME_RE,
    hier_part=HIER_PART_RE,
    query=QUERY_RE
    )

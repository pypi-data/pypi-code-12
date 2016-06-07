from kitty.model import *


def CString(name, value):
    return Container(
        name=name,
        fields=[
            String(name=name, value=value),
            Static(name=name + '_term', value='\x00')
        ]
    )


def DomainString(name, value):
    parts = value.split('.')
    part_list = []
    for i in range(len(parts)):
        part = String(name='%s_part%d' % (name, i), value=parts[i])
        lpart = SizeInBytes(name='%s_part%d_len' % (name, i), sized_field=part, length=8)
        part_list.append(lpart)
        part_list.append(part)
    part_list.append(U8(name='%s_parts_term' % name, value=0))
    return Container(name=name, fields=[
        SizeInBytes(name='%s_len' % name, sized_field='%s_parts' % name, length=16),
        Container(name='%s_parts' % name, fields=part_list)
    ])


def DnsRecord(name, name_val, type_val, class_val, ttl_val, resource_string):
    return Container(
        name=name,
        fields=[
            BE16(name='name', value=name_val),
            BE16(name='type', value=type_val),  # CNAME
            BE16(name='class', value=class_val),  # IN
            BE32(name='ttl', value=ttl_val),
            DomainString(name='resource', value=resource_string),
        ]
    )

standard_query_response = Template(
    name='standard_query_response',
    fields=[
        Dynamic(name='transaction_id', key='transaction_id', default_value='12'),
        Container(
            name='header',
            fields=[
                BE16(name='flags', value=0x8180),
                ElementCount(name='questions', depends_on='queries', length=16),
                ElementCount(name='answer_rrs', depends_on='answers', length=16),
                ElementCount(name='authority_rrs', depends_on='authoritatives_nameservers', length=16),
                ElementCount(name='additional_rrs', depends_on='addtional_records', length=16),
            ]),
        Container(
            name='queries',
            fields=[
                Container(
                    fields=[
                        DomainString(name='name', value='checkip.dyndns.org'),
                        LE16(name='type', value=0x1),
                        LE16(name='class', value=0x1),
                    ]),
            ]),
        Container(
            name='answers',
            fields=[
                DnsRecord('answer1', 0xc00c, 0x5, 0x1, 0x115, 'checkip.dyndns.com')
            ]),
        Container(
            name='authoritatives_nameservers',
            fields=[
                DnsRecord('auth1', 0xc038, 0x2, 0x1, 0x56f0, 'ns2.powweb.com')
            ]),
        Container(
            name='addtional_records',
            fields=[
                Container(
                    fields=[]),
            ])
    ]
)

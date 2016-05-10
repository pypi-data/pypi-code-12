# if __name__ == '__main__':
#     r = Rule('/example/<int:test>/<int:test2>', methods=['GET', 'POST'])
#     print r.base_rule
#     print r.rule_re
#     print r.type_variable
#     print r.dynamic
#     print r.match_order
#     print r.methods
#     print '======================='
#
#     r1 = Rule('/example/haha')
#     print r1.base_rule
#     print r1.rule_re
#     print r1.dynamic
#     print r1.match_order
#     print r1.methods
#     print '======================='
#
#     r2 = Rule('/example/<heihei>')
#     print r2.base_rule
#     print r2.rule_re
#     print r2.type_variable
#     print r2.match_order
#     print '======================='
#
#     s = '/example/<int:wocao>/test'
#     r3 = Rule(s)
#     print r3.base_rule
#     print r3.rule_re
#     print r3.dynamic
#     print r3.type_variable
#     print r3.match_order
#     print '======================='

# In Rule class
# def compile_rule(self, rule):
#     """Make the url rule to a Regular Expression"""
#     if not rule.startswith('^'):
#         if rule.startswith('/'):
#             rule = '^' + rule
#         else:
#             rule = '^/' + rule
#     if not rule.endswith('$'):
#         rule += '$'
#
#     # handling like "/<int:id>" url string
#     if '(?P<' not in rule and _rule_re.search(rule):
#         rule = _rule_re.sub(self._replace_rule, rule)
#     return rule
#
# def _replace_rule(self, match):
#     """ /<int:id>  -->  r'(?P<id>\d+)' """
#     group = match.groupdict()
#     _type = group.get('type')
#     _type_replace = _type_map.get(_type, '[^/]+')
#     _variable = group.get('variable')
#     return r'(?P<{variable}>{type_replace})'.format(
#         variable=_variable, type_replace=_type_replace
#     )





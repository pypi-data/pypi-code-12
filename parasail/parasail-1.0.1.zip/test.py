import parasail

print 'parasail.sw_table("asdf","asdfasdf",10,1,parasail.blosum62)'
result = parasail.sw_table("asdf","asdfasdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length
print result.score_table

print 'parasail.sw_stats_table("asdf","asdfasdf",10,1,parasail.blosum62)'
result = parasail.sw_stats_table("asdf","asdfasdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length
print result.score_table
print result.matches_table
print result.similar_table
print result.length_table

print 'parasail.sw_rowcol("asdf","asdfasdf",10,1,parasail.blosum62)'
result = parasail.sw_rowcol("asdf","asdfasdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length
print result.score_row
print result.score_col

print 'parasail.sw_stats_rowcol("asdf","asdfasdf",10,1,parasail.blosum62)'
result = parasail.sw_stats_rowcol("asdf","asdfasdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length
print result.score_row
print result.score_col
print result.matches_row
print result.matches_col
print result.similar_row
print result.similar_col
print result.length_row
print result.length_col

print 'parasail.sw("asdf","asdf",10,1,parasail.blosum62)'
result = parasail.sw("asdf","asdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length
print result.score_table

print 'parasail.sw_stats("asdf","asdf",10,1,parasail.blosum62)'
result = parasail.sw_stats("asdf","asdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length

print 'parasail.sw_scan_32("asdf","asdf",10,1,parasail.blosum62)'
result = parasail.sw_scan_32("asdf","asdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length

print 'parasail.sw_scan_16("asdf","asdf",10,1,parasail.blosum62)'
result = parasail.sw_scan_16("asdf","asdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length

print 'parasail.sw_stats_striped_16("asdf","asdf",10,1,parasail.blosum62)'
result = parasail.sw_stats_striped_16("asdf","asdf",10,1,parasail.blosum62)
print result
print result.saturated
print result.score
print result.matches
print result.similar
print result.length

print parasail.blosum62.name
print parasail.blosum62.size
print parasail.blosum62.matrix

print 'parasail.profile_create_8("asdf", parasail.blosum62)'
profile = parasail.profile_create_8("asdf", parasail.blosum62)
print 'parasail.profile_create_8("asdf", parasail.blosum62)'
profile = parasail.profile_create_8("asdf", parasail.blosum62)
print profile
print profile.s1
print profile.matrix

print 'parasail.sw_striped_profile_8(profile,"asdf",10,1)'
result = parasail.sw_striped_profile_8(profile,"asdf",10,1)
print result
print result.saturated
print result.score

print 'parasail.profile_create_sat("asdf", parasail.blosum62)'
profile = parasail.profile_create_sat("asdf", parasail.blosum62)
print profile
print profile.s1
print profile.matrix
print dir(profile.matrix)
print profile.matrix.min
print profile.matrix.max
print profile.matrix.size

print 'parasail.sw_striped_profile_sat(profile,"asdf",10,1)'
result = parasail.sw_striped_profile_sat(profile,"asdf",10,1)
print result
print result.saturated
print result.score
print type(result.score)


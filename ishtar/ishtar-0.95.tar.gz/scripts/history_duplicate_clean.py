"""
Clean duplicate in history.
This should be unecessary now.
"""

import datetime
from archaeological_operations.models import Operation, AdministrativeAct
from archaeological_files.models import File
from archaeological_context_records.models import ContextRecord
from archaeological_finds.models import Find, BaseFind, Treatment

nb_deleted = {}
to_delete = []
for model in [Operation, File, ContextRecord, AdministrativeAct, Find,
              BaseFind, Treatment]:
    nb_deleted[model.__name__] = 0
    for item in model.objects.all()[0:]:
        c_user, c_date = None, None
        for h in item.history.order_by('-history_modifier_id', '-history_date',
                                       '-history_id').all():
            if c_user and c_date and h.history_modifier_id == c_user and \
               c_date - h.history_date < datetime.timedelta(seconds=5):
                to_delete.append(h)
            c_user = h.history_modifier_id
            c_date = h.history_date
        nb_deleted[model.__name__] += len(to_delete)

for item in to_delete:
    item.delete()
for m in nb_deleted:
    print "* %d deleted for %s" % (nb_deleted[m], m)

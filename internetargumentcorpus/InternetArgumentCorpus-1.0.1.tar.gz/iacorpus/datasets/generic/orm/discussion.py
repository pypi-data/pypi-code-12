import operator
from iacorpus.utilities.misc import lazy_property

class DiscussionMixin():
    __tablename__ = 'discussion'

    # TODO: test performance vs @reconstructor+init() ... we typically want this attribute but sometimes not
    @lazy_property
    def post_list(self):
        return sorted(self.posts.values(), key=operator.attrgetter('creation_date', 'post_id'))

    def __iter__(self):
        iterator = self.get_posts()
        return iterator

    def get_posts(self):
        iterator = iter(self.post_list)
        return iterator

def build_class(Base, engine):
    class Discussion(DiscussionMixin, Base):
        pass
    return Discussion

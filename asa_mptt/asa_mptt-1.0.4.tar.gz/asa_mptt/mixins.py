from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Index, Column, Integer, ForeignKey, desc, asc

from sqlalchemy_mptt.mixins import BaseNestedSets
from .events import _BaseTree


class AnotherSAMPTT(BaseNestedSets):

    @classmethod
    def get_basetree(cls_):
        return _BaseTree


    @declared_attr
    def left(cls):
        return Column(cls.get_basetree().FIELD_LEFT_IDX, Integer, nullable=False)
    
    @declared_attr
    def right(cls):
        return Column(cls.get_basetree().FIELD_RIGHT_IDX, Integer, nullable=False)
            

    @declared_attr
    def __table_args__(cls):
        return (
            Index('%s_lft_idx' % cls.__tablename__, cls.get_basetree().FIELD_LEFT_IDX),
            Index('%s_rgt_idx' % cls.__tablename__, cls.get_basetree().FIELD_RIGHT_IDX),
            Index('%s_level_idx' % cls.__tablename__, "level"),
        )


    def move_before(self, node_id):
        """ Moving one node of tree before another
            
        For example see:
            
        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_before_function`
        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_before_to_other_tree`
        * :mod:`sqlalchemy_mptt.tests.cases.move_node.test_move_before_to_top_level`
        """  # noqa
        session = Session.object_session(self)
        table = self.get_basetree()._get_tree_table(self.__mapper__)
        pk = getattr(table.c, self.get_pk_column().name)
        node = session.query(table).filter(pk == node_id).one()
        self.parent_id = node.parent_id
        self.mptt_move_before = node_id
        session.add(self)


    def leftsibling_in_level(self):
        """ Node to the left of the current node at the same level
                
        For example see :mod:`sqlalchemy_mptt.tests.cases.get_tree.test_leftsibling_in_level`
        """  # noqa
        table = self.get_basetree()._get_tree_table(self.__mapper__)
        session = Session.object_session(self)
        current_lvl_nodes = session.query(table)\
            .filter_by(level=self.level).filter_by(tree_id=self.tree_id)\
            .filter(table.c.lft < self.left).order_by(table.c.lft).all()
        if current_lvl_nodes:
            return current_lvl_nodes[-1]
        return None



class DjangoSAMPTT(AnotherSAMPTT):
    @classmethod
    def get_basetree(cls_):
        if not hasattr(cls_, '__basetree'):
            class _djBaseTree(_BaseTree):
                FIELD_LEFT_IDX  = 'lft'
                FIELD_RIGHT_IDX = 'rght'
            cls_.__basetree = _djBaseTree
        return cls_.__basetree


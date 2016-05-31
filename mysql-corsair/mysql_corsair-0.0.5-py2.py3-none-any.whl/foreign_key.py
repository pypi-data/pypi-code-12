class ForeignKey:
    def __init__(self, fk_tuple):
        self.source_table = fk_tuple[0]
        self.source_column = fk_tuple[1]
        self.constraint_name = fk_tuple[2]
        self.target_table = fk_tuple[3]
        self.target_column = fk_tuple[4]

    def to_dict(self):
        return {
            'source_table': self.source_table,
            'target_table': self.target_table,
            'source_column': self.source_column,
            'target_column': self.target_column
        }

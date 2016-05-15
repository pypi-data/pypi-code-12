# :Progetto:  SoL -- Add ownersadmin flag to players
# :Creato:    2015-06-07 00:37:34.210433
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '2ed994e1fa4'
down_revision = '34b09069223'


def upgrade():
    op.add_column('players', sa.Column('ownersadmin', sa.Boolean(), nullable=False,
                                       server_default='0'))


def downgrade():
    op.drop_column('players', 'ownersadmin')

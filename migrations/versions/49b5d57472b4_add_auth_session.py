"""add auth session

Revision ID: 49b5d57472b4
Revises: 540dbbff3fd7
Create Date: 2014-02-10 15:28:10.126765

"""

# revision identifiers, used by Alembic.
revision = '49b5d57472b4'
down_revision = '540dbbff3fd7'

from alembic import op
import sqlalchemy as sa
from atmcraft.model import meta



def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], name='fk_auth_session_account_id_account'),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name='fk_auth_session_client_id_client'),
    sa.PrimaryKeyConstraint('id', name='pk_auth_session')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('auth_session')
    ### end Alembic commands ###
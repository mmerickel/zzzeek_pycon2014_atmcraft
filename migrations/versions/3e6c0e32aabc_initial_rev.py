"""initial rev

Revision ID: 3e6c0e32aabc
Revises: None
Create Date: 2013-09-08 13:15:32.088452

"""

# revision identifiers, used by Alembic.
revision = '3e6c0e32aabc'
down_revision = None

from alembic import op
import sqlalchemy as sa
from atmcraft.model import meta



def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=u'pk_account'),
    sa.UniqueConstraint("username", name="uq_account_username")
    )

    op.create_table('balance_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=u'pk_balance_type')
    )
    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=32), nullable=True),
    sa.Column('secret', meta.BcryptType(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=u'pk_client')
    )
    op.create_table('account_balance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('balance_type_id', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('last_trans_id', meta.GUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], name=u'fk_account_balance_account_id_account'),
    sa.ForeignKeyConstraint(['balance_type_id'], ['balance_type.id'], name=u'fk_account_balance_balance_type_id_balance_type'),
    sa.PrimaryKeyConstraint('id', name=u'pk_account_balance')
    )
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('trans_id', meta.GUID(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('account_balance_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_balance_id'], ['account_balance.id'], name=u'fk_transaction_account_balance_id_account_balance'),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name=u'fk_transaction_client_id_client'),
    sa.PrimaryKeyConstraint('id', name=u'pk_transaction'),
    sa.UniqueConstraint('trans_id', name='uq_transaction_trans_id')
    )

    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    op.drop_table('account_balance')
    op.drop_table('client')
    op.drop_table('balance_type')
    op.drop_table('account')
    ### end Alembic commands ###
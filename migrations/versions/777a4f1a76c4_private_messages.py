"""private messages

Revision ID: 777a4f1a76c4
Revises: 43f96fc2190d
Create Date: 2025-02-13 18:08:13.419944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '777a4f1a76c4'
down_revision = '43f96fc2190d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=256), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['recipient_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_message_recipient_id'), ['recipient_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_message_sender_id'), ['sender_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_message_timestamp'), ['timestamp'], unique=False)

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=140),
               type_=sa.String(length=256),
               existing_nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_message_read_time', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_message_read_time')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=140),
               existing_nullable=False)

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_message_timestamp'))
        batch_op.drop_index(batch_op.f('ix_message_sender_id'))
        batch_op.drop_index(batch_op.f('ix_message_recipient_id'))

    op.drop_table('message')
    # ### end Alembic commands ###

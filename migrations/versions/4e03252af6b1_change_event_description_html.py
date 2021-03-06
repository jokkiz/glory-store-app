"""change Event description_html

Revision ID: 4e03252af6b1
Revises: 2515f93285c3
Create Date: 2017-01-27 22:41:27.031158

"""

# revision identifiers, used by Alembic.
revision = '4e03252af6b1'
down_revision = '2515f93285c3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('amenity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('short_name', sa.String(length=20), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('cost', sa.Numeric(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('events', sa.Column('description_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events', 'description_html')
    op.drop_table('amenity')
    # ### end Alembic commands ###

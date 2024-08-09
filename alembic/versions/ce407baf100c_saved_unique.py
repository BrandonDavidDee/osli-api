"""saved-unique

Revision ID: ce407baf100c
Revises: d96134c53e9b
Create Date: 2024-08-09 10:01:37.631897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce407baf100c'
down_revision = 'd96134c53e9b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uq_saved_item_bucket', 'saved_item_bucket', ['item_bucket_id', 'created_by_id'])
    op.create_unique_constraint('uq_saved_item_vimeo', 'saved_item_vimeo', ['item_vimeo_id', 'created_by_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_saved_item_vimeo', 'saved_item_vimeo', type_='unique')
    op.drop_constraint('uq_saved_item_bucket', 'saved_item_bucket', type_='unique')
    # ### end Alembic commands ###

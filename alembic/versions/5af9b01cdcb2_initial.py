"""initial

Revision ID: 5af9b01cdcb2
Revises: 
Create Date: 2024-07-30 10:31:54.890297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5af9b01cdcb2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('scopes', sa.String(), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_user_id'), 'auth_user', ['id'], unique=False)
    op.create_index(op.f('ix_auth_user_username'), 'auth_user', ['username'], unique=True)
    op.create_table('source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('bucket_name', sa.String(), nullable=True),
    sa.Column('access_key_id', sa.String(), nullable=True),
    sa.Column('secret_access_key', sa.String(), nullable=True),
    sa.Column('media_prefix', sa.String(), nullable=True),
    sa.Column('grid_view', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_source_id'), 'source', ['id'], unique=False)
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_title'), 'tag', ['title'], unique=True)
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=False),
    sa.Column('mime_type', sa.String(length=100), nullable=True),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['source_id'], ['source.id'], name='item_source_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], name='tag_item_item_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], name='tag_item_tag_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag_item')
    op.drop_table('item')
    op.drop_index(op.f('ix_tag_title'), table_name='tag')
    op.drop_table('tag')
    op.drop_index(op.f('ix_source_id'), table_name='source')
    op.drop_table('source')
    op.drop_index(op.f('ix_auth_user_username'), table_name='auth_user')
    op.drop_index(op.f('ix_auth_user_id'), table_name='auth_user')
    op.drop_table('auth_user')
    # ### end Alembic commands ###

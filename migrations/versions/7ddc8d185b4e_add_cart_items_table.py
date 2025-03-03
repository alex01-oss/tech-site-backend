"""Add cart items table

Revision ID: 7ddc8d185b4e
Revises: 
Create Date: 2025-03-03 15:24:01.638035

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7ddc8d185b4e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cart_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('article', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('currency', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('cart')
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('article',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.alter_column('category',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('line',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('subline',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('currency',
               existing_type=sa.TEXT(),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('unit',
               existing_type=sa.TEXT(),
               type_=sa.String(length=10),
               existing_nullable=True)
        batch_op.alter_column('name_param1',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit_param1',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('value_param1',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('name_param2',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit_param2',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('value_param2',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('name_param3',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit_param3',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('value_param3',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('name_param4',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit_param4',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('value_param4',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('name_param5',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit_param5',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('value_param5',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('name_param6',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit_param6',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('value_param6',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('name_param7',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('unit_param7',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('value_param7',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('value_param7',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit_param7',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('name_param7',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('value_param6',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit_param6',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('name_param6',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('value_param5',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit_param5',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('name_param5',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('value_param4',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit_param4',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('name_param4',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('value_param3',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit_param3',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('name_param3',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('value_param2',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit_param2',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('name_param2',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('value_param1',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit_param1',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('name_param1',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('unit',
               existing_type=sa.String(length=10),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('currency',
               existing_type=sa.String(length=10),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('subline',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('line',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('category',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('article',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.create_table('cart',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product_article', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('added_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.CheckConstraint('quantity > 0', name='cart_quantity_check'),
    sa.ForeignKeyConstraint(['product_article'], ['products.article'], name='cart_product_article_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='cart_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='cart_pkey'),
    sa.UniqueConstraint('user_id', 'product_article', name='cart_user_id_product_article_key')
    )
    op.drop_table('cart_items')
    # ### end Alembic commands ###

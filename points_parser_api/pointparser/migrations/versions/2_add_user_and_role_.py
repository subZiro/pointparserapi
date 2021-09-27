"""empty message

Revision ID: f6c72df9cb65
Revises: 2_add_user_and_role
Create Date: 2021-09-04 10:36:46.506624

"""
from alembic import op
import sqlalchemy as sa
from migrations.versions.data.migration_2 import roles

# revision identifiers, used by Alembic.
revision = '2_add_user_and_role'
down_revision = '1_create_db_tables'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_tb_addresses_coordinates', table_name='tb_addresses', schema='locations')

    bind = op.get_bind()

    # заполняем roles
    raw = "INSERT INTO authentication.tb_user_roles (caption, description, is_default) VALUES {};"
    bind.execute(raw.format(','.join(f"($${cap}$$, $${desc}$$, {is_def})" for cap, desc, is_def in roles)))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # ----Удаление вставленных ролей пользователей---- #
    captions = ','.join(f"'{cap}'" for cap, _, _ in roles)
    op.execute(f"DELETE FROM authentication.tb_user_roles WHERE caption in ({captions});")

    op.create_index('idx_tb_addresses_coordinates', 'tb_addresses', ['coordinates'], unique=False, schema='locations')
    # ### end Alembic commands ###

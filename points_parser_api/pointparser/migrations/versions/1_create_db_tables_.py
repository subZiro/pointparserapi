"""empty message

Revision ID: 2b1a074d959b
Revises: 
Create Date: 2021-08-26 16:08:27.028928

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import types
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1_create_db_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tb_user_roles',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('caption', sa.String(length=96), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('is_default', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('caption'),
                    schema='authentication'
                    )
    op.create_table('tb_phones',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('phone', sa.String(length=20), nullable=False),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('phone'),
                    schema='common'
                    )
    op.create_table('tb_cites',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('caption', sa.String(length=96), nullable=False),
                    sa.Column('code', sa.String(length=12), nullable=True),
                    sa.Column('iso2', sa.String(length=2), nullable=True),
                    sa.Column('iso3', sa.String(length=3), nullable=True),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('caption'),
                    sa.UniqueConstraint('code'),
                    sa.UniqueConstraint('iso2'),
                    sa.UniqueConstraint('iso3'),
                    schema='locations'
                    )
    op.create_table('tb_countries',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('caption', sa.String(length=96), nullable=False),
                    sa.Column('code', sa.String(length=12), nullable=True),
                    sa.Column('iso2', sa.String(length=2), nullable=True),
                    sa.Column('iso3', sa.String(length=3), nullable=True),
                    sa.Column('is_valid', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('caption'),
                    sa.UniqueConstraint('code'),
                    sa.UniqueConstraint('iso2'),
                    sa.UniqueConstraint('iso3'),
                    schema='locations'
                    )
    op.create_table('tb_regions',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('caption', sa.String(length=96), nullable=False),
                    sa.Column('code', sa.String(length=12), nullable=True),
                    sa.Column('iso2', sa.String(length=2), nullable=True),
                    sa.Column('iso3', sa.String(length=3), nullable=True),
                    sa.Column('is_valid', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('caption'),
                    sa.UniqueConstraint('code'),
                    sa.UniqueConstraint('iso2'),
                    sa.UniqueConstraint('iso3'),
                    schema='locations'
                    )
    op.create_table('tb_parsers_details',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('parser_type', sa.String(), nullable=False),
                    sa.Column('caption', sa.Text(), nullable=False),
                    sa.Column('count', sa.Integer(), nullable=True),
                    sa.Column('limit', sa.Integer(), nullable=False),
                    sa.Column('last_update', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('pid'),
                    schema='parsers'
                    )
    op.create_table('tb_point_sub_types',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('caption', sa.String(length=124), nullable=False),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('caption'),
                    schema='points'
                    )
    op.create_table('tb_point_types',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('caption', sa.String(length=64), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('is_main', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('caption'),
                    schema='points'
                    )
    op.create_table('tb_users',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('uid', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
                    sa.Column('email', sa.String(length=64), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('caption', sa.String(length=64), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('member_since', sa.DateTime(), nullable=True),
                    sa.Column('last_seen', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['role_id'], ['authentication.tb_user_roles.pid'], ),
                    sa.PrimaryKeyConstraint('pid'),
                    schema='authentication'
                    )
    op.create_index(op.f('ix_authentication_tb_users_email'), 'tb_users', ['email'], unique=True, schema='authentication')
    op.create_index(op.f('ix_authentication_tb_users_role_id'), 'tb_users', ['role_id'], unique=False, schema='authentication')
    op.create_table('tb_addresses',
                    sa.Column('pid', sa.BigInteger(), autoincrement=True, nullable=False),
                    sa.Column('country_id', sa.Integer(), nullable=True),
                    sa.Column('region_id', sa.Integer(), nullable=True),
                    sa.Column('city_id', sa.Integer(), nullable=True),
                    sa.Column('full_address', sa.String(length=256), nullable=True),
                    sa.Column('latitude', sa.String(), nullable=True),
                    sa.Column('longitude', sa.String(), nullable=True),
                    sa.Column('coordinates', types.Geometry(geometry_type='POINT',
                                                            srid=4326,
                                                            from_text='ST_GeomFromEWKT',
                                                            name='geometry'),
                              nullable=True),
                    sa.Column('from_coordinates', sa.Boolean(), nullable=True),
                    sa.Column('distance_by_metro', sa.Float(), nullable=True),
                    sa.ForeignKeyConstraint(['city_id'], ['locations.tb_cites.pid'], ),
                    sa.ForeignKeyConstraint(['country_id'], ['locations.tb_countries.pid'], ),
                    sa.ForeignKeyConstraint(['region_id'], ['locations.tb_regions.pid'], ),
                    sa.PrimaryKeyConstraint('pid'),
                    schema='locations'
                    )
    op.create_index(op.f('ix_locations_tb_addresses_city_id'), 'tb_addresses', ['city_id'], unique=False, schema='locations')
    op.create_index(op.f('ix_locations_tb_addresses_country_id'), 'tb_addresses', ['country_id'], unique=False, schema='locations')
    op.create_index(op.f('ix_locations_tb_addresses_region_id'), 'tb_addresses', ['region_id'], unique=False, schema='locations')
    op.create_table('tb_search_histories',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('parser_id', sa.Integer(), nullable=True),
                    sa.Column('search_query', sa.String(), nullable=True),
                    sa.Column('cnt_results', sa.Integer(), nullable=True),
                    sa.Column('is_complete', sa.Boolean(), nullable=True),
                    sa.Column('skip', sa.Integer(), nullable=True),
                    sa.Column('created', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['parser_id'], ['parsers.tb_parsers_details.pid'], ),
                    sa.PrimaryKeyConstraint('pid'),
                    schema='parsers'
                    )
    op.create_index(op.f('ix_parsers_tb_search_histories_parser_id'), 'tb_search_histories', ['parser_id'], unique=False, schema='parsers')
    op.create_table('tb_target_categories',
                    sa.Column('pid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('type_id', sa.Integer(), nullable=False),
                    sa.Column('sub_type_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['sub_type_id'], ['points.tb_point_sub_types.pid'], ),
                    sa.ForeignKeyConstraint(['type_id'], ['points.tb_point_types.pid'], ),
                    sa.PrimaryKeyConstraint('pid'),
                    schema='points'
                    )
    op.create_table('tb_base_points',
                    sa.Column('pid', sa.BigInteger(), autoincrement=True, nullable=False),
                    sa.Column('type_id', sa.Integer(), nullable=False),
                    sa.Column('address_id', sa.BigInteger(), nullable=True),
                    sa.Column('working_times', sa.String(), nullable=True),
                    sa.Column('caption', sa.String(length=256), nullable=False),
                    sa.Column('yandex_id', sa.String(), nullable=True),
                    sa.Column('is_retail', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['address_id'], ['locations.tb_addresses.pid'], ),
                    sa.ForeignKeyConstraint(['type_id'], ['points.tb_point_types.pid'], ),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('yandex_id'),
                    schema='points'
                    )
    op.create_index(op.f('ix_points_tb_base_points_address_id'), 'tb_base_points', ['address_id'], unique=False, schema='points')
    op.create_index(op.f('ix_points_tb_base_points_type_id'), 'tb_base_points', ['type_id'], unique=False, schema='points')
    op.create_table('tb_temp_points',
                    sa.Column('pid', sa.BigInteger(), autoincrement=True, nullable=False),
                    sa.Column('address_id', sa.BigInteger(), nullable=True),
                    sa.Column('address', sa.String(), nullable=True),
                    sa.Column('type_id', sa.Integer(), nullable=True),
                    sa.Column('caption', sa.String(), nullable=True),
                    sa.Column('url', sa.String(), nullable=True),
                    sa.Column('categories', sa.String(), nullable=True),
                    sa.Column('phones', sa.String(), nullable=True),
                    sa.Column('yandex_id', sa.String(), nullable=False),
                    sa.Column('working_times', sa.String(), nullable=True),
                    sa.Column('type_point', sa.String(), nullable=True),
                    sa.Column('lat', sa.String(), nullable=True),
                    sa.Column('lon', sa.String(), nullable=True),
                    sa.Column('is_checked', sa.Boolean(), nullable=True),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['address_id'], ['locations.tb_addresses.pid'], ),
                    sa.ForeignKeyConstraint(['type_id'], ['points.tb_point_types.pid'], ),
                    sa.PrimaryKeyConstraint('pid'),
                    sa.UniqueConstraint('yandex_id'),
                    schema='points'
                    )
    op.create_index(op.f('ix_points_tb_temp_points_address_id'), 'tb_temp_points', ['address_id'], unique=False, schema='points')
    op.create_index(op.f('ix_points_tb_temp_points_type_id'), 'tb_temp_points', ['type_id'], unique=False, schema='points')
    op.create_table('tb_phones_base_point',
                    sa.Column('point_id', sa.BigInteger(), nullable=False),
                    sa.Column('phone_id', sa.Integer(), nullable=False),
                    sa.Column('is_main', sa.Boolean(), server_default='false', nullable=True),
                    sa.ForeignKeyConstraint(['phone_id'], ['common.tb_phones.pid'], ),
                    sa.ForeignKeyConstraint(['point_id'], ['points.tb_base_points.pid'], ),
                    sa.PrimaryKeyConstraint('point_id', 'phone_id'),
                    schema='common'
                    )
    op.create_table('tb_point_categories',
                    sa.Column('point_id', sa.Integer(), nullable=False),
                    sa.Column('category_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['category_id'], ['points.tb_target_categories.pid'], ),
                    sa.ForeignKeyConstraint(['point_id'], ['points.tb_base_points.pid'], ),
                    sa.PrimaryKeyConstraint('point_id', 'category_id'),
                    schema='points'
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tb_point_categories', schema='points')
    op.drop_table('tb_phones_base_point', schema='common')
    op.drop_index(op.f('ix_points_tb_temp_points_type_id'), table_name='tb_temp_points', schema='points')
    op.drop_index(op.f('ix_points_tb_temp_points_address_id'), table_name='tb_temp_points', schema='points')
    op.drop_table('tb_temp_points', schema='points')
    op.drop_index(op.f('ix_points_tb_base_points_type_id'), table_name='tb_base_points', schema='points')
    op.drop_index(op.f('ix_points_tb_base_points_address_id'), table_name='tb_base_points', schema='points')
    op.drop_table('tb_base_points', schema='points')
    op.drop_table('tb_target_categories', schema='points')
    op.drop_index(op.f('ix_parsers_tb_search_histories_parser_id'), table_name='tb_search_histories', schema='parsers')
    op.drop_table('tb_search_histories', schema='parsers')
    op.drop_index(op.f('ix_locations_tb_addresses_region_id'), table_name='tb_addresses', schema='locations')
    op.drop_index(op.f('ix_locations_tb_addresses_country_id'), table_name='tb_addresses', schema='locations')
    op.drop_index(op.f('ix_locations_tb_addresses_city_id'), table_name='tb_addresses', schema='locations')
    op.drop_table('tb_addresses', schema='locations')
    op.drop_index(op.f('ix_authentication_tb_users_role_id'), table_name='tb_users', schema='authentication')
    op.drop_index(op.f('ix_authentication_tb_users_email'), table_name='tb_users', schema='authentication')
    op.drop_table('tb_users', schema='authentication')
    op.drop_table('tb_point_types', schema='points')
    op.drop_table('tb_point_sub_types', schema='points')
    op.drop_table('tb_parsers_details', schema='parsers')
    op.drop_table('tb_regions', schema='locations')
    op.drop_table('tb_countries', schema='locations')
    op.drop_table('tb_cites', schema='locations')
    op.drop_table('tb_phones', schema='common')
    op.drop_table('tb_user_roles', schema='authentication')
    # ### end Alembic commands ###

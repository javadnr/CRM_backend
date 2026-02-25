"""create leads and action_history tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "0001_create_leads_history"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM

# Define the ENUM
lead_status_enum = ENUM(
    'new', 'in_progress', 'converted', 'lost',
    name='lead_status_enum',
    create_type=True
)

def upgrade():
    # create ENUM (checkfirst=True prevents "already exists" error)
    lead_status_enum.create(op.get_bind(), checkfirst=True)

    # create leads table
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("status", lead_status_enum, nullable=False, server_default="new"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # indexes
    op.create_index("idx_leads_status", "leads", ["status"])
    op.create_index("idx_leads_source", "leads", ["source"])

    # create action_history table
    op.create_table(
        "action_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_status", lead_status_enum, nullable=False),
        sa.Column("to_status", lead_status_enum, nullable=False),
        sa.Column("changed_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_history_lead_id", "action_history", ["lead_id"])


def downgrade():
    # drop tables and indexes
    op.drop_index("idx_history_lead_id", table_name="action_history")
    op.drop_table("action_history")
    op.drop_index("idx_leads_source", table_name="leads")
    op.drop_index("idx_leads_status", table_name="leads")
    op.drop_table("leads")

    # drop ENUM type (checkfirst=True prevents error if already dropped)
    lead_status_enum.drop(op.get_bind(), checkfirst=True)
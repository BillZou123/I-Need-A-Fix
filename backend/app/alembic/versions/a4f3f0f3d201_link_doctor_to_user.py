"""link doctor to user

Revision ID: a4f3f0f3d201
Revises: 9652b0a32ff3
Create Date: 2026-05-12 13:40:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a4f3f0f3d201"
down_revision = "9652b0a32ff3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("doctor", sa.Column("user_id", sa.UUID(), nullable=True))
    op.create_unique_constraint("uq_doctor_user_id", "doctor", ["user_id"])
    op.create_foreign_key(
        "fk_doctor_user_id_user",
        "doctor",
        "user",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_doctor_user_id_user", "doctor", type_="foreignkey")
    op.drop_constraint("uq_doctor_user_id", "doctor", type_="unique")
    op.drop_column("doctor", "user_id")

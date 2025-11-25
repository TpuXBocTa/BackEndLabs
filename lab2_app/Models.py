from sqlalchemy import text
from . import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True, index=True)

    records = db.relationship(
        "Record",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    owner_user = db.relationship("User", passive_deletes=True)
    records = db.relationship(
        "Record",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.UniqueConstraint("owner_id", "name", name="uq_categories_owner_id_name"),
        db.Index(
            "idx_categories_global_name",
            "name",
            unique=True,
            postgresql_where=text("owner_id IS NULL"),
        ),
    )


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    datetime = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="records")
    category = db.relationship("Category", back_populates="records")

    __table_args__ = (
        db.Index("idx_records_user_id_category_id_datetime", "user_id", "category_id", "datetime"),
        db.CheckConstraint("amount > 0", name="ck_records_amount_gt_zero"),
    )

from datetime import datetime
from . import db
from .Models import User, Category, Record

def test_data(reset: bool = False):
    if reset:
        db.drop_all()
        db.create_all()

    users = ["Nazar","Olena","Ihor","Svitlana","Andriy","Devushka"]
    cats  = ["Food & Dining","Transport","Utilities","Entertainment","Health & Fitness","Dogs"]
    demo = [
        (1,3,"2025-10-25 08:30:00",420.75),
        (2,1,"2025-10-25 12:15:30",158.40),
        (3,4,"2025-10-26 19:45:10",899.99),
        (4,2,"2025-10-27 07:10:20",64.00),
        (5,5,"2025-10-27 14:55:05",315.25),
        (1,1,"2025-10-27 18:20:00",92.30),
        (6,6,"2025-10-27 18:20:00",9999.99),
    ]

    db.session.add_all([User(name=n) for n in users])
    db.session.commit()

    db.session.add_all([Category(name=n) for n in cats])
    db.session.commit()

    for uid, cid, dt, amt in demo:
        db.session.add(Record(
            user_id=uid,
            category_id=cid,
            datetime=datetime.fromisoformat(dt),
            amount=float(amt),
        ))
    db.session.commit()

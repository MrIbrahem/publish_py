from flask.app import Flask
from src.main_app.db.models import CategoryRecord, PageRecord, UserRecord
from src.main_app.db.services.pages import get_leaderboard_chart_data
from src.main_app.extensions import db


def test_get_leaderboard_chart_data(app: Flask):
    with app.app_context():
        # Setup test data
        u1 = UserRecord(username="user1", user_group="group1")
        db.session.add(u1)

        c1 = CategoryRecord(category="cat1", campaign="camp1")
        db.session.add(c1)

        p1 = PageRecord(title="Page 1", user="user1", lang="en", cat="cat1", target="Target 1", pupdate="2023-01-15")
        p2 = PageRecord(title="Page 2", user="user1", lang="en", cat="cat1", target="Target 2", pupdate="2023-01-20")
        p3 = PageRecord(title="Page 3", user="user1", lang="en", cat="cat1", target="Target 3", pupdate="2023-02-10")
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        # Test basic retrieval
        data = get_leaderboard_chart_data()
        assert len(data) == 2
        assert data[0] == {"date": "2023-01", "count": 2}
        assert data[1] == {"date": "2023-02", "count": 1}

        # Test filter by user
        data = get_leaderboard_chart_data(user="user1")
        assert len(data) == 2

        data = get_leaderboard_chart_data(user="nonexistent")
        assert len(data) == 0

        # Test filter by lang
        data = get_leaderboard_chart_data(lang="en")
        assert len(data) == 2

        # Test filter by camp
        data = get_leaderboard_chart_data(camp="camp1")
        assert len(data) == 2

        # Test filter by year
        data = get_leaderboard_chart_data(year=2023)
        assert len(data) == 2

        # Test filter by year
        data = get_leaderboard_chart_data(year=2022)
        assert len(data) == 0

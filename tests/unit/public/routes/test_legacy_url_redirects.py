from flask.testing import FlaskClient


class TestLegacyUrlRedirects:

    def test_leaderboard_user_redirect_two_stage(self, test_client: FlaskClient):
        # Stage 1: Legacy PHP request -> 301 Redirect
        res1 = test_client.get("Translation_Dashboard/leaderboard.php?get=users&user=Mr.%20Ibrahem&unwanted_param=123")
        assert res1.status_code == 301
        assert "/Translation_Dashboard/leaderboard/users/Mr.%20Ibrahem" in res1.location
        assert "unwanted_param" not in res1.location

        # Stage 2: Destination Flask route -> 200 OK
        res2 = test_client.get(res1.location)
        assert res2.status_code == 200

    def test_leaderboard_lang_redirect_two_stage(self, test_client: FlaskClient):
        res1 = test_client.get("Translation_Dashboard/leaderboard.php?get=langs&langcode=ar&year=2024")
        assert res1.status_code == 301
        assert "/Translation_Dashboard/leaderboard/langs/ar" in res1.location
        assert "year=2024" in res1.location

        res2 = test_client.get(res1.location)
        assert res2.status_code == 200

    def test_leaderboard_index_redirect_two_stage(self, test_client: FlaskClient):
        res1 = test_client.get("/Translation_Dashboard/leaderboard.php?camp=COVID&year=2025")
        assert res1.status_code == 301
        assert "/Translation_Dashboard/leaderboard/" in res1.location
        assert "camp=COVID" in res1.location
        assert "year=2025" in res1.location

        res2 = test_client.get(res1.location)
        assert res2.status_code == 200

    def test_index_php_redirect_two_stage(self, test_client: FlaskClient):
        res1 = test_client.get("/Translation_Dashboard/index.php?code=ar&camp=COVID&unauthorized=bad")
        assert res1.status_code == 301
        assert "/Translation_Dashboard/" in res1.location
        assert "code=ar" in res1.location
        assert "camp=COVID" in res1.location
        assert "unauthorized" not in res1.location

        res2 = test_client.get(res1.location)
        assert res2.status_code == 200

    def test_translate_med_redirect_two_stage(self, test_client: FlaskClient):
        res1 = test_client.get("Translation_Dashboard/translate_med/index.php?title=COVID-19&code=ar")
        assert res1.status_code == 301
        assert "/Translation_Dashboard/translate_med/" in res1.location
        assert "title=COVID-19" in res1.location
        assert "code=ar" in res1.location

        res2 = test_client.get(res1.location)
        assert res2.status_code == 200

    def test_translate_shortcut_redirects(self, test_client: FlaskClient):
        for path in ["/translate.php", "/translate/medwiki.php", "/translate_med/medwiki.php"]:
            res = test_client.get(f"Translation_Dashboard/{path}?title=TestPage&code=es")
            assert res.status_code == 301
            assert "/Translation_Dashboard/translate_med/" in res.location

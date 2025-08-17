import unittest

from static.python.cookies import CookieStorage


class CookieTest(unittest.TestCase):
    """Tests CookieStorage functionality."""

    github_headers = """
set-cookie: _gh_sess=akjshdflashdbkfgjasklgfjadgf; Path=/; HttpOnly; Secure; SameSite=Lax
set-cookie: _octo=GH1.1.344607693.1754765774; Path=/; Domain=github.com; Expires=Sun, 09 Aug 2026 18:56:14 GMT; Secure; SameSite=Lax
set-cookie: logged_in=no; Path=/; Domain=github.com; Expires=Sun, 09 Aug 2026 18:56:14 GMT; HttpOnly; Secure; SameSite=Lax
    """.strip()  # noqa: E501

    wordpress_headers = """
set-cookie: tk_ai=m9ke2vO3Rm8TSqJOOvuahcjE; expires=Thu, 08 Aug 2030 18:57:35 GMT; Max-Age=157680000; path=/; domain=.wordpress.com; secure; SameSite=None
set-cookie: tk_ai_explat=m9ke2vO3Rm8TSqJOOvuahcjE; expires=Thu, 08 Aug 2030 18:57:35 GMT; Max-Age=157680000; path=/; domain=.wordpress.com; secure; SameSite=None
set-cookie: tk_qs=_en%3Dwpcom_experiment_variation_assigned%26_ut%3Danon%26_ui%3Dm9ke2vO3Rm8TSqJOOvuahcjE%26_ts%3D1754765855034%26experiment_id%3D22296%26experiment_variation_id%3D5247%26reason%3Dset_by_anon_id; path=/; domain=.wordpress.com; secure; SameSite=Strict
set-cookie: explat_test_aa_weekly_lohp_2025_week_32=treatment; expires=Mon, 25 Aug 2025 00:00:00 GMT; Max-Age=1314145; path=/; domain=.wordpress.com; secure; SameSite=None
set-cookie: tk_qs=_en%3Dwpcom_experiment_variation_assigned%26_ut%3Danon%26_ui%3Dm9ke2vO3Rm8TSqJOOvuahcjE%26_ts%3D1754765855034%26experiment_id%3D22296%26experiment_variation_id%3D5247%26reason%3Dset_by_anon_id%20_en%3Dwpcom_experiment_variation_assigned%26_ut%3Danon%26_ui%3Dm9ke2vO3Rm8TSqJOOvuahcjE%26_ts%3D1754765855035%26experiment_id%3D22309%26experiment_variation_id%3D5280%26reason%3Dset_by_anon_id; path=/; domain=.wordpress.com; secure; SameSite=Strict
set-cookie: wpcom_lohp_hero_bigsky_082025=control; expires=Thu, 28 Aug 2025 00:00:00 GMT; Max-Age=1573345; path=/; domain=.wordpress.com; secure; SameSite=None
    """.strip()  # noqa: E501

    def test_github(self) -> None:
        """Ensure we can parse github headers with some accuracy."""
        r = CookieStorage.from_headers(
            self.github_headers.strip().split("\n"),
            "github.com",
        )
        self.assertEqual(len(r.cookies), 3)
        self.assertEqual(r["_gh_sess"][0].value, "akjshdflashdbkfgjasklgfjadgf")
        self.assertEqual(r["_gh_sess"][0].path, "/")
        self.assertEqual(r["_gh_sess"][0].persistent, False)

        self.assertEqual(r["_octo"][0].secure, True)

    def test_wordpress(self) -> None:
        """Ensure we can parse wordpress.com cookie headers properly."""
        r = CookieStorage.from_headers(
            self.wordpress_headers.strip().split("\n"),
            ".wordpress.com",
        )
        self.assertEqual(len(r.cookies), 6)
        wpcom_cooke = r["wpcom_lohp_hero_bigsky_082025"][0]
        self.assertEqual(wpcom_cooke.value, "control")
        self.assertEqual(wpcom_cooke.secure, True)

    def test_clearing(self) -> None:
        """Ensure session-clearing works as expected."""
        r = CookieStorage.from_headers(
            self.github_headers.strip().split("\n"),
            "github.com",
        )

        r.end_session()
        self.assertEqual(len(r.cookies), 2)
        self.assertEqual(r["_octo"][0].samesite, "Lax")
        self.assertEqual(r.to_cookie_string(), "_octo=GH1.1.344607693.1754765774")
        self.assertEqual(
            r.to_cookie_string(for_javascript=False),
            "_octo=GH1.1.344607693.1754765774; logged_in=no",
        )

    def test_js(self) -> None:
        """Ensure javascript cookie-setting functions."""
        r = CookieStorage.from_headers(
            self.github_headers.strip().split("\n"),
            "github.com",
        )
        r.set_cookie("bob=willis; sam=maxton", "github.com")

        self.assertEqual(len(r.cookies), 4)
        self.assertEqual(r["bob"][0].value, "willis")
        self.assertEqual(len(r["sam"]), 0)

        r.set_cookie("sam=maxton; httponly", "github.com")
        self.assertEqual(len(r.cookies), 5)
        self.assertEqual(r["sam"][0].value, "maxton")
        self.assertIn("sam=maxton", r.to_cookie_string(for_javascript=False))

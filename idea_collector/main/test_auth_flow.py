from django.contrib.auth.models import User
from django.test import Client, TestCase


class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="old-password-123")

    def test_anonymous_is_redirected_to_login_when_account_exists(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/login/?next=/")

    def test_anonymous_settings_redirect_to_login_when_account_exists(self):
        response = self.client.get("/settings/")
        self.assertRedirects(response, "/login/?next=/settings/")

    def test_login_page_renders(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in")

    def test_manual_login(self):
        response = self.client.post(
            "/login/", {"username": "alice", "password": "old-password-123"}
        )
        self.assertRedirects(response, "/")
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_settings_page_renders_account_section(self):
        self.client.force_login(self.user)
        response = self.client.get("/settings/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Account")
        self.assertNotContains(response, "Save Account")
        self.assertNotContains(response, "Change Password")

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post("/logout/")
        self.assertRedirects(response, "/login/")
        self.assertRedirects(self.client.get("/"), "/login/?next=/")

    def test_delete_account_removes_login_requirement(self):
        self.client.force_login(self.user)
        response = self.client.post("/settings/", {"delete_account": ""})
        self.assertRedirects(response, "/settings/")

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(self.client.get("/").status_code, 200)


class RegistrationTests(TestCase):
    def test_app_is_open_while_no_account_exists(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_settings_offer_account_creation_when_no_user_exists(self):
        response = self.client.get("/settings/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")
        self.assertNotContains(response, "autofocus")
        self.assertContains(response, "There is no way to recover them")

    def test_create_account_signs_user_in(self):
        response = self.client.post(
            "/settings/",
            {
                "username": "newuser",
                "password1": "a-strong-password-123",
                "password2": "a-strong-password-123",
                "create_account": "",
            },
        )
        self.assertRedirects(response, "/settings/")
        self.assertTrue(User.objects.filter(username="newuser").exists())

        response = self.client.get("/settings/")
        self.assertContains(response, "Delete Account")
        self.assertNotContains(response, "Save Account")

        other = Client()
        self.assertRedirects(other.get("/"), "/login/?next=/")
        self.assertRedirects(
            other.post(
                "/login/",
                {"username": "newuser", "password": "a-strong-password-123"},
            ),
            "/",
        )

    def test_second_account_cannot_be_created(self):
        User.objects.create_user("alice", password="old-password-123")

        response = self.client.post(
            "/settings/",
            {
                "username": "mallory",
                "password1": "a-strong-password-123",
                "password2": "a-strong-password-123",
                "create_account": "",
            },
        )
        self.assertRedirects(response, "/login/?next=/settings/")
        self.assertFalse(User.objects.filter(username="mallory").exists())

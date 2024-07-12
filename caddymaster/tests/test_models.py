from django.test import TestCase
from django.contrib.auth.models import User

from caddymaster.models import CaddyShack, CaddyMaster

class CaddyShackModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        User.objects.create(
            username="test_cm", password="Stset01@", email="test1@test.com"
        )
        test_user = User.objects.get(id=1)
        cm = CaddyMaster.objects.create(user=test_user)
        User.objects.create(
            username="test_caddy", password="Stset01@", email="test2@test.com"
        )
        test_caddy = User.objects.get(id=2)
        cs = CaddyShack.objects.create(
            caddy_shack_title="Test Shack",
            caddy_master=cm,
        )
        cs.caddys.set([test_caddy])

    def test_str(self):
        shack = CaddyShack.objects.get(id=1)
        shack_str = shack.__str__()
        self.assertEqual(shack_str, "Test Shack")

    def test_caddy_shack_title_label(self):
        cs = CaddyShack.objects.get(id=1)
        field_label = cs._meta.get_field("caddy_shack_title").verbose_name
        self.assertEqual(field_label, "Caddy Shack")

    def test_caddy_master_label(self):
        cs = CaddyShack.objects.get(id=1)
        field_label = cs._meta.get_field("caddy_master").verbose_name
        self.assertEqual(field_label, "caddy master")

    def test_caddys_label(self):
        cs = CaddyShack.objects.get(id=1)
        field_label = cs._meta.get_field("caddys").verbose_name
        self.assertEqual(field_label, "caddys")
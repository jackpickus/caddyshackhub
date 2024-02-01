from django.test import TestCase
from django.contrib.auth.models import User

from loopers.models import Caddy, Loop


class CaddyModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(
            username="test_user", password="Stset01@", email="test@test.com"
        )
        user1 = User.objects.get(id=1)
        Caddy.objects.create(
            user=user1,
            loop_count=15,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )

    def test_loop_count_label(self):
        caddy = Caddy.objects.get(id=1)
        field_label = caddy._meta.get_field("loop_count").verbose_name
        self.assertEqual(field_label, "loop count")

    def test_friends_label(self):
        caddy = Caddy.objects.get(id=1)
        field_label = caddy._meta.get_field("friends").verbose_name
        self.assertEqual(field_label, "friends")

    def test_activation_key_label(self):
        caddy = Caddy.objects.get(id=1)
        field_label = caddy._meta.get_field("activation_key").verbose_name
        self.assertEqual(field_label, "activation key")

    def test_email_validated_label(self):
        caddy = Caddy.objects.get(id=1)
        field_label = caddy._meta.get_field("email_validated").verbose_name
        self.assertEqual(field_label, "email validated")

    def test_change_email_label(self):
        caddy = Caddy.objects.get(id=1)
        field_label = caddy._meta.get_field("change_email").verbose_name
        self.assertEqual(field_label, "change email")


class LoopModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(
            username="test_user2", password="Stset01@", email="test2@test.com"
        )
        user2 = User.objects.get(id=1)
        Loop.objects.create(
            loop_title="Double carry for Mr. Testcase",
            date="2021-03-20",
            num_loops=2,
            money=120,
            notes="Good loop",
            caddy=user2,
        )

    def test_loop_title_label(self):
        loop = Loop.objects.get(id=1)
        field_label = loop._meta.get_field("loop_title").verbose_name
        self.assertEqual(field_label, "loop title")

    def test_date_label(self):
        loop = Loop.objects.get(id=1)
        field_label = loop._meta.get_field("date").verbose_name
        self.assertEqual(field_label, "date")

    def test_num_loops_label(self):
        loop = Loop.objects.get(id=1)
        field_label = loop._meta.get_field("num_loops").verbose_name
        self.assertEqual(field_label, "Number of loops")

    def test_money_label(self):
        loop = Loop.objects.get(id=1)
        field_label = loop._meta.get_field("money").verbose_name
        self.assertEqual(field_label, "Money made")

    def test_notes_label(self):
        loop = Loop.objects.get(id=1)
        field_label = loop._meta.get_field("notes").verbose_name
        self.assertEqual(field_label, "notes")
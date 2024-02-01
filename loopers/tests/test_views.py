import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from loopers.models import Loop


class LoopListViewTest(TestCase):
    def setUp(self):
        test_user2 = User.objects.create_user(
            username="test_user2", password="Stset01@", email="test2@test.com"
        )

        test_user2.save()

        # Create 13 loops for pagination tests
        number_of_loops = 13

        count = 13
        for loop_id in range(number_of_loops):
            Loop.objects.create(
                loop_title=f"Loop {loop_id}",
                date=datetime.date.today() - datetime.timedelta(days=count),
                num_loops=1,
                money=60,
                notes=f"test {loop_id}",
                caddy=test_user2,
            )
            count -= 1

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:loops"))
        self.assertRedirects(response, "/accounts/login/?next=/loopers/loops/")

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username="test_user2", password="Stset01@")
        response = self.client.get(reverse("loopers:loops"))

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user2")
        # Check we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check the correct template was used
        self.assertTemplateUsed(response, "loopers/loop_list.html")

    def test_pagination_is_ten(self):
        login = self.client.login(username="test_user2", password="Stset01@")
        response = self.client.get(reverse("loopers:loops"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["loop_list"]) == 10)

    def test_lists_all_loops(self):
        login = self.client.login(username="test_user2", password="Stset01@")
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse("loopers:loops") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["loop_list"]) == 3)

    def test_loops_ordered_by_date_descending(self):
        login = self.client.login(username="test_user2", password="Stset01@")
        response = self.client.get(reverse("loopers:loops"))

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user2")
        # Check we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertTrue(len(response.context["loop_list"]) == 10)

        last_date = 0
        for loop in response.context["loop_list"]:
            if last_date == 0:
                last_date = loop.date
            else:
                self.assertTrue(last_date >= loop.date)
                last_date = loop.date

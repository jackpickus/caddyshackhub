import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from loopers.models import Loop, Caddy
from loopers.forms import FollowCaddyForm


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

class FriendsListViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test2@test.com"
        )
        test_user.save()
        self.test_caddy = Caddy.objects.create(
            user=test_user,
            loop_count=15,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )

        test_friend =User.objects.create_user(
            username="test_friend", password="Stset0133!", email="testfriend@test.com"
        )
        test_friend.save()
        Caddy.objects.create(
            user=test_friend,
            loop_count=0,
            activation_key="347e228cbdd89fabd",
            email_validated=1,
        )

        test_staff = User.objects.create(
            username="test_staff",
            password="Stset0133!",
            email="teststaff@test.com",
            is_staff=True,
        )
        test_staff.save()

        num_following = 3 

        for friend_id in range(num_following):
            test_user2 = User.objects.create_user(
                username=f"Friend {friend_id}",
                password="Testpw21!",
                email="test@testcase.com"
            )
            test_user2.save()
            test_caddy2 = Caddy.objects.create(
                user=test_user2,
                loop_count=1,
                activation_key="347efab47cd89fabd",
                email_validated=1,
            )
            test_caddy2.save()
            self.test_caddy.friends.add(test_caddy2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:friends"))
        self.assertRedirects(response, "/accounts/login/?next=/loopers/friends/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get(reverse("loopers:friends"))

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/friends.html")

    def test_get_number_of_caddys_following(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get(reverse("loopers:friends"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('total_following' in response.context)
        self.assertTrue('all_friends' in response.context)
        self.assertEqual(response.context["total_following"], 3)

    def test_redirect_to_friends_page_after_valid_form(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse('loopers:friends'), {'caddy_to_follow':'test_friend'})
        self.assertRedirects(response, reverse('loopers:friends'))
        get_response = self.client.get(reverse("loopers:friends"))
        self.assertEqual(get_response.context["total_following"], 4)

    def test_valid_form_but_staff(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse('loopers:friends'), {'caddy_to_follow':'test_staff'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/friends.html")
        self.assertEqual(response.context["total_following"], 3)

    def test_unfollow_caddy(self):
        self.client.login(username="test_user1", password="Stset01@")
        friend = User.objects.get(username="Friend 1")
        response = self.client.get(reverse("loopers:unfollow_friend", kwargs={"friend_id": friend.id}))
        self.assertRedirects(response, reverse("loopers:friends"))
        response2 = self.client.get(reverse("loopers:friends"))
        self.assertEqual(response2.context["total_following"], 2)

class IndexViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test2@test.com"
        )
        test_user.save()
        test_caddy = Caddy.objects.create(
            user=test_user,
            loop_count=15,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )
        test_friend =User.objects.create_user(
            username="test_friend", password="Stset0133!", email="testfriend@test.com"
        )
        test_friend.save()
        self.test_caddy2 = Caddy.objects.create(
            user=test_friend,
            loop_count=0,
            activation_key="347e228cbdd89fabd",
            email_validated=1,
        )
        test_caddy.friends.add(self.test_caddy2)
        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get("/loopers/")
        self.assertRedirects(response, "/accounts/login/?next=/loopers/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get("/loopers/")

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/index.html")

    def test_get_loop_count(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get("/loopers/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["loop_count"], 15)
        self.assertEqual(response.context["total_money"], 0)
        self.assertTrue('top_three_friends' in response.context)
        top_three_friends = response.context['top_three_friends']
        self.assertEqual(top_three_friends, {0: self.test_caddy2})

class NewLoopViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test2@test.com"
        )
        test_user.save()
        test_caddy = Caddy.objects.create(
            user=test_user,
            loop_count=0,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:new_loop"))
        self.assertRedirects(response, "/accounts/login/?next=/loopers/loop/new_loop/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get(reverse("loopers:new_loop"))

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/new_loop.html")

    def test_redirect_to_loops_page_after_valid_form(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse('loopers:new_loop'),
            {
                'loop_title':'test',
                'date':'2024-02-05',
                'num_loops':'1',
                'money':'100',
                'notes': '',
            })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('loopers:loops'))

    def test_render_new_loops_page_after_invalid_form(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse('loopers:new_loop'),
            {
                'loop_title':'',
                'date':'2024-02-05',
                'num_loops':'1',
                'money':'100',
                'notes': '',
            })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/new_loop.html")

class DeleteLoopViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user0", password="Stset01@", email="test2@test.com"
        )
        test_user.save()
        self.test_caddy = Caddy.objects.create(
            user=test_user,
            loop_count=14,
            activation_key="346efab47cd89fabd",
            email_validated=0,
        )

        test_user1 = User.objects.create_user(
            username="test_user1", password="Stset0133!", email="testfriend@test.com"
        )
        test_user1.save()
        Caddy.objects.create(
            user=test_user1,
            loop_count=-1,
            activation_key="346e228cbdd89fabd",
            email_validated=0,
        )
        Loop.objects.create(
            loop_title="Test User0s Loop",
            date=datetime.date.today(),
            num_loops=0,
            money=59,
            notes="test",
            caddy=test_user,
        )
        Loop.objects.create(
            loop_title="Test User1 Loop",
            date=datetime.date.today(),
            num_loops=0,
            money=59,
            notes="This is test user1s loop",
            caddy=test_user1,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:delete_loop", kwargs={"loop_id": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/loopers/loop/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_successfully_delete_loop(self):
        self.client.login(username="test_user0", password="Stset01@")
        response = self.client.get(reverse("loopers:delete_loop", kwargs={"loop_id": 1}))
        self.assertRedirects(response, reverse("loopers:loops"))

    def test_delete_other_caddys_loop(self):
        self.client.login(username="test_user0", password="Stset01@")
        response = self.client.get(reverse("loopers:delete_loop", kwargs={"loop_id": 2}))
        self.assertEqual(response.status_code, 403)

    def test_delete_non_existing_loop(self):
        self.client.login(username="test_user0", password="Stset01@")
        response = self.client.get(reverse("loopers:delete_loop", kwargs={"loop_id": 8}))
        self.assertEqual(response.status_code, 404)

class SettingsViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test2@test.com"
        )
        test_user.save()
        test_caddy = Caddy.objects.create(
            user=test_user,
            loop_count=15,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:settings"))
        self.assertRedirects(response, "/accounts/login/?next=/loopers/settings/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get(reverse("loopers:settings"))

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/settings.html")

class FollowersViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test2@test.com"
        )
        test_user1.save()
        self.test_caddy1 = Caddy.objects.create(
            user=test_user1,
            loop_count=14,
            activation_key="346efab47cd89fabd",
            email_validated=0,
        )

        test_user2 = User.objects.create_user(
            username="test_user2", password="Stset0133!", email="testfriend@test.com"
        )
        test_user2.save()
        test_caddy2 = Caddy.objects.create(
            user=test_user2,
            loop_count=-1,
            activation_key="346e228cbdd89fabd",
            email_validated=0,
        )
        self.test_caddy1.friends.add(test_caddy2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:followers"))
        self.assertRedirects(response, "/accounts/login/?next=/loopers/friends/followers/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_get_followers(self):
        self.client.login(username="test_user2", password="Stset0133!")
        response = self.client.get(reverse("loopers:followers"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/followers.html")
        followers = ''.join(response.context["followers"])
        self.assertEqual(followers, self.test_caddy1.user.username)

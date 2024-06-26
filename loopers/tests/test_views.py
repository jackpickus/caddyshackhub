import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from loopers.models import Loop, Caddy


class LoopListViewTest(TestCase):
    def setUp(self):
        test_user2 = User.objects.create_user(
            username="test_user2", password="Stset01@", email="test2@test.com"
        )

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
        self.assertRedirects(response, "/accounts/login/?next=/loops/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user2", password="Stset01@")
        response = self.client.get(reverse("loopers:loops"))

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user2")
        # Check we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check the correct template was used
        self.assertTemplateUsed(response, "loopers/loop_list.html")

    def test_pagination_is_ten(self):
        self.client.login(username="test_user2", password="Stset01@")
        response = self.client.get(reverse("loopers:loops"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["loop_list"]) == 10)

    def test_lists_all_loops(self):
        self.client.login(username="test_user2", password="Stset01@")
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse("loopers:loops") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["loop_list"]) == 3)

    def test_loops_ordered_by_date_descending(self):
        self.client.login(username="test_user2", password="Stset01@")
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
        self.test_caddy = Caddy.objects.create(
            user=test_user,
            loop_count=15,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )

        test_friend = User.objects.create_user(
            username="test_friend", password="Stset0133!", email="testfriend@test.com"
        )
        Caddy.objects.create(
            user=test_friend,
            loop_count=0,
            activation_key="347e228cbdd89fabd",
            email_validated=1,
        )

        User.objects.create(
            username="test_staff",
            password="Stset0133!",
            email="teststaff@test.com",
            is_staff=True,
        )

        num_following = 3 

        for friend_id in range(num_following):
            test_user2 = User.objects.create_user(
                username=f"Friend {friend_id}",
                password="Testpw21!",
                email="test@testcase.com"
            )
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
        self.assertRedirects(response, "/accounts/login/?next=/friends/")
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
        test_caddy = Caddy.objects.create(
            user=test_user,
            loop_count=15,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )
        test_friend =User.objects.create_user(
            username="test_friend", password="Stset0133!", email="testfriend@test.com"
        )
        self.test_caddy2 = Caddy.objects.create(
            user=test_friend,
            loop_count=0,
            activation_key="347e228cbdd89fabd",
            email_validated=1,
        )
        test_caddy.friends.add(self.test_caddy2)
        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get("")
        self.assertRedirects(response, "/accounts/login/?next=/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get("")

        # Check if user is logged in
        self.assertEqual(str(response.context["user"]), "test_user1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/index.html")

    def test_get_loop_count(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get("")
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
        Caddy.objects.create(
            user=test_user,
            loop_count=0,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:new_loop"))
        self.assertRedirects(response, "/accounts/login/?next=/loop/new_loop/")
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
        Caddy.objects.create(
            user=test_user,
            loop_count=14,
            activation_key="346efab47cd89fabd",
            email_validated=0,
        )

        test_user1 = User.objects.create_user(
            username="test_user1", password="Stset0133!", email="testfriend@test.com"
        )
        Caddy.objects.create(
            user=test_user1,
            loop_count=1,
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
        self.assertRedirects(response, "/accounts/login/?next=/loop/delete/1")
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

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:settings"))
        self.assertRedirects(response, "/accounts/login/?next=/settings/")
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
        self.test_caddy1 = Caddy.objects.create(
            user=test_user1,
            loop_count=14,
            activation_key="346efab47cd89fabd",
            email_validated=0,
        )

        test_user2 = User.objects.create_user(
            username="test_user2", password="Stset0133!", email="testfriend@test.com"
        )
        test_caddy2 = Caddy.objects.create(
            user=test_user2,
            loop_count=-1,
            activation_key="346e228cbdd89fabd",
            email_validated=0,
        )
        self.test_caddy1.friends.add(test_caddy2)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:followers"))
        self.assertRedirects(response, "/accounts/login/?next=/friends/followers/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_get_followers(self):
        self.client.login(username="test_user2", password="Stset0133!")
        response = self.client.get(reverse("loopers:followers"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/followers.html")
        followers = ''.join(response.context["followers"])
        self.assertEqual(followers, self.test_caddy1.user.username)

class RegisterViewTest(TestCase):
    def test_get_register_page(self):
        response = self.client.get(reverse("loopers:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/register.html")

    def test_register_new_user_valid_form(self):
        response = self.client.post(reverse("loopers:register"),
            {
                "username":"new_user1",
                "password1":"MyPass123!",
                "password2":"MyPass123!",
                "email":"example@test.com"
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_register_new_user_invalid_form(self):
        response = self.client.post(reverse("loopers:register"),
            {
                "username":"new_user1",
                "password1":"MyPass123",
                "password2":"MyPass123!",
                "email": "example@test.com"
            }
        )
        self.assertEqual(response.status_code, 200)

class ActivateAccountViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user", password="Stset01@", email="test2@test.com"
        )
        Caddy.objects.create(
            user=test_user,
            loop_count=14,
            activation_key="346efab47cd89fabd",
            email_validated=0,
        )

    def test_activate_account_successfully(self):
        response = self.client.get(reverse("loopers:activate"), {"key":"346efab47cd89fabd"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/activated.html")

    def test_activate_account_fail(self):
        response = self.client.get(reverse("loopers:activate"), {"key":"346efab47cd8"})
        self.assertEqual(response.status_code, 404)

    def test_activate_account_no_key(self):
        response = self.client.get(reverse("loopers:activate"), {"key":""})
        self.assertEqual(response.status_code, 404)

class LoopDetailViewTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user", password="Stset01@", email="test2@test.com"
        )
        Loop.objects.create(
            loop_title="Test Users Loop",
            date=datetime.date.today(),
            num_loops=0,
            money=59,
            notes="test",
            caddy=test_user,
        )  

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:followers"))
        response = self.client.get(reverse("loopers:loop-detail", kwargs={"pk":1}))
        self.assertRedirects(response, "/accounts/login/?next=/loop/1")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))
    
    def test_get_loop_detail_successfully(self):
        self.client.login(username="test_user", password="Stset01@")
        response = self.client.get(reverse("loopers:loop-detail", kwargs={"pk":1}))
        self.assertEqual(response.status_code, 200)

    def test_get_loop_detail_loop_non_existent(self):
        self.client.login(username="test_user", password="Stset01@")
        response = self.client.get(reverse("loopers:loop-detail", kwargs={"pk":10}))
        self.assertEqual(response.status_code, 404)

class EditLoopViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test@test.com"
        )
        test_user2 = User.objects.create_user(
            username="test_user2", password="Stset0133!", email="test2@test.com"
        )
        Loop.objects.create(
            loop_title="Test User1 Loop",
            date=datetime.date.today(),
            num_loops=1,
            money=59,
            notes="test",
            caddy=test_user1,
        )
        Loop.objects.create(
            loop_title="Test User2 Loop",
            date=datetime.date.today(),
            num_loops=1,
            money=59,
            notes="This is test user2s loop",
            caddy=test_user2,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("loopers:edit_loop", kwargs={"pk": 1}))
        self.assertRedirects(response, "/accounts/login/?next=/loop/1/edit_loop")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_edit_loop_valid_form(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:edit_loop", kwargs={"pk": 1}), 
            {
                'loop_title':'test edit',
                'date':'2024-02-05',
                'num_loops':'2',
                'money':'100',
                'notes': 'This is new note',
            })
        self.assertRedirects(response, reverse("loopers:loops"))

    def test_edit_loop_invalid_form(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:edit_loop", kwargs={"pk": 1}), 
            {
                'loop_title':'',
                'date':'2024-02-05',
                'num_loops':'2',
                'money':'100',
                'notes': 'This is new note',
            })
        self.assertEqual(response.status_code, 200)

    def test_request_not_post(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get(reverse("loopers:edit_loop", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

    def test_edit_other_caddys_loop(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:edit_loop", kwargs={"pk": 2}), 
            {
                'loop_title':'test edit',
                'date':'2024-02-05',
                'num_loops':'2',
                'money':'100',
                'notes': 'This is new note',
            })
        self.assertEqual(response.status_code, 403)

    def test_edit_non_existing_loop(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:edit_loop", kwargs={"pk": 8}), 
            {
                'loop_title':'test edit',
                'date':'2024-02-05',
                'num_loops':'2',
                'money':'100',
                'notes': 'This is new note',
            })
        self.assertEqual(response.status_code, 404)

class ChangePasswordViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test@test.com"
        )
        Caddy.objects.create(
            user=test_user1,
            loop_count=0,
            activation_key="347e228cbdd89fabd",
            email_validated=1,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("loopers:change_password"),
            {
                "old_password": "Stset01@",
                "new_passowrd1": "TheNew103$",
                "new_password2": "TheNew103$",
            })
        self.assertRedirects(response, "/accounts/login/?next=/settings/change_password/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_valid_form_submission(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:change_password"),
            {
                "old_password": "Stset01@",
                "new_password1": "TheNew103$",
                "new_password2": "TheNew103$",
            })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("loopers:settings"))

    def test_invalid_form_submission(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:change_password"),
            {
                "old_password": "Stset01@",
                "new_password1": "TheNew103$",
                "new_password2": "TheN$",
            })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/change_password.html")

    def test_request_not_post(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get(reverse("loopers:change_password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/change_password.html")

class ChangeEmailViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username="test_user1", password="Stset01@", email="test@test.com"
        )
        Caddy.objects.create(
            user=test_user1,
            loop_count=15,
            activation_key="347efab47cd89fabd",
            email_validated=1,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse("loopers:change_email"),
            {
                "password": "Stset01@",
                "new_email": "new@email.com",
            })
        self.assertRedirects(response, "/accounts/login/?next=/settings/change_email/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_valid_form_submission(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:change_email"),
            {
                "password": "Stset01@",
                "new_email": "new@email.com",
            })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("loopers:settings"))

    def test_invalid_form_wrong_password(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.post(reverse("loopers:change_email"),
            {
                "password": "Sts",
                "new_email": "new@email.com",
            })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/change_email.html")

    def test_request_not_post(self):
        self.client.login(username="test_user1", password="Stset01@")
        response = self.client.get(reverse("loopers:change_email"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/change_email.html")

class ChangeEmailVerificationTest(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
            username="test_user", password="Stset01@", email="test2@test.com"
        )
        Caddy.objects.create(
            user=test_user,
            loop_count=14,
            activation_key="346efab47cd89fabd",
            email_validated=1,
            change_email="newemail@test.com",
            change_email_key="123456",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("loopers:email_verification"), {"key":"123456"})
        self.assertRedirects(response, "/accounts/login/?next=/email_verification/?key=123456")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_verify_email_successfully(self):
        self.client.login(username="test_user", password="Stset01@")
        response = self.client.get(reverse("loopers:email_verification"), {"key":"123456"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "loopers/settings.html")

    def test_verify_email_fail(self):
        self.client.login(username="test_user", password="Stset01@")
        response = self.client.get(reverse("loopers:email_verification"), {"key":"123"})
        self.assertEqual(response.status_code, 404)

    def test_verify_email_no_key(self):
        self.client.login(username="test_user", password="Stset01@")
        response = self.client.get(reverse("loopers:email_verification"), {"key":""})
        self.assertEqual(response.status_code, 404)

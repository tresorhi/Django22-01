from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.contrib.auth.models import User

# Create your tests here.
class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_kim = User.objects.create_user(username="kim", password="somepassword")
        self.user_lee = User.objects.create_user(username="lee", password="somepassword")

        self.category_com = Category.objects.create(name="computer", slug="computer")
        self.category_edu = Category.objects.create(name="education", slug="education")

        self.post_001 = Post.objects.create(title="첫번째 포스트", content="첫번째 포스트입니다.",
                                       author=self.user_kim, category=self.category_com)
        self.post_002 = Post.objects.create(title="두번째 포스트", content="두번째 포스트입니다.",
                                       author=self.user_lee,  category=self.category_edu)
        self.post_003 = Post.objects.create(title="세번째 포스트", content="세번째 포스트입니다.",
                                            author=self.user_lee)

    def nav_test(self,soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        home_btn = navbar.find('a', text="Home")
        self.assertEqual(home_btn.attrs['href'],'/')
        blog_btn = navbar.find('a', text="Blog")
        self.assertEqual(blog_btn.attrs['href'], '/blog/')
        about_btn = navbar.find('a', text="About Me")
        self.assertEqual(about_btn.attrs['href'], '/about_me/')

    def category_test(self,soup):
        category_card = soup.find('div', id='category_card')
        self.assertIn('Categories', category_card.text)
        self.assertIn(f'{self.category_com.name} ({self.category_com.post_set.count()})', category_card.text)
        self.assertIn(f'{self.category_edu.name} ({self.category_edu.post_set.count()})', category_card.text)
        self.assertIn(f'미분류 (1)', category_card.text)

    def test_post_list(self):
        response = self.client.get('/blog/', follow=True)    # 301
        # response 결과가 정상적으로 보이는지
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        # title이 정상적으로 보이는지
        self.assertEqual(soup.title.text, 'Blog')

        # navbar가 정상적으로 보이는지
        self.nav_test(soup)
        self.category_test(soup)

        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id="main-area")
        self.assertIn(self.post_001.title, main_area.text)
        self.assertIn(self.post_002.title, main_area.text)
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        self.assertIn(self.post_001.author.username.upper(), main_area.text)
        self.assertIn(self.post_002.author.username.upper(), main_area.text)

        # post가 정상적으로 보이는지
        # 1. 맨 처음엔 Post가 없음
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id="main-area")
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

        # 2. Post가 추가
        #post_001 = Post.objects.create(title="첫번째 포스트", content="첫번째 포스트입니다.",
        #                               author=self.user_kim)
        #post_002 = Post.objects.create(title="두번째 포스트", content="두번째 포스트입니다.",
        #                               author=self.user_lee)


    def test_post_detail(self):
        post_001 = Post.objects.create(title="첫번째 포스트", content="첫번째 포스트입니다.",
                                       author=self.user_kim)
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(post_001.get_absolute_url(), follow=True) # '/blog/1/'
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # navbar가 정상적으로 보이는지
        self.nav_test(soup)

        self.assertIn(post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)
        self.assertIn(post_001.content, post_area.text)
        self.assertIn(post_001.author.username.upper(), post_area.text)
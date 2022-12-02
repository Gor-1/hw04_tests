from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase
from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адресов
        cls.author = User.objects.create_user(username='UserName')
        cls.group = Group.objects.create(
            title='tmp_title',
            slug='tmp_slug',
            description='tmp_description'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='tmp_post_text',
            group=cls.group
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        # Создаём экземпляр клиента. Он авторизован.
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_form_create_and_edit_test(self, False)

    def test_edit_post(self):
        """Валидная форма изменит запись в Post."""
        post_form_create_and_edit_test(self, True)


def post_form_create_and_edit_test(self, edit):
    # подсчитаем кол_во постов
    post_count = Post.objects.count()
    text = 'New Тестовый текст'
    if edit:
        text = 'Измененный текст'

    form_data = {
        'group': self.group.pk,
        'text': text
    }

    if edit:
        # отправляем запрос
        response = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ))
    else:
        post_count += 1
        # Отправляем POST-запрос
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ))

    # Проверяем, увеличилось ли число постов
    self.assertEqual(Post.objects.count(), post_count)
    # Проверяем, что создалась запись
    self.assertTrue(
        Post.objects.filter(
            author=self.author,
            group=self.group,
            text=text
        ).exists()
    )

    # Проверим, что ничего не упало и страница отдаёт код 200
    self.assertEqual(response.status_code, 200)

import os
import subprocess

# Step 1: Create virtual environment and install dependencies
def setup_environment():
    os.system('python -m venv env')
    activate_script = 'env\\Scripts\\activate' if os.name == 'nt' else 'source env/bin/activate'
    os.system(activate_script)
    os.system('pip install django djangorestframework django-cors-headers pillow djangorestframework-simplejwt channels channels-redis django-ratelimit django-allauth')

# Step 2: Create Django project and app
def create_django_project():
    os.system('django-admin startproject wins')
    os.chdir('wins')
    os.system('python manage.py startapp core')
    os.system('python manage.py migrate')
    os.system('python manage.py createsuperuser')

# Step 3: Configure models, views, serializers, and URLs
def configure_django_app():
    models_code = """\
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    following_threads = models.ManyToManyField('Thread', related_name='followers', blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class Thread(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name='threads', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='threads', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    thread = models.ForeignKey(Thread, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
"""
    serializers_code = """\
from rest_framework import serializers
from .models import User, Category, Thread, Post

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
"""
    views_code = """\
from rest_framework import viewsets, pagination
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import action
from rest_framework.response import Response
from ratelimit.decorators import ratelimit
from .models import User, Category, Thread, Post
from .serializers import UserSerializer, CategorySerializer, ThreadSerializer, PostSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        user.set_password(request.data['password'])
        user.save()
        return Response({'status': 'password set'})

    @action(detail=True, methods=['post'])
    def follow_thread(self, request, pk=None):
        user = self.get_object()
        thread = Thread.objects.get(pk=request.data['thread_id'])
        user.following_threads.add(thread)
        return Response({'status': 'thread followed'})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    pagination_class = pagination.PageNumberPagination

    @action(detail=False, methods=['get'])
    @ratelimit(key='ip', rate='10/m', method='GET', block=True)
    def search(self, request):
        query = request.query_params.get('q')
        threads = self.queryset.filter(title__icontains=query)
        page = self.paginate_queryset(threads)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(threads, many=True)
        return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = pagination.PageNumberPagination

    @action(detail=False, methods=['get'])
    @ratelimit(key='ip', rate='10/m', method='GET', block=True)
    def search(self, request):
        query = request.query_params.get('q')
        posts = self.queryset.filter(content__icontains(query))
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
"""
    urls_code = """\
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, CategoryViewSet, ThreadViewSet, PostViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'threads', ThreadViewSet)
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('allauth.urls')),
]
"""
    project_urls_code = """\
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]
"""
    settings_additions = """\

# Additional configurations
INSTALLED_APPS += [
    'core',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'channels',
    'ratelimit',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

MIDDLEWARE += [
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-email-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# Channels Configuration
ASGI_APPLICATION = 'wins.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
"""
    asgi_code = """\
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wins.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
"""
    consumers_code = """\
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Thread

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
"""
    routing_code = """\
from django.urls import path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]
"""
    with open('core/models.py', 'w') as f:
        f.write(models_code)
    
    with open('core/serializers.py', 'w') as f:
        f.write(serializers_code)
    
    with open('core/views.py', 'w') as f:
        f.write(views_code)
    
    with open('core/urls.py', 'w') as f:
        f.write(urls_code)
    
    with open('wins/urls.py', 'w') as f:
        f.write(project_urls_code)

    settings_path = 'wins/settings.py'
    with open(settings_path, 'a') as f:
        f.write(settings_additions)

    with open('wins/asgi.py', 'w') as f:
        f.write(asgi_code)

    with open('core/consumers.py', 'w') as f:
        f.write(consumers_code)

    with open('core/routing.py', 'w') as f:
        f.write(routing_code)

    os.system('python manage.py makemigrations core')
    os.system('python manage.py migrate')

# Step 4: Create React frontend
def create_react_frontend():
    os.chdir('../')
    os.system('npx create-react-app frontend')
    os.chdir('frontend')
    os.system('npm install axios react-router-dom @headlessui/react @heroicons/react tailwindcss postcss autoprefixer @ckeditor/ckeditor5-react @ckeditor/ckeditor5-build-classic react-toastify')
    os.system('npx tailwindcss init -p')

    tailwind_config = """\
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class', // Enable dark mode
  theme: {
    extend: {},
  },
  plugins: [],
}
"""
    index_css = """\
@tailwind base;
@tailwind components;
@tailwind utilities;
"""

    with open('tailwind.config.js', 'w') as f:
        f.write(tailwind_config)
    
    with open('src/index.css', 'w') as f:
        f.write(index_css)

# Step 5: Configure React components
def configure_react_app():
    os.chdir('src')
    os.mkdir('components')
    os.mkdir('pages')
    os.mkdir('services')

    navbar_code = """\
import React from 'react';
import { Link } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Navbar = () => (
    <nav className="bg-gray-800 p-4">
        <ul className="flex space-x-4">
            <li><Link to="/" className="text-white">Home</Link></li>
            <li><Link to="/threads" className="text-white">Threads</Link></li>
            <li><Link to="/profile" className="text-white">Profile</Link></li>
            <li><Link to="/create-thread" className="text-white">Create Thread</Link></li>
        </ul>
        <ToastContainer />
    </nav>
);

export default Navbar;
"""
    home_code = """\
import React from 'react';

const Home = () => (
    <div className="text-white">
        <h1 className="text-3xl">Welcome to WINS Forum</h1>
    </div>
);

export default Home;
"""
    threads_code = """\
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactPaginate from 'react-paginate';

const Threads = () => {
    const [threads, setThreads] = useState([]);
    const [pageCount, setPageCount] = useState(0);

    useEffect(() => {
        fetchThreads(1);
    }, []);

    const fetchThreads = (selectedPage) => {
        axios.get(`/api/threads/?page=${selectedPage}`)
            .then(response => {
                setThreads(response.data.results);
                setPageCount(Math.ceil(response.data.count / 10));
            });
    };

    const handlePageClick = (data) => {
        fetchThreads(data.selected + 1);
    };

    return (
        <div className="text-white">
            <h1 className="text-3xl">Threads</h1>
            <ul>
                {threads.map(thread => (
                    <li key={thread.id}>{thread.title}</li>
                ))}
            </ul>
            <ReactPaginate
                previousLabel={'previous'}
                nextLabel={'next'}
                breakLabel={'...'}
                pageCount={pageCount}
                marginPagesDisplayed={2}
                pageRangeDisplayed={3}
                onPageChange={handlePageClick}
                containerClassName={'pagination'}
                activeClassName={'active'}
            />
        </div>
    );
};

export default Threads;
"""
    profile_code = """\
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';

const Profile = () => {
    const [user, setUser] = useState({});
    const history = useHistory();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await axios.get('/api/users/me/');
                setUser(response.data);
            } catch (error) {
                console.error('Error fetching user', error);
                history.push('/login');
            }
        };

        fetchUser();
    }, [history]);

    const handleAvatarChange = async (e) => {
        const formData = new FormData();
        formData.append('avatar', e.target.files[0]);
        try {
            await axios.put(`/api/users/${user.id}/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setUser({ ...user, avatar: URL.createObjectURL(e.target.files[0]) });
        } catch (error) {
            console.error('Error updating avatar', error);
        }
    };

    return (
        <div className="text-white">
            <h1 className="text-3xl">User Profile</h1>
            <p>Username: {user.username}</p>
            <p>Email: {user.email}</p>
            <p>Bio: {user.bio}</p>
            <input type="file" onChange={handleAvatarChange} />
            {user.avatar && <img src={user.avatar} alt="Avatar" />}
        </div>
    );
};

export default Profile;
"""
    login_code = """\
import React, { useState } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import { toast } from 'react-toastify';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const history = useHistory();

    const handleLogin = async () => {
        try {
            const response = await axios.post('/api/token/', { username, password });
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
            history.push('/');
        } catch (error) {
            console.error('Login failed', error);
            toast.error('Login failed');
        }
    };

    return (
        <div className="text-white">
            <h1 className="text-3xl">Login</h1>
            <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                className="bg-gray-700 p-2 mb-4"
            />
            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="bg-gray-700 p-2 mb-4"
            />
            <button onClick={handleLogin} className="bg-blue-500 p-2">Login</button>
        </div>
    );
};

export default Login;
"""
    register_code = """\
import React, { useState } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import { toast } from 'react-toastify';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const history = useHistory();

    const handleRegister = async () => {
        try {
            await axios.post('/api/users/', { username, password, email });
            history.push('/login');
            toast.success('Registration successful');
        } catch (error) {
            console.error('Registration failed', error);
            toast.error('Registration failed');
        }
    };

    return (
        <div className="text-white">
            <h1 className="text-3xl">Register</h1>
            <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                className="bg-gray-700 p-2 mb-4"
            />
            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="bg-gray-700 p-2 mb-4"
            />
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="bg-gray-700 p-2 mb-4"
            />
            <button onClick={handleRegister} className="bg-blue-500 p-2">Register</button>
        </div>
    );
};

export default Register;
"""
    create_thread_code = """\
import React, { useState } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import { CKEditor } from '@ckeditor/ckeditor5-react';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import { toast } from 'react-toastify';

const CreateThread = () => {
    const [title, setTitle] = useState('');
    const [category, setCategory] = useState('');
    const [content, setContent] = useState('');
    const history = useHistory();

    const handleCreateThread = async () => {
        try {
            await axios.post('/api/threads/', { title, category, content });
            history.push('/threads');
            toast.success('Thread created successfully');
        } catch (error) {
            console.error('Thread creation failed', error);
            toast.error('Thread creation failed');
        }
    };

    return (
        <div className="text-white">
            <h1 className="text-3xl">Create Thread</h1>
            <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Title"
                className="bg-gray-700 p-2 mb-4"
            />
            <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="Category"
                className="bg-gray-700 p-2 mb-4"
            />
            <CKEditor
                editor={ClassicEditor}
                data={content}
                onChange={(event, editor) => {
                    const data = editor.getData();
                    setContent(data);
                }}
            />
            <button onClick={handleCreateThread} className="bg-blue-500 p-2 mt-4">Create</button>
        </div>
    );
};

export default CreateThread;
"""
    auth_service_code = """\
import axios from 'axios';

const API_URL = '/api/';

const register = (username, email, password) => {
    return axios.post(API_URL + 'users/', {
        username,
        email,
        password,
    });
};

const login = (username, password) => {
    return axios
        .post(API_URL + 'token/', {
            username,
            password,
        })
        .then((response) => {
            if (response.data.access) {
                localStorage.setItem('user', JSON.stringify(response.data));
            }

            return response.data;
        });
};

const logout = () => {
    localStorage.removeItem('user');
};

export default {
    register,
    login,
    logout,
};
"""
    app_code = """\
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Threads from './pages/Threads';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import CreateThread from './pages/CreateThread';
import { toast } from 'react-toastify';
import { io } from 'socket.io-client';

const App = () => {
    useEffect(() => {
        const socket = io('ws://localhost:8000/ws/notifications/');
        socket.on('connect', () => {
            console.log('Connected to WebSocket');
        });
        socket.on('notification', (message) => {
            toast.info(message);
        });
        return () => socket.disconnect();
    }, []);

    return (
        <Router>
            <div className="bg-gray-900 min-h-screen">
                <Navbar />
                <div className="container mx-auto p-4">
                    <Switch>
                        <Route exact path="/" component={Home} />
                        <Route path="/threads" component={Threads} />
                        <Route path="/profile" component={Profile} />
                        <Route path="/login" component={Login} />
                        <Route path="/register" component={Register} />
                        <Route path="/create-thread" component={CreateThread} />
                    </Switch>
                </div>
            </div>
        </Router>
    );
};

export default App;
"""
    with open('components/Navbar.js', 'w') as f:
        f.write(navbar_code)
    
    with open('pages/Home.js', 'w') as f:
        f.write(home_code)
    
    with open('pages/Threads.js', 'w') as f:
        f.write(threads_code)
    
    with open('pages/Profile.js', 'w') as f:
        f.write(profile_code)
    
    with open('pages/Login.js', 'w') as f:
        f.write(login_code)
    
    with open('pages/Register.js', 'w') as f:
        f.write(register_code)
    
    with open('pages/CreateThread.js', 'w') as f:
        f.write(create_thread_code)
    
    with open('services/authService.js', 'w') as f:
        f.write(auth_service_code)
    
    with open('App.js', 'w') as f:
        f.write(app_code)

# Step 6: Integrate with backend
def integrate_backend():
    setup_proxy_code = """\
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: 'http://localhost:8000',
            changeOrigin: true,
        })
    );
};
"""
    with open('setupProxy.js', 'w') as f:
        f.write(setup_proxy_code)

# Step 7: Create Unit Tests
def create_unit_tests():
    os.mkdir('core/tests')
    test_models_code = """\
from django.test import TestCase
from core.models import User, Category, Thread, Post

class ModelTests(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertEqual(user.username, 'testuser')

    def test_create_category(self):
        category = Category.objects.create(name='Test Category')
        self.assertEqual(category.name, 'Test Category')

    def test_create_thread(self):
        user = User.objects.create_user(username='testuser', password='password123')
        category = Category.objects.create(name='Test Category')
        thread = Thread.objects.create(title='Test Thread', category=category, author=user)
        self.assertEqual(thread.title, 'Test Thread')

    def test_create_post(self):
        user = User.objects.create_user(username='testuser', password='password123')
        category = Category.objects.create(name='Test Category')
        thread = Thread.objects.create(title='Test Thread', category=category, author=user)
        post = Post.objects.create(thread=thread, author=user, content='Test Post')
        self.assertEqual(post.content, 'Test Post')
"""
    test_views_code = """\
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import User, Category, Thread, Post
from django.urls import reverse

class ViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Test Category')
        self.thread = Thread.objects.create(title='Test Thread', category=self.category, author=self.user)

    def test_create_post(self):
        url = reverse('post-list')
        data = {'thread': self.thread.id, 'author': self.user.id, 'content': 'Test Post'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Test Post')

    def test_search_threads(self):
        url = reverse('thread-search')
        response = self.client.get(url, {'q': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
"""
    with open('core/tests/test_models.py', 'w') as f:
        f.write(test_models_code)
    
    with open('core/tests/test_views.py', 'w') as f:
        f.write(test_views_code)

# Step 8: Run migrations and start the server
def start_server():
    os.chdir('../../wins')
    os.system('python manage.py runserver')

if __name__ == '__main__':
    setup_environment()
    create_django_project()
    configure_django_app()
    create_react_frontend()
    configure_react_app()
    integrate_backend()
    create_unit_tests()
    start_server()

DB_NAME = 'automadomus'
DB_USERNAME = None
DB_PASSWORD = None
DB_HOST = '127.0.0.1'
DB_PORT = 27017
JWT_SECRET_KEY = 'test'
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_CSRF_PROTECT = False
MAX_PAGINATED_LIMIT = 5
DEFAULT_USERS = [
    {
        'username': 'admin',
        'first_name': 'Test',
        'second_name': 'Admin',
        'password': 'test',
    },
]

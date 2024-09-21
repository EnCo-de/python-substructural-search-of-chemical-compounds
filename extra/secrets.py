import os

print(os.getenv('ACCESS_KEY', 'SECRET_ACCESS_KEY')[:7])
print(os.getenv('SECRET_ACCESS_KEY', 'SECRET_ACCESS_KEY')[:4:-1])
print(os.getenv('SECRET_ACCESS_KEY', 'SECRET_ACCESS_KEY')[-5:-1])

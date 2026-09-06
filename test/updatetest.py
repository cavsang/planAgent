import os

from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()  # .env 파일에서 환경 변수 로드

_fernet = Fernet(os.environ["ENCRYPTION_KEY"].encode())
c = _fernet.encrypt("테스트키".encode()).decode();
print(c);
d = _fernet.decrypt(c.encode()).decode();
print(d);
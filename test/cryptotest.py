from cryptography.fernet import Fernet

master_key = Fernet.generate_key()
print(master_key.decode())  
# 이 값을 환경변수(ENCRYPTION_KEY)로 저장. 절대 코드/DB에 하드코딩 금지.
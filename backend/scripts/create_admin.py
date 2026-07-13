"""İlk admin kullanıcısını oluşturur. Çalıştırma: python -m scripts.create_admin"""

import getpass

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.services.user_service import get_user_by_email


def main() -> None:
    db = SessionLocal()
    try:
        email = input("Admin e-posta: ").strip()
        if get_user_by_email(db, email):
            print("Bu e-posta zaten kayıtlı.")
            return
        password = getpass.getpass("Admin şifre: ")
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name="Admin",
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        print(f"Admin kullanıcı oluşturuldu: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

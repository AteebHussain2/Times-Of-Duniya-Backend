import hmac
import os


def isValidApiKey(secret: str) -> bool:
    API_SECRET = os.getenv("SECRET_KEY")
    if not API_SECRET:
        return False

    try:
        # Both must be bytes for secure comparison
        return hmac.compare_digest(secret.encode("utf-8"), API_SECRET.encode("utf-8"))
    except Exception as error:
        print("Error comparing secrets:", error)
        return False

import os
import requests

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://host.docker.internal:3000")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")


def revalidate(trigger: str, status: str, type: str):
    """
    Send revalidation request to Next.js /api/webhooks/revalidate/route.ts
    """
    try:
        url = f"{FRONTEND_BASE_URL}/api/webhooks/revalidate"
        payload = {
            "trigger": trigger,
            "status": status,
            "type": type,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SECRET_KEY}",
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        print(f"🔄 Revalidation triggered: {payload}")
        return True

    except Exception as e:
        print(f"❌ Revalidation failed for {payload}: {e}")
        return False

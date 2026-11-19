"""Paid tools: switched-off slots only. They cost money, so the router refuses them unless Franklin has turned one on
in config.json ("enabled": true) AND set "paid_ok": true AND added the key as a GitHub secret. Nothing here calls the
network until then. Each slot says what it would cost, checked 19 Nov 2026 (prices change; re-check before enabling).
"""
import os
from .base import Backend, NotAvailable


class Paid(Backend):
    free = False
    secret = ""
    cost_note = ""

    def available(self):
        if not os.environ.get(self.secret):
            raise NotAvailable(f"{self.name} is a paid tool; off (needs GitHub secret {self.secret} and Franklin's yes)")
        raise NotAvailable(f"{self.name}: the plug is a placeholder; write its request code when Franklin enables it")

    def generate(self, shot, out_path):
        self.available()


class Kling(Paid):
    name, secret = "kling", "KLING_API_KEY"
    cost_note = "Kling API: no free tier; about $0.056-$0.42 per second of video"


class Veo(Paid):
    name, secret = "veo", "GEMINI_PAID_API_KEY"
    cost_note = "Veo through the Gemini API: paid tier only; about $0.05-$0.60 per second"


class Higgsfield(Paid):
    name, secret = "higgsfield", "HIGGSFIELD_API_KEY"
    cost_note = "Higgsfield: paid subscription with credits; runs the same third-party models"

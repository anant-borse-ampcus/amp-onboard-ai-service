"""End-to-end smoke test exercising the full workflow via the ASGI app.

Run with: python scripts/e2e_smoke.py
Uses in-memory storage and the mock LLM provider for a deterministic offline run.
"""

import asyncio
import os

os.environ["STORAGE_BACKEND"] = "memory"
os.environ["LLM_PROVIDER"] = "mock"

from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import create_app  # noqa: E402


async def main() -> None:
    app = create_app()
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://e2e") as c:
            # 1. Manager logs in
            r = await c.post(
                "/api/v1/auth/login",
                json={"email": "manager@example.com", "password": "password123"},
            )
            assert r.status_code == 200, r.text
            mgr = {"Authorization": f"Bearer {r.json()['access_token']}"}
            print("1. manager login: OK")

            # 2. Create employee profile
            r = await c.post(
                "/api/v1/profiles",
                headers=mgr,
                json={
                    "name": "Jamie Fox",
                    "email": "jamie.fox@example.com",
                    "role": "Backend Engineer",
                    "team": "Payments",
                    "experience_level": "junior",
                    "skills": ["Go", "Postgres"],
                    "learning_style": "reading",
                    "start_date": "2026-08-01",
                },
            )
            assert r.status_code == 201, r.text
            profile_id = r.json()["id"]
            print(f"2. create profile: OK ({profile_id})")

            # 3. AI profile analysis
            r = await c.post(f"/api/v1/profiles/{profile_id}/analyze", headers=mgr)
            assert r.status_code == 200, r.text
            print("3. profile analysis: OK")

            # 4. Generate + activate journey
            r = await c.post(
                "/api/v1/journeys/generate",
                headers=mgr,
                json={"profile_id": profile_id, "total_days": 5},
            )
            assert r.status_code == 201, r.text
            journey = r.json()
            journey_id = journey["id"]
            r = await c.post(f"/api/v1/journeys/{journey_id}/activate", headers=mgr)
            assert r.status_code == 200, r.text
            print(f"4. generate + activate journey: OK ({len(journey['days'])} days)")

            # 5. Employee logs in and reads their journey
            r = await c.post(
                "/api/v1/auth/login",
                json={"email": "alex.rivera@example.com", "password": "password123"},
            )
            emp = {"Authorization": f"Bearer {r.json()['access_token']}"}
            r = await c.get(
                "/api/v1/journeys/profile/11111111-1111-1111-1111-111111111111",
                headers=emp,
            )
            assert r.status_code == 200, r.text
            emp_journey = r.json()[0]
            task_id = emp_journey["days"][0]["tasks"][0]["id"]
            print("5. employee login + read journey: OK")

            # 6. Complete a task
            r = await c.patch(
                f"/api/v1/journeys/{emp_journey['id']}/tasks/{task_id}",
                headers=emp,
                json={"completed": True},
            )
            assert r.status_code == 200, r.text
            print("6. complete task: OK")

            # 7. Mentor guidance
            r = await c.post(
                "/api/v1/mentor/guidance",
                headers=emp,
                json={
                    "task_id": task_id,
                    "profile_id": "11111111-1111-1111-1111-111111111111",
                    "journey_id": emp_journey["id"],
                },
            )
            assert r.status_code == 200, r.text
            print("7. mentor guidance: OK")

            # 8. FAQ (grounded + fallback)
            r = await c.post(
                "/api/v1/faq/ask", headers=emp, json={"question": "How do I set up VPN?"}
            )
            assert r.status_code == 200 and r.json()["fallback"] is False, r.text
            print("8. FAQ grounded answer: OK")

            # 9. Manager updates profile -> regenerate -> compare
            r = await c.put(
                f"/api/v1/profiles/{profile_id}",
                headers=mgr,
                json={"team": "Fraud Detection", "skills": ["Go", "Postgres", "ML"]},
            )
            assert r.status_code == 200, r.text
            r = await c.post(
                "/api/v1/journeys/regenerate",
                headers=mgr,
                json={"profile_id": profile_id, "previous_journey_id": journey_id},
            )
            assert r.status_code == 201, r.text
            new_journey_id = r.json()["id"]
            r = await c.get(
                f"/api/v1/journeys/compare/{journey_id}/{new_journey_id}", headers=mgr
            )
            assert r.status_code == 200, r.text
            comp = r.json()
            print(
                f"9. regenerate + compare: OK "
                f"(+{len(comp['added'])} ~{len(comp['modified'])} -{len(comp['removed'])})"
            )

            # 10. Authorization: employee blocked from manager action
            r = await c.get("/api/v1/profiles", headers=emp)
            assert r.status_code == 403, r.text
            print("10. RBAC (employee blocked from manager route): OK")

    print("\nALL E2E STEPS PASSED")


if __name__ == "__main__":
    asyncio.run(main())

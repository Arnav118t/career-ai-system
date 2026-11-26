import asyncio
import io
import unittest
from unittest.mock import patch

from fastapi import HTTPException, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import offer_routes, resume_routes
from app.db.database import Base
from app.db import models
from app.schemas.schemas import OfferCreate, ProfileCreate, UserCreate
from app.services.decision_service import generate_recommendations
from pydantic import ValidationError


class ApiIntegrationTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        self.addCleanup(engine.dispose)
        self.db = sessionmaker(bind=engine)()
        self.addCleanup(self.db.close)

        self.user = models.User(
            email="student@example.com",
            hashed_password="unused",
            full_name="Test Student",
        )
        self.other_user = models.User(
            email="other@example.com",
            hashed_password="unused",
            full_name="Other Student",
        )
        self.db.add_all([self.user, self.other_user])
        self.db.flush()

    def test_offer_list_only_returns_current_users_offers(self):
        self.db.add_all([
            models.Offer(
                user_id=self.user.id,
                company_name="Owned Company",
                company_type="Product",
                role="Engineer",
                ctc=12,
                location="Pune",
            ),
            models.Offer(
                user_id=self.other_user.id,
                company_name="Private Company",
                company_type="MNC",
                role="Engineer",
                ctc=10,
                location="Delhi",
            ),
        ])
        self.db.commit()

        offers = offer_routes.list_offers(self.db, self.user)

        self.assertEqual([offer.company_name for offer in offers], ["Owned Company"])

    def test_offer_creation_sets_owner(self):
        offer = OfferCreate(
            company_name="Example",
            company_type="Product",
            role="Engineer",
            ctc=12,
            location="Pune",
        )

        created = offer_routes.add_offer(offer, self.db, self.user)

        self.assertEqual(created.user_id, self.user.id)
        self.assertEqual(created.company_name, "Example")

    def test_invalid_offer_and_profile_values_are_rejected(self):
        with self.assertRaises(ValidationError):
            OfferCreate(
                company_name="Example",
                company_type="Product",
                role="Engineer",
                ctc=0,
                location="Pune",
            )
        with self.assertRaises(ValidationError):
            ProfileCreate(college="Example", branch="CSE", gpa=11)

    def test_password_longer_than_bcrypt_limit_is_rejected(self):
        with self.assertRaises(ValidationError):
            UserCreate(
                email="student@example.com",
                password="é" * 37,
                full_name="Test Student",
            )

    def test_recommendation_payload_matches_frontend_and_uses_profile_skills(self):
        self.db.add(models.Profile(
            user_id=self.user.id,
            college="Example College",
            branch="CSE",
            gpa=8.0,
            college_tier=2,
            current_skills=["python"],
            distance_from_home=50,
            wants_to_switch_after=24,
            study_time_available=2,
        ))
        self.db.add(models.Offer(
            user_id=self.user.id,
            company_name="Example",
            company_type="Product",
            role="Software Engineer",
            job_description="Python and SQL",
            skill_requirements=["python", "sql"],
            ctc=12,
            location="Pune",
            work_mode="Hybrid",
        ))
        self.db.commit()

        result = generate_recommendations(self.db, self.user.id)
        recommendation = result["recommendations"][0]

        self.assertIn("average_recommendation_score", result["analysis_summary"])
        self.assertEqual(recommendation["predictions"]["skill_match"], 50.0)
        self.assertEqual(recommendation["predictions"]["skill_match_details"]["source"], "profile")
        self.assertIn("growth_percentage", recommendation["predictions"]["salary"])
        self.assertIn("wlb_score", recommendation["predictions"]["workload"])
        self.assertIn("yearly", recommendation["predictions"]["savings"])

    def test_resume_upload_parses_and_persists_resume(self):
        class FakePage:
            def extract_text(self):
                return "Python SQL React B.Tech"

        class FakePdfReader:
            pages = [FakePage()]

        upload = UploadFile(
            filename="resume.PDF",
            file=io.BytesIO(b"%PDF-1.4 test content"),
        )
        with patch("app.services.resume_service.PyPDF2.PdfReader", return_value=FakePdfReader()):
            result = asyncio.run(resume_routes.upload_resume(upload, self.db, self.user))

        stored = self.db.query(models.Resume).one()
        self.assertEqual(result["resume_id"], stored.id)
        self.assertEqual(stored.user_id, self.user.id)
        self.assertEqual(set(result["extracted_skills"]), {"python", "sql", "react"})

    def test_resume_upload_rejects_non_pdf(self):
        upload = UploadFile(filename="resume.txt", file=io.BytesIO(b"not a PDF"))

        with self.assertRaises(HTTPException) as error:
            asyncio.run(resume_routes.upload_resume(upload, self.db, self.user))

        self.assertEqual(error.exception.status_code, 400)

    def test_resume_upload_rejects_oversized_file(self):
        upload = UploadFile(
            filename="resume.pdf",
            file=io.BytesIO(b"%PDF-" + b"x" * (5 * 1024 * 1024 + 1)),
        )

        with self.assertRaises(HTTPException) as error:
            asyncio.run(resume_routes.upload_resume(upload, self.db, self.user))

        self.assertEqual(error.exception.status_code, 413)


if __name__ == "__main__":
    unittest.main()

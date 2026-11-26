from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db import models
from app.services import prediction_service, resume_service
from app.schemas import schemas
from typing import List, Dict
import numpy as np
from app.services.ml_model_service import predict_satisfaction


def generate_recommendations(db: Session, user_id: int):

    profile = db.query(models.Profile).filter(
        models.Profile.user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Please complete your profile first."
        )

    offers = db.query(models.Offer).filter(
        models.Offer.user_id == user_id
    ).all()

    if not offers:
        raise HTTPException(
            status_code=404,
            detail="No offers found. Please add job offers first."
        )

    recommendations = []

    for offer in offers:

        # -----------------------------
        # Salary Growth Prediction
        # -----------------------------
        salary_pred = prediction_service.predict_salary_growth(
            schemas.SalaryPredictionInput(
                company_type=offer.company_type,
                role=offer.role,
                location=offer.location,
                current_ctc=offer.ctc,
                college_tier=profile.college_tier,
                gpa=profile.gpa
            ),
            profile
        )

        # -----------------------------
        # Skill Match
        # -----------------------------
        skill_match = _match_offer_skills(db, user_id, profile, offer)
        skill_score = skill_match["skill_match_score"]

        # -----------------------------
        # Workload Prediction
        # -----------------------------
        workload_pred = prediction_service.predict_workload(
            schemas.WorkloadPredictionInput(
                company_name=offer.company_name,
                company_type=offer.company_type,
                role=offer.role,
                work_mode=offer.work_mode
            )
        )

        # -----------------------------
        # Savings Potential
        # -----------------------------
        savings = prediction_service.calculate_savings_potential(
            offer.ctc,
            offer.location,
            profile.distance_from_home
        )

        # -----------------------------
        # Switch Probability
        # -----------------------------
        switch_score = 0

        if profile.wants_to_switch_after:

            switch_pred = prediction_service.predict_switch_probability(
                schemas.SwitchPredictionInput(
                    current_role=offer.role,
                    skill_gap=100 - skill_score,
                    study_time_available=workload_pred.get("available_study_hours", 0),
                    wants_to_switch_after=profile.wants_to_switch_after
                )
            )

            switch_score = switch_pred.get("switch_probability", 0)

        # -----------------------------
        # ML FEATURE VECTOR
        # -----------------------------
        feature_dict = {

            "gpa": profile.gpa,
            "college_tier": profile.college_tier,
            "study_time": workload_pred.get("available_study_hours", 0),
            "switch_months": profile.wants_to_switch_after or 0,

            "risk_score": 5,
            "ambition_score": 6,
            "stability_score": 5,
            "learning_score": 6,
            "salary_priority": 7,
            "wlb_preference": 6,

            "ctc": offer.ctc,

            "company_type": offer.company_type
            if isinstance(offer.company_type, int)
            else 3,

            "location_tier": 1
            if offer.location in [
                "Bangalore",
                "Mumbai",
                "Delhi",
                "Hyderabad",
                "Pune"
            ]
            else 2,

            "workload_score": workload_pred.get("workload_score", 5),
            "skill_match": skill_score,
            "savings_rate": savings.get("savings_rate", 0),
            "switch_probability": switch_score,
            "predicted_2yr_salary": salary_pred.get("predicted_2yr_ctc", 0)
        }

        # -----------------------------
        # ML Prediction
        # -----------------------------
        ml_score = predict_satisfaction(feature_dict)

        # penalties
        mass_recruiter_penalty = -15 if offer.is_mass_recruiter else 0
        bond_penalty = -min(20, (offer.bond_period or 0) / 12 * 5)

        final_score = ml_score + mass_recruiter_penalty + bond_penalty

        final_score = max(0, min(100, final_score))

        # -----------------------------
        # Save Predictions
        # -----------------------------
        offer.predicted_2yr_salary = salary_pred.get("predicted_2yr_ctc", 0)
        offer.skill_match_score = skill_score
        offer.switch_probability = switch_score
        offer.workload_score = workload_pred.get("workload_score", 5)
        offer.recommendation_score = final_score

        # -----------------------------
        # Generate Recommendation
        # -----------------------------
        recommendation = generate_recommendation_text(
            final_score,
            offer,
            salary_pred,
            workload_pred,
            savings,
            profile
        )

        recommendations.append({
            "offer_id": offer.id,
            "company_name": offer.company_name,
            "role": offer.role,
            "ctc": offer.ctc,
            "recommendation_score": round(final_score, 2),
            "recommendation": recommendation,
            "predictions": {
                "salary": {
                    "predicted_2yr_ctc": salary_pred["predicted_2yr_ctc"],
                    "growth_percentage": salary_pred["growth_rate"],
                },
                "skill_match": skill_score,
                "skill_match_details": skill_match,
                "workload": {"wlb_score": workload_pred["wlb_score"]},
                "savings": {"yearly": savings["yearly_savings"]},
                "switch_probability": switch_score,
            },
        })

    db.commit()

    recommendations.sort(
        key=lambda x: x["recommendation_score"],
        reverse=True
    )

    return {
        "total_offers": len(recommendations),
        "recommendations": recommendations,
        "top_recommendation": recommendations[0] if recommendations else None,
        "analysis_summary": generate_overall_summary(
            recommendations,
            profile
        )
    }


def _match_offer_skills(db, user_id, profile, offer):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user_id)
        .order_by(models.Resume.uploaded_at.desc())
        .first()
    )
    if resume and offer.job_description:
        result = resume_service.match_skills_with_job(db, user_id, offer.job_description)
        result["source"] = "resume"
        return result

    user_skills = {
        skill.strip().lower()
        for skill in ((resume.extracted_skills or []) if resume else (profile.current_skills or []))
        if isinstance(skill, str) and skill.strip()
    }
    required_skills = offer.skill_requirements or []
    if offer.job_description:
        required_skills = resume_service.extract_skills(offer.job_description)
    required_skills = {
        skill.strip().lower()
        for skill in required_skills
        if isinstance(skill, str) and skill.strip()
    }
    matching = user_skills.intersection(required_skills)
    score = (len(matching) / len(required_skills) * 100) if required_skills else 0.0
    return {
        "skill_match_score": round(score, 2),
        "user_skills": sorted(user_skills),
        "job_required_skills": sorted(required_skills),
        "matching_skills": sorted(matching),
        "missing_skills": sorted(required_skills - user_skills),
        "text_similarity": 0.0,
        "source": "resume" if resume else "profile",
    }


# -------------------------------------------------
# Recommendation Explanation
# -------------------------------------------------

def generate_recommendation_text(score, offer, salary_pred, workload_pred, savings, profile):

    if score >= 80:
        action = "STRONGLY RECOMMEND"
        reason = "Excellent overall fit"

    elif score >= 65:
        action = "RECOMMEND"
        reason = "Good opportunity"

    elif score >= 50:
        action = "CONSIDER"
        reason = "Moderate option"

    elif score >= 35:
        action = "CAUTION"
        reason = "Some concerns"

    else:
        action = "NOT RECOMMENDED"
        reason = "Better options likely available"

    details = []

    if salary_pred.get("growth_rate", 0) > 30:
        details.append("Strong salary growth potential")

    if workload_pred.get("burnout_risk") == "High":
        details.append("High workload risk")

    if savings.get("savings_rate", 0) > 50:
        details.append("Excellent savings potential")

    if offer.is_mass_recruiter:
        details.append("Mass recruiter may limit growth")

    if offer.bond_period and offer.bond_period > 0:
        details.append(f"Bond period: {offer.bond_period} months")

    return {
        "action": action,
        "reason": reason,
        "key_insights": details
    }


# -------------------------------------------------
# Overall Summary
# -------------------------------------------------

def generate_overall_summary(recommendations: List[Dict], profile):

    if not recommendations:
        return "No offers to analyze"

    avg_score = np.mean([
        r["recommendation_score"]
        for r in recommendations
    ])

    best = recommendations[0]

    summary = {
        "total_offers": len(recommendations),
        "average_score": round(avg_score, 2),
        "average_recommendation_score": round(avg_score, 2),
        "best_offer_company": best["company_name"],
        "best_offer_score": best["recommendation_score"],
        "insights": []
    }

    if avg_score > 70:
        summary["insights"].append("Excellent set of offers available")

    elif avg_score > 50:
        summary["insights"].append("Some decent opportunities")

    else:
        summary["insights"].append("Consider waiting for better opportunities")

    return summary
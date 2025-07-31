"""
SEO Reports Model for storing audit history and generating reports
"""

from app.core.extensions import db
from datetime import datetime
import json


class SEOReport(db.Model):
    """Model for storing SEO audit reports"""

    __tablename__ = "seo_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Null for anonymous users
    website_url = db.Column(db.String(500), nullable=False)
    domain = db.Column(db.String(255), nullable=False, index=True)

    # Report data
    overall_score = db.Column(db.Integer, nullable=False)
    pages_analyzed = db.Column(db.Integer, default=0)
    issues_found = db.Column(db.Integer, default=0)
    audit_results = db.Column(db.Text, nullable=False)  # JSON string

    # Metadata
    audit_duration = db.Column(db.Float, default=0.0)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Report status
    is_public = db.Column(db.Boolean, default=False)
    report_hash = db.Column(
        db.String(64), unique=True, index=True
    )  # For sharing reports

    def __repr__(self):
        return f"<SEOReport {self.domain} - Score: {self.overall_score}>"

    @property
    def audit_data(self):
        """Get audit results as dictionary"""
        if self.audit_results:
            try:
                return json.loads(self.audit_results)
            except json.JSONDecodeError as e:
                # Handle corrupted JSON gracefully
                print(f"JSON decode error for report {self.id}: {str(e)}")
                return {
                    "error": "Report data is corrupted",
                    "overall_score": self.overall_score or 0,
                    "crawl_summary": {
                        "successfully_crawled": self.pages_analyzed or 0,
                        "total_pages_found": self.pages_analyzed or 0,
                    },
                    "recommendations": [],
                    "technical_analysis": {},
                    "content_analysis": {},
                    "performance_analysis": {},
                }
            except Exception as e:
                print(
                    f"Unexpected error parsing audit data for report {self.id}: {str(e)}"
                )
                return {}
        return {}

    @audit_data.setter
    def audit_data(self, data):
        """Set audit results from dictionary"""
        try:
            # Ensure the data can be serialized properly
            if data is None:
                self.audit_results = json.dumps({})
            else:
                # Test serialization first
                test_json = json.dumps(data, default=str, ensure_ascii=False)
                # If successful, store it
                self.audit_results = test_json
        except (TypeError, ValueError) as e:
            print(f"Error serializing audit data: {str(e)}")
            # Store minimal safe data
            self.audit_results = json.dumps(
                {
                    "error": "Failed to serialize audit data",
                    "overall_score": (
                        getattr(data, "overall_score", 0)
                        if hasattr(data, "overall_score")
                        else 0
                    ),
                    "timestamp": str(datetime.utcnow()),
                }
            )

    @property
    def score_grade(self):
        """Get letter grade based on score"""
        if self.overall_score >= 90:
            return "A+"
        elif self.overall_score >= 80:
            return "A"
        elif self.overall_score >= 70:
            return "B"
        elif self.overall_score >= 60:
            return "C"
        elif self.overall_score >= 50:
            return "D"
        else:
            return "F"

    @property
    def score_color(self):
        """Get color class based on score"""
        if self.overall_score >= 80:
            return "green"
        elif self.overall_score >= 60:
            return "yellow"
        else:
            return "red"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "website_url": self.website_url,
            "domain": self.domain,
            "overall_score": self.overall_score,
            "score_grade": self.score_grade,
            "pages_analyzed": self.pages_analyzed,
            "issues_found": self.issues_found,
            "audit_duration": self.audit_duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "audit_data": self.audit_data,
        }


class SEOUsageLimit(db.Model):
    """Track SEO audit usage for free users"""

    __tablename__ = "seo_usage_limits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    # Monthly limits
    current_month = db.Column(db.Integer, nullable=False)  # Month number (1-12)
    current_year = db.Column(db.Integer, nullable=False)
    usage_count = db.Column(db.Integer, default=0)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<SEOUsageLimit User:{self.user_id} Usage:{self.usage_count}>"

    @staticmethod
    def get_usage_for_user(user_id):
        """Get current month usage for user"""
        now = datetime.now()
        usage = SEOUsageLimit.query.filter_by(
            user_id=user_id, current_month=now.month, current_year=now.year
        ).first()

        if not usage:
            # Create new usage record for current month
            usage = SEOUsageLimit(
                user_id=user_id,
                current_month=now.month,
                current_year=now.year,
                usage_count=0,
            )
            db.session.add(usage)
            db.session.commit()

        return usage

    @staticmethod
    def increment_usage(user_id):
        """Increment usage count for user"""
        usage = SEOUsageLimit.get_usage_for_user(user_id)
        usage.usage_count += 1
        db.session.commit()
        return usage

    @staticmethod
    def can_use_tool(user_id, is_premium=False):
        """Check if user can use SEO audit tool"""
        if is_premium:
            return True, "Premium user - unlimited access"

        usage = SEOUsageLimit.get_usage_for_user(user_id)
        free_limit = 3  # 3 audits per month for free users

        if usage.usage_count >= free_limit:
            return (
                False,
                f"Monthly limit reached ({usage.usage_count}/{free_limit}). Upgrade to Premium for unlimited access.",
            )

        return True, f"Usage: {usage.usage_count}/{free_limit} this month"

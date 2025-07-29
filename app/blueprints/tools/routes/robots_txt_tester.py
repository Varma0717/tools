from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
import requests
from urllib.parse import urljoin, urlparse
import urllib.robotparser

robots_txt_tester_bp = Blueprint("robots_txt_tester", __name__, url_prefix="/tools")


class RobotsForm(FlaskForm):
    url = StringField("Website URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Test Robots.txt")


def test_robots_txt(url):
    """Test robots.txt file of a website"""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(base_url, "/robots.txt")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Fetch robots.txt
        response = requests.get(robots_url, headers=headers, timeout=10)

        results = {
            "url": url,
            "robots_url": robots_url,
            "status_code": response.status_code,
            "exists": response.status_code == 200,
        }

        if response.status_code == 200:
            robots_content = response.text
            results["content"] = robots_content
            results["size"] = len(robots_content)

            # Parse robots.txt
            lines = robots_content.split("\n\nrobots_txt_tester_bp = Blueprint("robots_txt_tester", __name__, url_prefix="/tools")\n\n")
            directives = []
            current_user_agent = None

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if ":" in line:
                    directive, value = line.split(":", 1)
                    directive = directive.strip().lower()
                    value = value.strip()

                    directives.append(
                        {
                            "line": line_num,
                            "directive": directive,
                            "value": value,
                            "original": line,
                        }
                    )

                    if directive == "user-agent":
                        current_user_agent = value

            results["directives"] = directives

            # Check for common issues
            issues = []
            if not any(d["directive"] == "user-agent" for d in directives):
                issues.append("No User-agent directive found")

            if not any(d["directive"] in ["allow", "disallow"] for d in directives):
                issues.append("No Allow or Disallow directives found")

            # Check for sitemap
            sitemap_found = any(d["directive"] == "sitemap" for d in directives)
            if not sitemap_found:
                issues.append("No Sitemap directive found")

            results["issues"] = issues
            results["sitemap_declared"] = sitemap_found

            # Try to parse with robotparser
            try:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(robots_url)
                rp.read()

                # Test common user agents
                test_agents = ["*", "Googlebot", "Bingbot", "Slurp"]
                agent_tests = {}

                for agent in test_agents:
                    can_fetch_root = rp.can_fetch(agent, base_url + "/")
                    can_fetch_admin = rp.can_fetch(agent, base_url + "/admin/")

                    agent_tests[agent] = {
                        "can_fetch_root": can_fetch_root,
                        "can_fetch_admin": can_fetch_admin,
                    }

                results["agent_tests"] = agent_tests

            except Exception as e:
                results["parser_error"] = str(e)

        else:
            results["content"] = None
            results["error"] = f"Robots.txt not found (HTTP {response.status_code})"

        return results

    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}


@robots_txt_tester_bp.route("/robots-txt-tester", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def robots_txt_tester():
    csrf_token = generate_csrf()
    form = RobotsForm()
    return render_template(
        "tools/robots_txt_tester.html", form=form, csrf_token=csrf_token
    )


@robots_txt_tester_bp.route("/robots-txt-tester/ajax", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def robots_txt_tester_ajax():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    try:
        results = test_robots_txt(url)
        if "error" in results:
            return jsonify({"success": False, "error": results["error"]}), 400

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@robots_txt_tester_bp.route("/robots-txt-tester/")
def robots_txt_tester_page():
    """Robots Txt Tester main page."""
    return render_template("tools/robots_txt_tester.html", csrf_token=generate_csrf())

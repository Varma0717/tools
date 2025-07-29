from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_wtf.csrf import generate_csrf
from app.utils.auth_decorators import freemium_tool
from app.core.extensions import csrf
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import time

broken_link_checker_bp = Blueprint("broken_link_checker", __name__, url_prefix="/tools")


class BrokenLinkForm(FlaskForm):
    url = StringField("Website URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Check for Broken Links")


def check_link_status(url, timeout=10):
    """Check if a single link is working"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return {
            "url": url,
            "status_code": response.status_code,
            "status": "working" if response.status_code < 400 else "broken",
            "redirect_url": response.url if response.url != url else None,
        }
    except requests.RequestException:
        try:
            # Try GET request if HEAD fails
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            return {
                "url": url,
                "status_code": response.status_code,
                "status": "working" if response.status_code < 400 else "broken",
                "redirect_url": response.url if response.url != url else None,
            }
        except requests.RequestException as e:
            return {
                "url": url,
                "status_code": None,
                "status": "broken",
                "error": str(e),
            }


def find_broken_links(url, limit=50):
    """Find broken links on a webpage"""
    try:
        # Add protocol if missing
        if not url.startswith(("http:/", "https:/")):
            url = "https:/" + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Get the main page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Find all links
        links = set()

        # Find anchor links
        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if href and not href.startswith(("#", "mailto:", "tel:", "javascript:")):
                absolute_url = urljoin(url, href)
                links.add(absolute_url)

        # Limit the number of links to check
        links = list(links)[:limit]

        # Check links concurrently
        results = {
            "url": url,
            "total_links": len(links),
            "working_links": [],
            "broken_links": [],
            "redirect_links": [],
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(check_link_status, link): link for link in links
            }

            for future in concurrent.futures.as_completed(future_to_url, timeout=60):
                try:
                    result = future.result()
                    if result["status"] == "working":
                        if result.get("redirect_url"):
                            results["redirect_links"].append(result)
                        else:
                            results["working_links"].append(result)
                    else:
                        results["broken_links"].append(result)
                except Exception as e:
                    url_checked = future_to_url[future]
                    results["broken_links"].append(
                        {"url": url_checked, "status": "broken", "error": str(e)}
                    )

        # Summary statistics
        results["summary"] = {
            "total": len(links),
            "working": len(results["working_links"]),
            "broken": len(results["broken_links"]),
            "redirects": len(results["redirect_links"]),
        }

        return results

    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}


@broken_link_checker_bp.route("/broken-link-checker/", methods=["GET"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def broken_link_checker():
    csrf_token = generate_csrf()
    form = BrokenLinkForm()
    return render_template(
        "tools/broken_link_checker.html", form=form, csrf_token=csrf_token
    , csrf_token=generate_csrf())


@broken_link_checker_bp.route("/broken-link-checker/ajax", methods=["POST"])
@freemium_tool(requires_login=False, is_premium=False, free_limit=5)
def broken_link_checker_ajax():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    try:
        results = find_broken_links(url)
        if "error" in results:
            return jsonify({"success": False, "error": results["error"]}), 400

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@broken_link_checker_bp.route("/broken-link-checker/")
def broken_link_checker_page():
    """Broken Link Checker main page."""
    return render_template("tools/broken_link_checker.html", csrf_token=generate_csrf())

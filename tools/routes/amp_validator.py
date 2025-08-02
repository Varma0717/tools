from flask import Blueprint, render_template, request, flash

from flask_wtf import FlaskForm

from flask_login import current_user, login_required, login_user, logout_user

from wtforms import StringField, SubmitField

from wtforms.validators import DataRequired, URL

from flask_wtf.csrf import CSRFProtect

import requests

import re


csrf = CSRFProtect()


amp_validator_bp = Blueprint("amp_validator", __name__, url_prefix="/tools")


class AMPValidatorForm(FlaskForm):

    url = StringField("AMP Page URL", validators=[DataRequired(), URL()])

    submit = SubmitField("Validate AMP")


def validate_amp(url):

    try:

        headers = {"User-Agent": "Mozilla/5.0"}

        resp = requests.get(url, headers=headers, timeout=8)

        if resp.status_code != 200:

            return {"valid": False, "msg": f"URL returned {resp.status_code} status."}

        # AMP validation: Look for required AMP scripts and doctype

        html = resp.text

        amp_tag = re.search(r"<html[^>]+(⚡|amp)[^>]*>", html, re.IGNORECASE)

        amp_script = re.search(
            r'<script[^>]+src="https://cdn.ampproject.org/v0.js"[^>]*>',
            html,
            re.IGNORECASE,
        )

        amp_boilerplate = re.search(
            r"<style[^>]*amp-boilerplate[^>]*>", html, re.IGNORECASE
        )

        if amp_tag and amp_script and amp_boilerplate:

            return {
                "valid": True,
                "msg": "This page is AMP valid (basic static check passed).",
            }

        return {
            "valid": False,
            "msg": "AMP tags or scripts not found. Page is not AMP valid.",
        }

    except Exception as e:

        return {"valid": False, "msg": f"Error: {str(e)}"}


@amp_validator_bp.route("/amp-validator", methods=["GET", "POST"])
@login_required
@csrf.exempt
def amp_validator():

    form = AMPValidatorForm()

    result = None

    if form.validate_on_submit():

        url = form.url.data.strip()

        result = validate_amp(url)

        if not result.get("valid"):

            flash(result.get("msg"), "danger")

    return render_template("tools/amp_validator.html", form=form, result=result)

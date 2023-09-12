# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .. import admin
from ...decorators import check_if_admin
from ...misc import get_internal_api_header

from ...auth.forms import UserAccountRegistrationForm, UserAccountEditForm
from ..forms import AdminUserAccountEditForm, ForgetPasswordForm
from ..forms.auth import AccountLockPasswordForm
from ...sample.enums import (
    SampleBaseType,
    FluidSampleType,
    CellSampleType,
    MolecularSampleType,
    ContainerBaseType,
    FluidContainer,
    CellContainer,
)
from ...database import TemporaryStore, db, UserAccount

from flask import render_template, url_for, redirect, abort, flash, current_app, request
from flask_login import current_user, login_required

from ...extensions import mail

import requests

from flask_mail import Message


@admin.route("/auth/", methods=["GET"])
@check_if_admin
@login_required
def auth_index():
    return render_template("admin/auth/index.html")


@admin.route("/auth/new", methods=["GET", "POST"])
@check_if_admin
@login_required
def auth_new_account():
    sites_response = requests.get(
        url_for("api.site_home", _external=True), headers=get_internal_api_header()
    )

    if sites_response.status_code == 200:
        sites = []

        for site in sites_response.json()["content"]:
            sites.append(
                [int(site["id"]), "LIMBSIT-%s: %s" % (site["id"], site["name"])]
            )

        form = UserAccountRegistrationForm(sites, with_type=True)

        if form.validate_on_submit():
            new_user_response = requests.post(
                url_for("api.auth_new_user", _external=True),
                json={
                    "title": form.title.data,
                    "first_name": form.first_name.data,
                    "middle_name": form.middle_name.data,
                    "last_name": form.last_name.data,
                    "email": form.email.data,
                    "account_type": form.type.data,
                    "password": form.password.data,
                    "site_id": form.site.data,
                },
                headers=get_internal_api_header(),
            )

            if new_user_response.status_code == 200:
                flash("User successfully added!")
                return redirect(url_for("admin.auth_index"))
            else:
                flash("We have encountered a problem :(")

        return render_template("/admin/auth/new.html", form=form)
    else:
        return abort(500)


@admin.route("/auth/<id>", methods=["GET", "POST"])
@check_if_admin
@login_required
def auth_view_account(id):
    response = requests.get(
        url_for("api.auth_view_user", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        form = AccountLockPasswordForm(response.json()["content"]["email"])

        if form.validate_on_submit():
            lock_response = requests.put(
                url_for("api.auth_lock_user", id=id, _external=True),
                headers=get_internal_api_header(),
            )

            if lock_response.status_code == 200:
                if lock_response.json()["content"]["is_locked"]:
                    flash("User Account locked!")
                else:
                    flash("User Account unlocked!")
                return redirect(url_for("admin.auth_index"))
            else:
                flash("We were unable to unlock the User Account.")

        return render_template(
            "admin/auth/view.html", user=response.json()["content"], form=form
        )
    else:
        return abort(response.status_code)


@admin.route("/auth/data", methods=["GET"])
@check_if_admin
@login_required
def auth_data():
    auth_response = requests.get(
        url_for("api.auth_home", _external=True),
        headers=get_internal_api_header(),
    )

    sites_response = requests.get(
        url_for("api.site_home_tokenuser", _external=True),
        headers=get_internal_api_header(),
    )

    if sites_response.status_code == 200:
        sites = sites_response.json()["content"]["choices"]
        sites_dict = {s[0]: s[1] for s in sites}
    else:
        sites_dict = None

    if auth_response.status_code == 200:
        auth_info = auth_response.json()["content"]

        for user in auth_info:
            # Default
            try:
                user["affiliated_site"] = sites_dict[user["site_id"]]
                user["working_sites"] = [user["affiliated_site"]]
            except:
                user["affiliated_site"] = user["site_id"]
                user["working_sites"] = [user["site_id"]]

            try:
                if "view_only" in user["settings"]:
                    entry_key = "view_only"
                elif "data_entry" in user["settings"]:
                    entry_key = "data_entry"
                else:
                    entry_key = None
                if entry_key:
                    user["working_sites"] = [
                        sites_dict[s]
                        for s in user["settings"][entry_key]["site"]["choices"]
                    ]

            except:
                pass
        # print("auth_info_final", auth_info)
        return {"content": auth_info, "success": True}

    return auth_response.content


@admin.route("/auth/<id>/password/reset", methods=["GET", "POST"])
@check_if_admin
@login_required
def admin_password_reset(id):
    response = requests.get(
        url_for("api.auth_view_user", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        form = AccountLockPasswordForm(response.json()["content"]["email"])

        if form.validate_on_submit():
            token_email = requests.post(
                url_for("api.auth_password_reset", _external=True),
                headers=get_internal_api_header(),
                json={"email": form.email.data},
            )

            if token_email.status_code == 200:
                token = token_email.json()["content"]["token"]
                confirm_url = url_for(
                    "auth.change_password_external", token=token, _external=True
                )
                template = render_template(
                    "admin/auth/email/password_reset.html", reset_url=confirm_url
                )
                subject = "LIMBUS: Password Reset Email"
                msg = Message(
                    subject,
                    recipients=[form.email.data],
                    html=template,
                    sender=current_app.config["MAIL_USERNAME"],
                )
                mail.send(msg)
                flash("Password reset email has been sent!")
                return redirect(url_for("admin.auth_view_account", id=id))
            else:
                flash(token_email["content"])

        return render_template(
            "admin/auth/password_reset.html", user=response.json()["content"], form=form
        )
    else:
        return abort(response.status_code)


def populate_settings(
    settings_data,
    default_sites,
    item_list,
    sites=[],
    consent_templates=[],
    study_protocols=[],
    collection_protocols=[],
    processing_protocols=[],
):
    """
    Input:
        settings_data: settings (json format) obtained from the user account in the database
        default_sites: [default_site]
        item_list: list of items to be processed and populated
    Return:
        settings: reformated settings (in list) to be used in form AdminUserAccountEditForm and UserSettings.
    """

    def flatten_settings(name, settings_val, choices=[], setting={}):
        name_choices = name + "_choices"
        name_default = name + "_default"
        name_selected = name + "_selected"
        try:
            setting[name_choices] = settings_val["choices"]

            if setting[name_choices] is None or len(setting[name_choices]) == 0:
                setting[name_choices] = [s[0] for s in choices]
        except:
            setting[name_choices] = [s[0] for s in choices]

        try:
            setting[name_default] = settings_val["default"]
            if setting[name_default] not in setting[name_choices]:
                setting[name_default] = setting[name_choices][0]

        except:
            setting[name_default] = None

        setting[name_selected] = "\n".join(
            [s[1] for s in choices if s[0] in setting[name_choices]]
        )

        return setting

    if item_list is None:
        item_list = [
            "site",
            "consent_template",
            "study_protocol",
            "collection_protocol",
            "processing_protocol",
            "sample_basetype",
            "sample_flu_type",
            "sample_cel_type",
            "sample_mol_type",
            "container_basetype",
            "prm_container",
            "lts_container",
        ]

    settings = []
    for access_type in settings_data:
        setting = {}
        for k in item_list:
            setting.update({k + "_choices": [], k + "_default": None})
            setting.update({k + "_selected": []})

        if access_type == "data_entry":
            setting["access_level"] = 1
        else:  # if access_type == "view_only":
            setting["access_level"] = 2

        # -- Working sites
        # -- Default working site is the site for the user account
        try:
            setting["site_choices"] = settings_data[access_type]["site"]["choices"]
            if setting["site_choices"] is None or len(setting["site_choices"]) == 0:
                setting["site_choices"] = default_sites
        except:
            setting["site_choices"] = default_sites

        setting["site_selected"] = "\n".join(
            [s[1] for s in sites if s[0] in setting["site_choices"]]
        )

        # -- Consent templates
        if "consent_template" in item_list:
            try:
                # settings_val = account_data["settings"][access_type]["consent_template"]
                settings_val = settings_data[access_type]["consent_template"]
                setting = flatten_settings(
                    name="consent_template",
                    settings_val=settings_val,
                    choices=consent_templates,
                    setting=setting,
                )
            except:
                pass

        # -- Study protocols
        if "study_protocol" in item_list:
            try:
                settings_val = settings_data[access_type]["protocol"]["STU"]
                setting = flatten_settings(
                    name="study_protocol",
                    settings_val=settings_val,
                    choices=study_protocols,
                    setting=setting,
                )
            except:
                pass

        # -- Sample collection/acquisition protocols
        if "collection_protocol" in item_list:
            try:
                settings_val = settings_data[access_type]["protocol"]["ACQ"]
                setting = flatten_settings(
                    name="collection_protocol",
                    settings_val=settings_val,
                    choices=collection_protocols,
                    setting=setting,
                )
            except:
                pass

        # -- Sample processsing protocols
        if "processing_protocol" in item_list:
            try:
                settings_val = settings_data[access_type]["protocol"]["SAP"]
                setting = flatten_settings(
                    name="processing_protocol",
                    settings_val=settings_val,
                    choices=processing_protocols,
                    setting=setting,
                )
            except:
                pass

        # -- Sample base type
        if "sample_basetype" in item_list:
            try:
                settings_val = settings_data[access_type]["sample_type"]["base_type"]
                setting = flatten_settings(
                    name="sample_basetype",
                    settings_val=settings_val,
                    choices=SampleBaseType.choices(),
                    setting=setting,
                )
            except:
                pass

        # -- Sample fluid type
        if "sample_flu_type" in item_list:
            try:
                settings_val = settings_data[access_type]["sample_type"]["FLU"]
                setting = flatten_settings(
                    name="sample_flu_type",
                    settings_val=settings_val,
                    choices=FluidSampleType.choices(),
                    setting=setting,
                )
            except:
                pass

        # -- Sample solid (cell) type
        if "sample_cel_type" in item_list:
            try:
                settings_val = settings_data[access_type]["sample_type"]["CEL"]
                setting = flatten_settings(
                    name="sample_cel_type",
                    settings_val=settings_val,
                    choices=CellSampleType.choices(),
                    setting=setting,
                )
            except:
                pass

        # -- Sample molecular type
        if "sample_mol_type" in item_list:
            try:
                settings_val = settings_data[access_type]["sample_type"]["MOL"]
                setting = flatten_settings(
                    name="sample_mol_type",
                    settings_val=settings_val,
                    choices=MolecularSampleType.choices(),
                    setting=setting,
                )
            except:
                pass

        # -- Sample container basetype
        if "container_basetype" in item_list:
            try:
                settings_val = settings_data[access_type]["container_type"]["base_type"]
                setting = flatten_settings(
                    name="container_basetype",
                    settings_val=settings_val,
                    choices=ContainerBaseType.choices(),
                    setting=setting,
                )
            except:
                pass

        # -- Sample primary container types
        if "prm_container" in item_list:
            try:
                settings_val = settings_data[access_type]["container_type"]["PRM"][
                    "container"
                ]
                setting = flatten_settings(
                    name="prm_container",
                    settings_val=settings_val,
                    choices=FluidContainer.choices(),
                    setting=setting,
                )
            except:
                pass

        # -- Sample long term storage (lts) container types
        if "lts_container" in item_list:
            try:
                settings_val = settings_data[access_type]["container_type"]["LTS"][
                    "container"
                ]
                setting = flatten_settings(
                    name="lts_container",
                    settings_val=settings_val,
                    choices=CellContainer.choices(),
                    setting=setting,
                )
            except:
                pass

        # print("setting: ", setting)
        settings.append(setting)

    return settings


def jsonise_settings(form, account_data):
    for setting in form.settings.entries:
        site_choices = []
        if len(setting.site_choices.data) > 0:
            site_choices = [
                int(k)
                for k in setting.site_choices.data
                if int(k) != account_data["site_id"]
            ]
            site_choices = [account_data["site_id"]] + site_choices

        settings = {}
        if setting.access_level.data == 2:
            settings["view_only"] = {"site": {"choices": site_choices}}

        else:
            settings["data_entry"] = {"site": {"choices": site_choices}}

            settings["data_entry"].update(
                {
                    "consent_template": {
                        "choices": setting.consent_template_choices.data,
                        "default": setting.consent_template_default.data,
                    },
                    "protocol": {
                        "STU": {
                            "choices": setting.study_protocol_choices.data,
                            "default": setting.study_protocol_default.data,
                        },
                        "ACQ": {
                            "choices": setting.collection_protocol_choices.data,
                            "default": setting.collection_protocol_default.data,
                        },
                        "SAP": {
                            "choices": setting.processing_protocol_choices.data,
                            "default": setting.processing_protocol_default.data,
                        },
                    },
                }
            )

            settings["data_entry"].update(
                {
                    "sample_type": {
                        "base_type": {"default": setting.sample_basetype_default.data},
                        "FLU": {
                            "default": setting.sample_flu_type_default.data,
                            "choices": [],
                        },
                        "CEL": {
                            "default": setting.sample_cel_type_default.data,
                            "choices": [],
                        },
                        "MOL": {
                            "default": setting.sample_mol_type_default.data,
                            "choices": [],
                        },
                    }
                }
            )

            settings["data_entry"].update(
                {
                    "container_type": {
                        "base_type": {
                            "default": setting.container_basetype_default.data
                        },
                        "PRM": {
                            "container": {
                                "default": setting.prm_container_default.data
                            },
                            # "fixation_type": {}
                        },
                        "LTS": {
                            "container": {
                                "default": setting.lts_container_default.data
                            },
                            # "fixation_type": {}
                        },
                    }
                }
            )

        # print("template: ", setting.saveto_template_name.data)
        if setting.saveto_template_name.data not in [None, ""]:
            settings["template_name"] = setting.saveto_template_name.data

    return settings


@admin.route("/auth/<id>/edit_settings", methods=["GET", "POST"])
@admin.route("/auth/<id>/edit_settings/<use_template>", methods=["GET", "POST"])
@check_if_admin
@login_required
def admin_edit_settings(id, use_template=None):
    response = requests.get(
        url_for("api.auth_view_user", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    sites_response = requests.get(
        url_for("api.site_home_tokenuser", _external=True),
        headers=get_internal_api_header(),
    )

    # sites=[0, None]
    if sites_response.status_code == 200:
        sites = sites_response.json()["content"]["choices"]
    else:
        flash("No site created!")
        return render_template(
            "admin/auth/edit.html", user=response.json()["content"], form={}
        )

    consent_templates_response = requests.get(
        url_for("api.consent_query_tokenuser", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False},
    )

    if consent_templates_response.status_code == 200:
        consent_templates = consent_templates_response.json()["content"]["choices"]

    protocols_response = requests.get(
        url_for("api.protocol_query_tokenuser", default_type="STU", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False, "type": ["STU"]},
    )

    study_protocols = []
    if protocols_response.status_code == 200:
        study_protocols = protocols_response.json()["content"]["choices"]

    protocols_response = requests.get(
        url_for("api.protocol_query_tokenuser", default_type="ACQ", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False, "type": ["ACQ"]},
    )

    collection_protocols = []
    if protocols_response.status_code == 200:
        collection_protocols = protocols_response.json()["content"]["choices"]

    protocols_response = requests.get(
        url_for("api.protocol_query_tokenuser", default_type="SAP", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False, "type": ["SAP"]},
    )

    processing_protocols = []
    if protocols_response.status_code == 200:
        processing_protocols = protocols_response.json()["content"]["choices"]

    setting_templates = [(None, "None")]
    templates = TemporaryStore.query.filter_by(type="SET").all()
    if len(templates) > 0:
        setting_templates = setting_templates + [(s.uuid, s.uuid) for s in templates]

    if response.status_code == 200:
        account_data = response.json()["content"].copy()
        site_id = int(account_data["site"]["id"])
        account_data.update({"site_id": site_id})
        settings0 = account_data.pop("settings", None)

        default_sites = [site_id]
        # -- prepare data population to the form
        # -- currently only either "data_entry" or "view_only", not both can be stored in the DB

        if use_template:  # Use template
            for tmpl in templates:
                if tmpl.uuid == use_template:
                    settings = populate_settings(
                        tmpl.data,
                        default_sites,
                        None,
                        sites,
                        consent_templates,
                        collection_protocols,
                        processing_protocols,
                    )

                    account_data["settings"] = settings
                    account_data["use_template"] = use_template

        elif settings0:  # Current settings
            account_data["settings"] = settings0
            settings = populate_settings(
                settings0,
                default_sites,
                None,
                sites,
                consent_templates,
                collection_protocols,
                processing_protocols,
            )

            account_data["settings"] = settings

        else:
            account_data["settings"] = [
                {
                    "access_level": 1,
                    "site_choices": default_sites,
                    "site_selected": [s[1] for s in sites if s[0] == site_id][0],
                }
            ]

        form = AdminUserAccountEditForm(sites=sites, data=account_data)

        form.use_template.choices = setting_templates
        for setting in form.settings.entries:
            setting.site_choices.choices = sites
            # setting.site_default.choices = sites
            setting.consent_template_choices.choices = consent_templates
            setting.consent_template_default.choices = consent_templates

            setting.study_protocol_choices.choices = study_protocols
            setting.study_protocol_default.choices = study_protocols

            setting.collection_protocol_choices.choices = collection_protocols
            setting.collection_protocol_default.choices = collection_protocols

            setting.processing_protocol_choices.choices = processing_protocols
            setting.processing_protocol_default.choices = processing_protocols

        if (
            form.validate_on_submit()
            and form.use_template.data is not None
            and form.set_to_template.data
        ):
            if form.use_template.data in [None, "None"]:
                return redirect(url_for("admin.admin_edit_settings", id=id))

            else:
                return redirect(
                    url_for(
                        "admin.admin_edit_settings",
                        id=id,
                        use_template=form.use_template.data,
                    )
                )

        elif form.validate_on_submit() and form.submit.data:
            json = {
                "title": form.title.data,
                "first_name": form.first_name.data,
                "middle_name": form.middle_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "account_type": form.account_type.data,
                # "password": form.password.data,
                "site_id": form.site_id.data,
            }

            settings = jsonise_settings(form, account_data)
            json["settings"] = settings  # There is only one settings entry

            edit_response = requests.put(
                url_for("api.admin_edit_account", id=id, _external=True),
                headers=get_internal_api_header(),
                json=json,
            )

            if edit_response.status_code == 200:
                flash("User account updated successfully!")
                return redirect(url_for("admin.auth_view_account", id=id))
            else:
                flash(edit_response.json()["message"])

        return render_template(
            "admin/auth/edit.html", user=response.json()["content"], form=form
        )
    else:
        return abort(response.status_code)

@admin.route('auth/forget_password', methods=["GET", "POST"])
def auth_forget_password():

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        # get password reset token
        token_email = requests.post(
            url_for("api.auth_forget_password", _external=True),
            headers={"FlaskApp": current_app.config.get("SECRET_KEY"), "Email": form.email.data},
            json={"email": form.email.data},
        )

        if token_email.status_code == 200:
            token = token_email.json()["content"]["token"]
            confirm_url = url_for(
                "auth.change_password_external", token=token, _external=True
            )
            template = render_template(
                "admin/auth/email/password_reset.html", reset_url=confirm_url
            )
            subject = "LIMBUS: Password Reset Email"
            msg = Message(
                subject,
                recipients=[form.email.data],
                html=template,
                sender=current_app.config["MAIL_USERNAME"],
            )

            # Send password reset email
            mail.send(msg)
            flash("Password reset email has been sent!")
            return redirect(url_for("auth.login"))

        else:
            flash(token_email.json()["message"])


    return render_template("admin/auth/forget_password.html", form=form)
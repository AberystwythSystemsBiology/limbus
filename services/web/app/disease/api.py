# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
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

from flask import request
from .owl import load_doid
from ..api import api, get_filters_and_joins
from ..api.responses import *
from ..decorators import token_required
from ..api.responses import *
from ..auth.models import UserAccount

from owlready2.entity import ThingClass

DOID, obo = load_doid()


def prepare_instance(thing: ThingClass):
    def _get_parents(thing, ret):
        if len(ret) == 0:
            pass

    def _resolve_references(hasDbXref):
        reference_dictionary = {}

        resolutions = {
            "ICDO": "http://www.wolfbane.com/icd/icdo.htm#%s",
            "EFO": "https://www.ebi.ac.uk/ols/ontologies/efo/terms?short_form=EFO_%s",
            "ORDO": "https://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=GB&Expert=%s",
            "KEGG": "https://www.kegg.jp/kegg-bin/show_pathway?%s",
            "ICD10CM": "https://icdlist.com/icd-10/%s",
            "ICD9CM": "https://icdlist.com/icd-9/%s",
            "UMLS_CUI": "https://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI%20Thesaurus&code=%s",
            "OMIM": "https://www.omim.org/entry/%s",
            "SNOMEDCT_US_2020_03_01": "https://snomedbrowser.com/Codes/Details/%s",
            "SNOMEDCT_US_2018_03_01": "https://snomedbrowser.com/Codes/Details/%s",  ##??
            "MESH": "https://meshb.nlm.nih.gov/record/ui?ui=%s",
            "GARD": "https://rarediseases.info.nih.gov/diseases/%s/index",
            "NCI": "https://nciterms.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&version=20.07d&code=%s&ns=ncit",
        }

        for reference in hasDbXref:
            db, identifier = reference.split(":")
            try:
                reference_dictionary[reference] = {
                    "self": resolutions[db] % (str(identifier))
                }
            except:  # ValueError:
                pass

        return reference_dictionary

    return {
        "iri": thing.iri,
        "name": thing.name,
        "description": thing.IAO_0000115,
        "synonyms": thing.hasExactSynonym,
        "label": thing.label.first() or instance.name,
        "references": _resolve_references(thing.hasDbXref),
    }


def retrieve_by_iri(iri: str) -> dict:
    thing = DOID.search_one(iri=iri)

    if thing != None:
        return prepare_instance(thing)

    return thing


def retrieve_by_label(label: str):
    # results = DOID.search(label="*%s" % (label), subclass_of=obo.DOID_4)
    results = DOID.search(
        label="*%s*" % (label), subclass_of=obo.DOID_4, _case_sensitive=False
    )

    results_dict = {}

    for thing in results:
        results_dict[thing.iri] = prepare_instance(thing)

    return results_dict


@api.route("/disease/query/validate_label", methods=["GET"])
@token_required
def doid_validate_by_iri(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    thing = retrieve_by_iri(values["iri"])

    success = True
    response = 200

    if thing == None:
        success = False
        response += 300

    return {"success": success, "iri": values["iri"], "thing": thing}, response


@api.route("/disease/query/name", methods=["post"])
@token_required
def doid_query_by_label(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    return success_with_content_response(retrieve_by_label(values["label"]))

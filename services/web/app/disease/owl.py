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

from owlready2 import get_ontology, onto_path, get_namespace, Thing
import os

onto_path.append(os.environ["ONTOLOGY_DIRECTORY"])


def load_doid():
    onto = get_ontology(os.environ["DOID_PATH"]).load()
    obo = get_namespace("http://purl.obolibrary.org/obo/")
    doid = get_namespace("http://purl.obolibrary.org/obo/doid")
    subclasses = onto.get_children_of(Thing)
    # subclasses = [obo.UBERON_0001062, obo.CL_0000000, # anatomy, cellular
    #               obo.DOID_4, #obo.DISDRIV_0000000, # disease, disease caused by
    #               obo.OMIM_000000, # cancer types
    #               obo.SYMP_0000462, obo.TRANS_0000000, # symptoms, transmission
    #               obo.GENO_0000141, #
    #               obo.NCBITaxon_1, # organism taxonomy (bacteria, virus, ...)
    #               doid.chebi, obo.FOODON_00002403, # drug, and food/supplement
    #               obo.ECO_0000000,
    #               # obo.HP_0003674,
    #               obo.UPHENO_0001001,
    #               doid.sequence
    #               ]
    return onto, obo, doid, subclasses

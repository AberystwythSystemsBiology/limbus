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

from ..FormEnum import FormEnum


class SampleQuality(FormEnum):
    GOO = "Good"
    BAD = "Bad"
    DAM = "Damaged"
    UNU = "Unusable"
    NOT = "Not Specified"


class Colour(FormEnum):
    BLU = "Blue"
    RED = "Red"
    GRE = "Green"
    YEL = "Yellow"
    GRY = "Grey"


class SampleSource(FormEnum):
    NEW = "New"
    ALI = "Aliquot"
    DER = "Derivative"


class SampleType(FormEnum):
    FLU = "Fluid"
    CEL = "Cell"
    MOL = "Molecular"


class BiohazardLevel(FormEnum):
    ONE = "Level One"
    TWO = "Level Two"
    THR = "Level Three"
    FOU = "Level Four"


class FluidSampleType(FormEnum):
    ASC = "Ascites fluid"
    AMN = "Amniotic fluid"
    BAL = "Bronchoalveolar lavage"
    BLD = "Blood (whole)"
    BMA = "Bone marrow aspirate"
    BMK = "Breast milk"
    BUC = "Buccal cells"
    BILE = "Bile"
    BUF = "Unficolled buffy coat, viable"
    BFF = "Unficolled buffy coat, non-viable"
    BCF = "Body Cavity Fluid"
    BMP = "Bone Marrow Plasma"
    CER = "Cerebrospinal Fluid"
    FEC = "Feces"
    GAF = "Gastric Fluid"
    LAV = "Lavage"
    MIL = "Milk"
    CEL = "Ficoll mononuclear cells, viable"
    CEN = "Fresh cells from non-blood specimen type"
    RNA = "RNALater"
    PLA = "Plasma"
    SAL = "Saliva"
    SER = "Serum"
    SPU = "Sputum"
    SWE = "Sweat"
    SYN = "Synovial Fluid"
    URI = "Urine"
    VIT = "Vitreous Fluid"


class MolecularSampleType(FormEnum):
    CDN = "cDNA"
    CTD = "ctDNA"
    DNA = "DNA"
    PRO = "Protein"
    RNA = "RNA"
    RNC = "RNA, cytoplasmic"
    RNM = "RNA, nulcear"
    RNP = "RNA, poly-A enriched"
    TNA = "Total Nucleic Acid"
    WGA = "Whole Genome Amplified DNA"


class CellSampleType(FormEnum):
    CYO = "Cyropreserved Cells"
    FXB = "Fixed Cell Block"
    FCB = "Frozen Cell Block"
    FCP = "Frozen Cell Pellet"
    PRM = "PMRC"
    SLI = "Slide"


class TissueSampleType(FormEnum):
    FIX = "Fixed Tissue"
    FTB = "Fixed Tissue Block"
    FTS = "Fixed Tissue Slide"
    FRE = "Fresh Tissue"
    FRO = "Frozen Tissue"
    FROTB = "Frozen Tissue Block"
    FROTS = "Frozen Tissue Slide"
    MDS = "Microdissected"


class DisposalInstruction(FormEnum):
    NAP = "No Disposal"
    DES = "Destroy"
    TRA = "Transfer"
    REV = "Review"
    PRE = "Preserve"


class SampleStatus(FormEnum):
    AVA = "Available"
    DES = "Destroyed"
    TRA = "Transferred"
    MIS = "Missing"
    NPR = "Not Processed"

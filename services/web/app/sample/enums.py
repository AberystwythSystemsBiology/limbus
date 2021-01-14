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


class ReviewType(FormEnum):
    PC = "Purity Check"
    QC = "Quality Check"
    IC = "Identity Check"


class ReviewResult(FormEnum):
    PA = "Pass"
    FA = "Fail"
    UN = "Unknown"


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


class SampleBaseType(FormEnum):
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


class CellContainer(FormEnum):
    CEN = "Fresh cells from non-blood specimen type"
    CLN = "Cells from non-blood specimen type, viable"
    FNA = "Cells from fine needle aspirate"
    HAR = "Hair"
    LCM = "Cells from laser capture microdissected tissue"
    PEN = "Cells from non-blood specimen type (e.g. dissociated tissue), non viable"
    PLC = "Placenta"
    TIS = "Solid tissue"
    TCM = "Disrupted tissue, non-viable"
    ZZZ = "Other"


class FixationType(FormEnum):
    ACA = "Non-aldehyde with acetic acid"
    ALD = "Aldehyde-based"
    ALL = "Allprotect tissue reagent"
    ETH = "Alcohol-based"
    FOR = "Non-buffered formalin"
    HST = "Heat stabilisation"
    SNP = "Snap freezing"
    NAA = "Non-aldehyde based without acetic acid"
    NBF = "Neutral buffered formalin"
    OCT = "Optimum cutting temperature medium"
    PXT = "PAXgene Tissue"
    RNL = "RNA Later"
    XXX = "Unknown"
    ZZZ = "Other"


class FluidContainer(FormEnum):
    ACD = "Acid citrate dextrose"
    ADD = "Additives"
    CAT = "Serum tube without clot activator"
    CPD = "Citrate phosphate dextrose"
    CPT = "Cell Preparation Tube"
    EDG = "EDTA and gel"
    HEP = "Lithium heparin"
    HIR = "Hirudin"
    LHG = "Lithium heparin and gel"
    ORG = "Oragene collection container or equivalent"
    PAX = "PAXgene blood RNA+"
    PED = "Potassium EDTA"
    PET = "Polyethylene tube sterile"
    PIONE = "S8820 protease inhibitor tablets or equivalent"
    PIX = "Protease inhibators"
    PPS = "Polypropylene tube sterile"
    PXD = "PAXgene blood DNA"
    PXR = "PAXgene bone marrow RNA"
    SCI = "Sodium citrate"
    SED = "Sodium EDTA"
    SHP = "Sodium heparin"
    SPO = "Sodium fluoride/potassium oxalate"
    SST = "Serum seperator tube with clot activator"
    TEM = "Tempus tube"
    TRC = "Trace element tube"
    XXX = "Unknown"
    ZZZ = "Other"


class SampleStatus(FormEnum):
    AVA = "Available"
    DES = "Destroyed"
    UNU = "Unusable"
    TRA = "Transferred"
    MIS = "Missing"
    TMP = "Temporary Storage"
    NCO = "Not Collected"
    NPR = "Not Processed"
    NRE = "Pending Review"

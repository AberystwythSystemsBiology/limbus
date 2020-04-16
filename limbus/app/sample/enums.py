from enum import Enum
from ..FormEnum import FormEnum


class SampleType(FormEnum):
    FLU = "Fluid"
    CEL = "Cell"
    MOL = "Molecular"

class FluidSampleType(FormEnum):
    # If Fluid the Quantity == ml

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
    PLA = "Plasma"
    SAL = "Saliva"
    SER = "Serum"
    SPU = "Sputum"
    SWE = "Sweat"
    SYN = "Synovial Fluid"
    URI = "Urine"
    VIT = "Vitreous Fluid"


class MolecularSampleType(FormEnum):
    # If MolecularSample Quantity ==  uberg + concentration? ug/ml
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
    # If Cell Quantity == Cells
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
    DES = "Destroy"
    TRA = "Transfer"
    REV = "Review"
    PRE = "Preserve"


class SampleStatus(FormEnum):
    AVA = "Available"
    DES = "Destroyed"
    TRA = "Transferred"
    MIS = "Missing"


class SampleAttributeTypes(FormEnum):
    OPTION = "Option"
    TEXT = "Text"
    NUMERIC = "Numeric"

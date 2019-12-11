from enum import Enum

class SampleType(Enum):
    FLU = "Fluid"
    TIS = "Tissue"

class FluidSampleType(Enum):
    ASC = "Ascites fluid"
    AMN = "Amniotic fluid"
    BAL = "Bronchoalveolar lavage"
    BLD = "Blood (whole)"
    BMA = "Bone marrow aspirate"
    BMK = "Breast milk"
    BUC = "Buccal cells"
    BUF = "Unficolled buffy coat, viable"
    BFF = "Unficolled buffy coat, non-viable"
    CEL = "Ficoll mononuclear cells, viable"
    CEN = "Fresh cells from non-blood specimen type"

class DisposalInstruction(Enum):
    DES = "Destroy"
    TRA = "Transfer"
    REV = "Note for Review"
    PRE = "Preserve"

class SampleStatus(Enum):
    AVA = "Available"
    DES = "Destroyed"
    TRA = "Transferred"
    MIS = "Missing"
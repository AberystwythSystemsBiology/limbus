from enum import Enum
from ..FormEnum import FormEnum

class SampleType(FormEnum):
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

class DisposalInstruction(FormEnum):
    DES = "Destroy"
    TRA = "Transfer"
    REV= "Review"
    PRE = "Preserve"

class SampleStatus(FormEnum):
    AVA = "Available"
    DES = "Destroyed"
    TRA = "Transferred"
    MIS = "Missing"

class SampleAttributeTypes(Enum):
    OPTION = "Option"
    TEXT = "Text"
    NUMERIC = "Numeric"
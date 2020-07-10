from ..FormEnum import FormEnum


class EntityToStorageTpye(FormEnum):
    STB = "Sample to Box"
    STS = "Sample to Shelf"
    BTS = "Box to Shelf"

class FixedColdStorageType(FormEnum):
    FRI = "Fridge"
    FRE = "Freezer"


class FixedColdStorageTemps(FormEnum):
    L = "-150 to -86°C"
    A = "-85 to -60°C"
    B = "-59 to -35°C"
    C = "-34 to -18°C"
    D = "-17 to -10°C"
    E = "-9 to -5°C"
    F = "-4 to 0°C"


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
    CPD = "Sitrate phosphate dextrose"
    CPT = "Cell Preperation Tube"
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

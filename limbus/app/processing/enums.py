from ..FormEnum import FormEnum

class ProtocolTypes(FormEnum):
    DOC = "Document"
    DIG = "Digital"
    DIC = "Digital and Document"

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


# Replace this with something smarter.
# Something like Room Temp - 2 to 10*C - 35 to 38 C etc...
class ProcessingTemps(FormEnum):
    A = "Room Temperature"
    B = "2 to 10°C"
    C = "-35 to -38°C"
    U = "Unknown"
    O = "Other"


class ProcessingTimes(FormEnum):
    A = "< 2 hours"
    B = "2 to 4 hours"
    C = "8 to 12 hours"
    D = "12 to 24 hours"
    E = "24 to 48 hours"
    F = "> 48 hours"
    U = "Unknown"
    O = "Other"


class CentrifugationTime(FormEnum):
    A = "10 to 15 minutes"
    B = "30 minutes"
    U = "Unknown"
    O = "Other"


class CentrifugationWeights(FormEnum):
    A = "< 3000g"
    B = "3000g to 6000g"
    C = "> 1000g"
    U = "Unknown"
    O = "Other"


class FluidLongTermStorage(FormEnum):
    A = "PP tube 0.5-2mL @ -85 to -60°C"
    B = "PP tube 0.5-2mL @ -35 to -18°C"
    V = "PP tube 0.5-2mL @ < 135°C"
    C = "Cryotube 1-2mL in Liquid Nitrogen"
    D = "Cryotube 1-2mL @ -85 to -60°C"
    E = "Cryotube 1-2mL @ < 135°C"
    F = "Plastic cryo straw in Liquid Nitrogen"
    G = "Straw @ -85 to -60°C"
    H = "Straw @ -35 to -18°C"
    I = "Straw @ < -135°C"
    J = "PP tube > 5mL @ -85 to -60°C"
    K = "PP tube > 5mL @ -35 to -18°C"
    L = "Microplate @ -85 to -60°C"
    M = "Microplate @ -35 to -18°C"
    N = "Cryotube 1-2mL in Liquid Nitrogen"
    O = "Plastic cryo straw in Liquid Nitrogen"
    P = "Paraffin block @ Room Temp or 2 - 10°C"
    Q = "Bag in Liquid Nitrogen"
    R = "Dry technology medium @ Room Temp"
    S = "PP tube 40-500 @ -85 to -60°C"
    T = "PP tube 40-500 @ -35 to -18°C"
    W = "PP tube 40-500μL @ < 135°C"
    Y = "Original Container @ -85 to -18°C"
    X = "Unknown"
    Z = "Other"

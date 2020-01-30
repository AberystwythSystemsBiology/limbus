from ..FormEnum import FormEnum

class DonorRace(FormEnum):
    AONE = "Welsh / English / Scottish / Northern Irish"
    ATWO = "Irish"
    ATHREE = "Gypsy or Irish Traveller"
    AFOUR = "Any Other White Background"
    BONE = "White and Black Caribbean"
    BTWO = "White and Black African"
    BTHREE = "White and Asian"
    BFOUR = "Any Other Mixed / Multiple Ethnic Background"
    CONE = "Indian"
    CTWO = "Pakistani"
    CTHREE = "Bangladeshi"
    CFOUR = "Chinese"
    CFIVE = "Any Other Asian Background"
    DONE = "African"
    DTWO = "Caribbean"
    DTHREE = "Any Other Black / African / Caribbean Background"
    EONE = "Arab"
    ETWO = "Any Other Ethnic Group"

class DonorSex(FormEnum):
    M = "Male"
    F = "Female"

class DonorDiagnosticProcedureType(FormEnum):
    SUR = "Surgery"

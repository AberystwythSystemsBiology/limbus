from ..FormEnum import FormEnum


class RaceTypes(FormEnum):
    A = "White"
    A1 = "Welsh/Englush/Scottish/Northern Irish/British"
    A2 = "Irish"
    A3 = "Gypsy or Irish Traveller"
    A4 = "Any Other White Background"
    B = "Mixed/Multiple Ethnic Groups"
    B1 = "White and Black Caribbean"
    B2 = "White and Black African"
    B3 = "White and Asian"
    B4 = "Any Other Mixed/Multiple Ethnic Background"
    C = "Asian/Asian British"
    C1 = "Indian"
    C2 = "Pakistani"
    C3 = "Bangladeshi"
    C4 = "Chinese"
    C5 = "Any Other Asian Background"
    D = "Black"
    D1 = "African"
    D2 = "Caribbean"
    D3 = "Any Other Black/African/Carbibean Background"
    E = "Other Ethnic Group"
    E1 = "Arab"
    E2 = "Any Other Ethnic Group"
    UNK = "Unknown"


class BiologicalSexTypes(FormEnum):
    M = "Male"
    F = "Female"


class DonorStatusTypes(FormEnum):
    AL = "Alive"
    DE = "Deceased"
    UNK = "Unknown"

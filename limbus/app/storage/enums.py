from ..FormEnum import FormEnum

class FixedColdStorageType(FormEnum):
    FRI = "Fridge"
    FRE = "Freezer"


class FixedColdStorageTemps(FormEnum):
    A = "-85 to -60°C"
    B = "-59 to -35°C"
    C = "-34 to -18°C"
    D = "-17 to -10°C"
    E = "-9 to -5°C"
    F = "-4 to 0°C"
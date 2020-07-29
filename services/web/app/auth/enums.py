from ..FormEnum import FormEnum


class Title(FormEnum):
    MRS = "Mrs."
    MISS = "Miss."
    MS = "Ms."
    MR = "Mr."
    MX = "Mx."
    PROF = "Prof."
    DR = "Dr."


class AccountType(FormEnum):
    ADM = "Administrator"
    BIO = "Biobank Member"
    PRO = "Project Member"
    BOT = "Bot"


class AccessControl(FormEnum):
    ADM = "Administrator"
    MOD = "Moderator"
    PRI = "Privileged"
    VIE = "Viewer"
    BOT = "Bot"

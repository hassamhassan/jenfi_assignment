from enum import Enum as PEnum


class UserRole(str, PEnum):
    TRAIN_OPERATOR = "Train Operator"
    PARCEL_OWNER = "Parcel Owner"
    POST_MASTER = "Post Master"


class TrainStatus(str, PEnum):
    AVAILABLE = "Available"
    BOOKED = "Booked"
    SENT = "Sent"
    UNAVAILABLE = "Unavailable"

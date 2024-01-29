from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from common.enums import TrainStatus
from models.parcel import Parcel
from models.train import Train


async def assign_parcels_to_train(db: Session, train: Train):
    available_parcels = await db.execute(select(Parcel).where(Parcel.train_id.is_(None)))  # noqa
    available_parcels = available_parcels.scalars().all()

    parcels_with_costs = [(parcel, parcel.calculate_shipping_cost(train)) for parcel in available_parcels]

    sorted_parcels = sorted(parcels_with_costs, key=lambda x: x[1])

    for parcel, _ in sorted_parcels:
        if (
                train.current_weight + parcel.weight <= train.max_weight and
                train.current_volume + parcel.volume <= train.max_volume
        ):
            train.current_weight += parcel.weight
            train.current_volume += parcel.volume
            parcel.train_id = train.id
            train.status = TrainStatus.BOOKED
            train.updated_at = datetime.now()

            train.cost += parcel.calculate_shipping_cost(train)

            await db.commit()  # noqa

    return "Parcel assignment completed successfully"

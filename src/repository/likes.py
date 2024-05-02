from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from src.common import detail_message
from src.database.models import ImageLike
from src.database.models import User
from src.schemas.likes import LikeSchema


async def add_grade_to_image(
    image_id: int, body: LikeSchema, db: AsyncSession, current_user: User
) -> ImageLike:
    try:
        image_like = ImageLike(
            user_id=current_user.id, image_id=image_id, grade=body.grade
        )
        db.add(image_like)
        await db.commit()
        await db.refresh(image_like)
        return image_like
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail_message.ONE_LIVE_ONE_GRADE,
        )


async def get_current_rating(image_id: int, db: AsyncSession) -> float:
    result = await db.execute(
        select(func.avg(ImageLike.grade))
        .where(ImageLike.image_id == image_id)
        .group_by(ImageLike.image_id)
    )
    average_rating = result.scalar()
    if average_rating is None:
        return 0

    return round(float(average_rating), 1)

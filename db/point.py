from db.models import Wins

async def add_points(user_id: int, point: int):
    win_record, created = await Wins.get_or_create(user_id=user_id, defaults={'point': point})
    if not created:
        win_record.point += point
        await win_record.save()
    return {"status": "success", "data": f"user {user_id} has been credited with {point} points."}

async def get_points(user_id: int):
    win_record = await Wins.get_or_none(user_id=user_id)
    if win_record:
        return win_record.point
    return 0

async def get_all_points():
    all_records = await Wins.all()
    return {record.user_id: record.point for record in all_records}


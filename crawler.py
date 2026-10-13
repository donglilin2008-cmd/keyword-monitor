
import datetime, random, asyncio
import database

def is_in_schedule(platform):
    if platform["is_all_day"]: return True
    now = datetime.datetime.now()
    weekday = str(now.isoweekday())  # 1=Mon
    if weekday not in platform["weekdays"].split(","):
        return False
    start_h, start_m = map(int, platform["schedule_start"].split(":"))
    end_h, end_m = map(int, platform["schedule_end"].split(":"))
    start = now.replace(hour=start_h, minute=start_m, second=0)
    end = now.replace(hour=end_h, minute=end_m, second=0)
    if end < start: # overnight
        return now >= start or now <= end
    return start <= now <= end

async def crawl_object(object_id: int):
    # Here you would use playwright to check real ranking
    # For demo, return mock
    platforms = database.get_platforms()
    results=[]
    for p in platforms:
        if not is_in_schedule(p):
            results.append({"platform":p["name"], "status":"休眠中","reason":f"按计划暂停 {p['schedule_start']}-{p['schedule_end']}"})
            continue
        # mock rank
        rank = random.randint(1,50) if random.random()>0.3 else None
        results.append({"platform":p["name"], "rank":rank, "in_top5": 1 if rank and rank<=5 else 0, "checked_at": datetime.datetime.now().isoformat()})
    return results

async def crawl_all():
    return await crawl_object(1)



import sqlite3, pathlib, json, datetime
DB = pathlib.Path(__file__).parent / "monitor.db"

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS objects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, url TEXT DEFAULT 'www.prolockey.com',
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        object_id INTEGER,
        keyword TEXT, ktype TEXT DEFAULT '中文关键词',
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS platforms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, url TEXT, category TEXT,
        pc_url TEXT, mobile_url TEXT,
        status TEXT DEFAULT '已登录',
        schedule_start TEXT DEFAULT '00:00',
        schedule_end TEXT DEFAULT '23:59',
        frequency TEXT DEFAULT '每小时',
        weekdays TEXT DEFAULT '1,2,3,4,5,6,7',
        is_all_day INTEGER DEFAULT 1
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        object_id INTEGER, keyword_id INTEGER, platform_id INTEGER,
        rank_pos INTEGER, in_top5 INTEGER, checked_at TEXT
    )""")
    # seed platforms if empty
    cur = c.execute("SELECT COUNT(*) as cnt FROM platforms")
    if cur.fetchone()["cnt"] == 0:
        seeds = [
            ("百度","https://www.baidu.com","国内热搜","https://www.baidu.com","https://m.baidu.com"),
            ("必应国内版","https://cn.bing.com","国内热搜","https://cn.bing.com","https://cn.bing.com"),
            ("360搜索","https://www.so.com","国内热搜","https://www.so.com","https://m.so.com"),
            ("搜狗","https://www.sogou.com","国内热搜","https://www.sogou.com","https://m.sogou.com"),
            ("夸克","https://www.quark.cn","国内热搜","https://www.quark.cn","https://m.quark.cn"),
            ("微信搜一搜","https://weixin.sogou.com","国内热搜","https://weixin.sogou.com","https://weixin.sogou.com"),
            ("B站","https://www.bilibili.com","国内热搜","https://www.bilibili.com","https://m.bilibili.com"),
            ("小红书","https://www.xiaohongshu.com","国内热搜","https://www.xiaohongshu.com","https://m.xiaohongshu.com"),
            ("Google","https://www.google.com","海外热搜","https://www.google.com","https://www.google.com"),
            ("Bing国际版","https://www.bing.com","海外热搜","https://www.bing.com","https://www.bing.com"),
            ("Yahoo","https://search.yahoo.com","海外热搜","https://search.yahoo.com","https://search.yahoo.com"),
            ("DuckDuckGo","https://duckduckgo.com","海外热搜","https://duckduckgo.com","https://duckduckgo.com"),
            ("1688网址","https://www.1688.com","国内电商","https://www.1688.com","https://m.1688.com"),
            ("淘宝","https://www.taobao.com","国内电商","https://www.taobao.com","https://m.taobao.com"),
            ("拼多多","https://www.pinduoduo.com","国内电商","https://www.pinduoduo.com","https://www.pinduoduo.com"),
            ("京东","https://www.jd.com","国内电商","https://www.jd.com","https://m.jd.com"),
            ("抖音","https://www.douyin.com","国内电商","https://www.douyin.com","https://www.douyin.com"),
            ("Amazon DE","https://www.amazon.de","海外电商","https://www.amazon.de","https://www.amazon.de"),
            ("Amazon UK","https://www.amazon.co.uk","海外电商","https://www.amazon.co.uk","https://www.amazon.co.uk"),
            ("Temu","https://www.temu.com","海外电商","https://www.temu.com","https://www.temu.com"),
            ("AliExpress","https://www.aliexpress.com","海外电商","https://www.aliexpress.com","https://www.aliexpress.com"),
            ("豆包","https://www.doubao.com/chat","GEO AI","https://www.doubao.com/chat","https://www.doubao.com/chat"),
            ("Deepseek","https://www.deepseek.com","GEO AI","https://www.deepseek.com","https://www.deepseek.com"),
            ("元宝","https://yuanbao.tencent.com","GEO AI","https://yuanbao.tencent.com","https://yuanbao.tencent.com"),
            ("KIMI","https://kimi.moonshot.cn","GEO AI","https://kimi.moonshot.cn","https://kimi.moonshot.cn"),
        ]
        for name,url,cat,pc,mob in seeds:
            c.execute("INSERT INTO platforms (name,url,category,pc_url,mobile_url) VALUES (?,?,?,?,?)",(name,url,cat,pc,mob))
    conn.commit()
    conn.close()

def get_all_objects():
    conn=get_conn(); rows=conn.execute("SELECT * FROM objects ORDER BY id DESC").fetchall(); conn.close()
    return [dict(r) for r in rows]

def add_object(name):
    conn=get_conn(); c=conn.cursor()
    c.execute("INSERT INTO objects (name,url,created_at) VALUES (?,?,?)",(name,"www.prolockey.com",datetime.datetime.now().isoformat()))
    conn.commit(); oid=c.lastrowid; conn.close(); return {"success":True,"id":oid}

def delete_object(oid):
    conn=get_conn(); conn.execute("DELETE FROM objects WHERE id=?",(oid,)); conn.commit(); conn.close(); return {"success":True}

def get_all_keywords():
    conn=get_conn(); rows=conn.execute("SELECT * FROM keywords").fetchall(); conn.close(); return [dict(r) for r in rows]

def get_keywords_by_object(oid):
    conn=get_conn(); rows=conn.execute("SELECT * FROM keywords WHERE object_id=?",(oid,)).fetchall(); conn.close(); return [dict(r) for r in rows]

def add_keyword(object_id, keyword, ktype="中文关键词"):
    conn=get_conn(); c=conn.cursor()
    c.execute("INSERT INTO keywords (object_id,keyword,ktype,created_at) VALUES (?,?,?,?)",(object_id,keyword,ktype,datetime.datetime.now().isoformat()))
    conn.commit(); kid=c.lastrowid; conn.close(); return {"success":True,"id":kid}

def get_platforms():
    conn=get_conn(); rows=conn.execute("SELECT * FROM platforms").fetchall(); conn.close(); return [dict(r) for r in rows]

def update_platform_schedule(pid, data):
    conn=get_conn()
    conn.execute("UPDATE platforms SET schedule_start=?, schedule_end=?, frequency=?, weekdays=?, is_all_day=? WHERE id=?",
                 (data.get("schedule_start","00:00"), data.get("schedule_end","23:59"), data.get("frequency","每小时"), data.get("weekdays","1,2,3,4,5,6,7"), int(data.get("is_all_day",1)), pid))
    conn.commit(); conn.close(); return {"success":True}

def get_rankings():
    conn=get_conn(); rows=conn.execute("SELECT * FROM rankings ORDER BY checked_at DESC LIMIT 200").fetchall(); conn.close(); return [dict(r) for r in rows]

"""하루 한 건: 위비티/링커리어 SW 공모전 공고 → 인스타그램 게시. 표준 라이브러리만 사용.

IG_ACCESS_TOKEN 없이 실행하면 게시하지 않고 올릴 내용만 출력한다(dry-run).
"""
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urljoin
from urllib.request import Request, urlopen

KST = timezone(timedelta(hours=9))

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
GRAPH = "https://graph.instagram.com"
POSTED = Path(__file__).with_name("posted.txt")
HASHTAGS = "#공모전 #SW공모전 #IT공모전 #해커톤 #개발자 #코딩 #대학생"

# (목록 URL, 공고 id 정규식, 상세 URL 템플릿)
# 온오프믹스는 robots.txt가 일반 봇을 전면 차단(Disallow: /)해서 넣지 않았다.
WEVITY = (r"gbn=view[^\"']*?ix=(\d+)", "https://www.wevity.com/?c=find&s=1&gub=1&gbn=view&ix={}")
SOURCES = [
    ("https://www.wevity.com/?c=find&s=1&gub=1&cidx=20", *WEVITY),  # 웹/모바일/IT
    ("https://www.wevity.com/?c=find&s=1&gub=1&cidx=21", *WEVITY),  # 게임/소프트웨어
    ("https://linkareer.com/list/contest?filterBy_categoryIDs=35", r"/activity/(\d+)", "https://linkareer.com/activity/{}"),  # 공모전 > 과학/공학
]

# ponytail: 카테고리만으로는 광고 고정글·e스포츠·사진 공모전이 섞여서 제목 키워드로 한 번 더 거른다.
# 놓치는 공고나 잘못 올라가는 공고가 보이면 이 정규식만 고치면 된다.
SW = re.compile(
    r"(?<![A-Za-z])(?:AI|SW|IT|ICT)(?![A-Za-z])"  # 영문 약어는 Competition의 it 같은 오탐을 막으려 대문자·단어 단위로만
    r"|소프트웨어|인공지능|해커톤|프로그래밍|코딩|개발자|데이터|알고리즘|오픈소스|보안|해킹|버그바운티|앱|웹(?!툰|소설)"
)


def get(url, data=None):
    req = Request(url, data=urlencode(data).encode() if data else None, headers={"User-Agent": UA})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def og(page, prop):
    m = re.search(rf'<meta[^>]+property="og:{prop}"[^>]+content="([^"]*)"', page)
    return html.unescape(m.group(1)).replace("\xa0", " ").strip() if m else ""


def candidates():
    """사이트별 최신 공고 URL을 번갈아 섞어서 반환."""
    lists = []
    for list_url, pattern, detail in SOURCES:
        try:
            ids = dict.fromkeys(re.findall(pattern, get(list_url)))  # 순서 유지 중복 제거
        except OSError as e:  # 한 사이트가 죽어도 나머지로 진행
            print(f"목록 실패 {list_url}: {e}", file=sys.stderr)
            ids = []
        lists.append([detail.format(i) for i in ids])
    return list(dict.fromkeys(u for group in zip_longest(*lists) for u in group if u))  # 위비티는 두 카테고리에 같은 공고가 겹친다


def activity(page):
    """링커리어 상세의 __NEXT_DATA__에서 공고 객체를 꺼낸다. 위비티처럼 없으면 {}."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    try:
        return json.loads(m.group(1))["props"]["pageProps"]["data"]["activityData"]["activity"]
    except (AttributeError, KeyError, TypeError, ValueError):
        return {}


def poster(page):
    """원본 해상도 포스터 URL. og:image는 250px 썸네일이라 최후의 수단으로만 쓴다."""
    thumb = og(page, "image")
    found = [f["url"] for f in activity(page).get("files") or [] if re.search(r"\.(jpe?g|png)$", f.get("filename") or "", re.I)]
    found += [urljoin("https://www.wevity.com", u) for u in re.findall(r'<img[^>]+src="(/upload/contest/[^"]+)"', page)]
    return next((u for u in found if u != thumb), thumb)


def caption(page, url):
    title = og(page, "title").split(" | ")[0]
    desc = re.sub(r"\s*■\s*", "\n▪ ", og(page, "description"))[:1500]  # 인스타 캡션 한도 2,200자
    a = activity(page)
    if a.get("recruitCloseAt"):  # 링커리어는 og 설명에 주최·마감일이 없어서 보충
        close = datetime.fromtimestamp(a["recruitCloseAt"] / 1000, KST)
        desc += f"\n\n🏢 주최: {a.get('organizationName') or '-'}\n⏰ 마감: {close:%Y.%m.%d}"
    return f"📌 {title}\n\n{desc}\n\n🔗 {url}\n\n{HASHTAGS}"


def image_url(src):
    # ponytail: 인스타는 JPEG + 4:5~1.91:1 비율만 받는데 포스터는 대부분 더 길다.
    # 무료 이미지 프록시 wsrv.nl로 4:5 흰 여백 패딩. 프록시가 막히면 Pillow로 변환해
    # repo에 커밋하고 raw URL을 넘기는 방식으로 교체.
    return f"https://wsrv.nl/?url={quote(src, safe='')}&w=1080&h=1350&fit=contain&cbg=white&output=jpg"


def warm(img):
    """프록시는 첫 요청이 느릴 수 있어, 인스타가 가져가기 전에 캐시를 데우고 JPEG인지 확인한다."""
    for _ in range(2):
        try:
            with urlopen(Request(img, headers={"User-Agent": UA}), timeout=60) as r:
                if r.read(3) == b"\xff\xd8\xff":
                    return
        except OSError:
            pass
    raise RuntimeError("이미지 변환 실패")


def publish(uid, token, img, text):
    cid = json.loads(get(f"{GRAPH}/{uid}/media", {"image_url": img, "caption": text, "access_token": token}))["id"]
    for _ in range(10):  # 컨테이너 처리 대기
        status = json.loads(get(f"{GRAPH}/{cid}?fields=status_code&access_token={token}"))["status_code"]
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"컨테이너 {status}")
        time.sleep(3)
    else:
        raise RuntimeError("컨테이너 처리 시간 초과")
    get(f"{GRAPH}/{uid}/media_publish", {"creation_id": cid, "access_token": token})


def main():
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not token and os.environ.get("CI"):
        sys.exit("IG_ACCESS_TOKEN secret이 없습니다")
    uid = json.loads(get(f"{GRAPH}/me?fields=user_id&access_token={token}"))["user_id"] if token else None

    posted = set(POSTED.read_text().split())
    urls = candidates()
    if not urls:
        sys.exit("공고를 하나도 못 찾음 — 사이트 구조가 바뀐 듯")

    failures = 0
    for url in urls:
        if url in posted:
            continue
        time.sleep(1)  # 상세 페이지를 연달아 긁으면 링커리어가 연결을 끊는다
        try:
            page = get(url)
        except OSError as e:  # 상세 하나가 죽어도 다음 공고로 (내일 다시 시도됨)
            print(f"상세 실패 {url}: {e}", file=sys.stderr)
            continue
        if not SW.search(og(page, "title")):
            continue
        src = poster(page)
        if not src:  # 포스터 없는 공고는 건너뜀
            continue
        img, text = image_url(src), caption(page, url)
        try:
            warm(img)
            if not token:
                print(f"[dry-run] {img}\n\n{text}")
                return
            publish(uid, token, img, text)
        except (HTTPError, RuntimeError) as e:
            # 한 공고(이미지 문제 등)가 매일 큐를 막지 않도록 다음 공고로 넘어간다
            detail = e.read().decode("utf-8", "replace") if isinstance(e, HTTPError) else e
            print(f"게시 실패 {url}: {detail}", file=sys.stderr)
            failures += 1
            if failures == 3:
                sys.exit("연속 3건 실패 — 중단")
            continue
        with POSTED.open("a") as f:
            f.write(url + "\n")
        print("게시 완료:", url)
        return
    if failures:
        sys.exit("게시 실패")
    print("새 공고 없음")


if __name__ == "__main__":
    main()

"""해커톤·개발 공모전 필터·중복 판별 자가 점검: python3 test_post.py"""
from post import is_dev, is_uou_contest, title_key

# 같은 공모전은 사이트별 표기가 달라도 같은 키
assert title_key("[서울대학교 창업지원단·H1R AI] 2026 SNU X Croche AI 앱 해커톤") == title_key("2026 SNU X Croche AI 앱 해커톤")
assert title_key("[데이콘]합성 미세구조 기반 재료 물성 예측 AI 경진대회(~10/19)") == title_key("합성 미세구조 기반 재료 물성 예측 AI 경진대회")
# 회차가 다르면 다른 공모전
assert title_key("2026 제5회 오픈소스 SW개발 경진대회") != title_key("2027 제6회 오픈소스 SW개발 경진대회")
assert title_key("[SW 해커톤]")  # 괄호뿐인 제목도 빈 키가 되지 않는다

for title in [
    "[과학기술정보통신부] 제3회 미래융합인재 발굴 소프트웨어 챌린지",
    "2026 CWNU SW-DNA² 챌린지 대학생 AI·SW 경진대회",
    "2026 고용24 국민참여 AI 고용서비스 발굴 온라인 해커톤",
    "공공 웹사이트 불법광고 탐지 도구 개발 공모전",
    "제32회 전국 창의성 IT코딩 경시대회",
    "2026 DATA·AI 분석 경진대회",
]:
    assert is_dev(title), title

for title in [
    "2026 0924영상제 영상 공모전",
    "[29역숏폼왕] 2026 간단요리사 미식대전 프링즈 모집",
    "7th Da-Ho Award Asian International Short Film Competition(단편영화 공모전)",
    "2026 대전 콘텐츠페어 이스포츠 대전 브롤스타즈 참가자 모집",
    "2026 모두의 AI 라운지(수도권) <마이 AI 랩> 참여팀 공모",  # AI만 붙은 공고
    "[한국탄소산업진흥원] 2026 AI 영상 콘텐츠 공모전 「탄소, 다시 보다」",
    "제 3회 AI·디지털 융합 교육 콘텐츠 개발 경진대회 참가자 모집",  # 개발이지만 콘텐츠 제작
]:
    assert not is_dev(title), title

# 울산대 SW중심대학사업단 공지: 대회 모집만, 결과·수상·마감 공지는 제외
for title in [
    "[SW중심대학사업단]2026 대구울산경북 대학교 x Upstage AI Agent 해커톤 울산대학교 참가자 모집",
    "[SW중심대학사업단] 2026-2학기 프로그래밍 경진대회",
    "[SW융합교육센터] 2026 SUMTECH Hackathon 참가자 모집",
    "[SW중심대학사업단] 2026 UOU로봇 OS특강 + 피지컬 AI 챌린지 대회",
    "[SW융합교육센터] 2026학년도 제1회 AI를 활용한 사회문제해결 아이디어 공모전 개최",
]:
    assert is_uou_contest(title), title

for title in [
    "[SW중심대학사업단] 2026-2학기 U-Point 설명회 PPT 자료",
    "2026 캡스톤디자인 경진대회 ★수상자 발표★",
    "[SW융합교육센터] (최종 결과)2026학년도 제1회 AI를 활용한 사회문제해결 아이디어 공모전",
    "(마감)[외부프로그램][단순홍보]2026 울산SW미래채움 초중등 AI·SW 해커톤 대회 대학생 멘토 모집",
    "[울산대 SW중심대학사업단] 2026-2 SW 서포터즈 모집",
]:
    assert not is_uou_contest(title), title

print("ok")

"""SW 키워드 필터 자가 점검: python3 test_post.py"""
from post import SW

for title in [
    "[과학기술정보통신부] 제3회 미래융합인재 발굴 소프트웨어 챌린지",
    "2026 CWNU SW-DNA² 챌린지 대학생 AI·SW 경진대회",
    "2026 DATA·AI 분석 경진대회",
    "제32회 전국 창의성 IT코딩 경시대회",
    "공공 웹사이트 불법광고 탐지 도구 개발 공모전",
]:
    assert SW.search(title), title

for title in [
    "LG 대국민 미소 사진 공모전 - 스마일 모먼트",
    "7th Da-Ho Award Asian International Short Film Competition",  # 소문자 it/ai 오탐 방지
    "2026 대전 콘텐츠페어 이스포츠 대전 브롤스타즈 참가자 모집",
    "제5회 네이버 웹툰 공모전",
]:
    assert not SW.search(title), title

print("ok")

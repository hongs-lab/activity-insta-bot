"""해커톤·개발 공모전 필터 자가 점검: python3 test_post.py"""
from post import is_dev

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

print("ok")

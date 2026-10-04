# 대외활동 인스타 봇

매일 09시(KST)에 위비티·링커리어의 대외활동 공고 1건을 포스터 이미지 + 설명글로 인스타그램에 올린다.
GitHub Actions + 인스타그램 공식 API(Instagram Login)만 사용, 의존성 없음.

## 설정 (최초 1회)

1. **인스타그램 계정** 생성 후 설정 → 계정 유형 → **프로페셔널 계정**(비즈니스/크리에이터)으로 전환.
2. **Meta 앱**: <https://developers.facebook.com/apps> → 앱 만들기 → Instagram 제품 추가 →
   "Instagram 로그인을 통한 API 설정"에서 위 계정을 추가하고 **토큰 생성**.
   권한: `instagram_business_basic`, `instagram_business_content_publish`.
3. **GitHub Secrets** (repo → Settings → Secrets and variables → Actions):
   - `IG_ACCESS_TOKEN`: 2번에서 받은 토큰
   - `GH_PAT`: fine-grained PAT (이 repo 한정, Secrets: Read and write) — 토큰 자동 갱신용
4. Actions 탭 → `daily-post` → **Run workflow**로 첫 게시 테스트.

## 로컬 확인

```bash
python3 post.py   # 토큰 없으면 게시하지 않고 올릴 내용만 출력
```

게시한 공고 URL은 `posted.txt`에 쌓이고, 여기 있는 공고는 다시 올리지 않는다.

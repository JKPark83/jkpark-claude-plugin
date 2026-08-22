# Privacy Nutrition Label & Age Rating

Both are questionnaires whose answers persist across versions and are checked
against the binary. Answer each from a code citation, never from intent.

## What "수집(collect)" means

Apple counts data as collected when it **leaves the device and is retained by
the developer or a third party acting for the developer**, in any form beyond
the immediate transaction.

Three cases the scan must distinguish:

| 상황 | 수집인가 | 근거 예 |
|---|---|---|
| 오디오가 기기 안에서만 처리되고 앱 컨테이너에만 저장 | **아님** | 전사·요약 호출부가 전부 온디바이스 프레임워크 |
| 사용자가 버튼을 눌러 본인 Notion/Google 계정으로 내보냄 | **아님** — 개발자가 받지 않음. 단 개인정보 처리방침에는 명시해야 한다 | `ExportService.swift`가 사용자 토큰으로 서드파티 API 직접 호출 |
| 앱 서버가 OAuth 코드를 토큰으로 교환 | **검토 필요** — 서버가 토큰을 저장하면 수집 | `server/src/routes/notionOAuth.ts` |

세 번째 유형이 가장 많이 틀린다. 서버 코드를 읽어 토큰·요청 본문이 로그나 DB에
남는지 확인하고, 남지 않으면 그 사실을 근거로 적는다. 확인할 수 없으면
"수집 안 함"이라고 쓰지 말고 초안 6절에 검증 항목으로 올린다.

Violation example: 앱이 온디바이스라는 이유만으로 모든 항목을 "수집 안 함"으로
채우고, 크래시 리포팅 SDK가 `Package.swift`에 들어 있는 것을 놓친 경우 —
Sentry·Firebase는 진단 데이터 수집에 해당하고, 누락은 사후 앱 제거 사유가 된다.

## 스캔에서 확인할 신호

```bash
grep -rn "URLSession\|Alamofire" --include=*.swift . | grep -v Test
grep -rln "Firebase\|Sentry\|Amplitude\|Mixpanel\|GoogleAnalytics\|Adjust\|AppsFlyer" .
grep -rn "AppTrackingTransparency\|ASIdentifierManager\|advertisingIdentifier" --include=*.swift .
grep -rn "CLLocationManager\|HKHealthStore\|CNContactStore\|PHPhotoLibrary" --include=*.swift .
```

| 신호 | 영양표 영향 |
|---|---|
| 분석·크래시 SDK 존재 | 진단(Diagnostics) 또는 사용 데이터 수집 = 예 |
| `AppTrackingTransparency` 사용 | 추적(Tracking) = 예 → ATT 프롬프트 필수 |
| 위치·건강·연락처·사진 API | 해당 데이터 유형 검토 + 대응 `UsageDescription` 필요 |
| 계정 로그인 | 연락처 정보(이메일) 수집 여부 검토 |
| 서드파티 SDK 하나도 없고 서버도 없음 | "데이터를 수집하지 않음" 가능 |

각 데이터 유형은 수집이라면 **용도**(앱 기능 / 분석 / 광고 / 개인화)와
**신원 연결 여부**, **추적 사용 여부**를 함께 답해야 한다. 초안 3절 표에 이
세 열을 추가한다.

## 연령 등급

설문은 App Store Connect에서 직접 답해야 하고, 답변은 앱 정보 탭에 남는다.
초안에는 답안과 근거만 적어 사용자가 그대로 옮길 수 있게 한다.

코드 근거로 판정할 수 있는 항목:

| 설문 항목 | 판정 근거 |
|---|---|
| 사용자 생성 콘텐츠 공개 공유 | 공개 피드·댓글·프로필 화면이 없으면 아니요 |
| 웹 브라우징 기능 | `WKWebView`가 임의 URL을 열지 않으면 아니요 (OAuth 전용 `ASWebAuthenticationSession`은 브라우징이 아니다) |
| 메시징·채팅 | 사용자 간 통신 코드 없음 |
| 도박·경품 | 관련 코드 없음 |
| 의료·치료 정보 | 건강 데이터 API 미사용 |
| 광고 | 광고 SDK 없음 |

전부 아니요이고 폭력·성적 콘텐츠·약물 묘사가 없으면 결과는 **4+**다.

주의: 사용자가 자유 텍스트를 입력하고 그것이 **다른 사용자에게 보이지 않으면**
사용자 생성 콘텐츠 항목은 아니요다. 회의록을 사용자 본인만 보는 앱이 여기에
해당한다.

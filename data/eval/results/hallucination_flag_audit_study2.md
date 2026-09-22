# Study 2 환각 플래그 전수 감사 (사후, 읽기 전용; 2026-09-22)

질문: 채점기 v4가 환각으로 센 문자열이 실제로 화면에도 매뉴얼에도 없는 '지어낸' 요소인가, 아니면 매뉴얼 해당 절(§1.4.2a / §1.4.3b)에 그대로 있는 조작 명칭인가. 대조 = 플래그 문자열(정규화)이 해당 절 본문(KB v4 청크)에 부분 문자열로 존재하는지. 서명된 판정은 바꾸지 않는다.

| model | backend | 플래그 스텝/전체 | 플래그 수 | 매뉴얼에 있음 | 매뉴얼에 없음 | 환각률 v4 | 환각률(매뉴얼 제외 시) |
|---|---|---|---|---|---|---|---|
| gemini | no_rag | 16/160 | 17 | 10 | 7 | 0.100 | 0.044 |
| gemini | vanilla_budget | 20/160 | 20 | 15 | 5 | 0.125 | 0.031 |
| gemini | vanilla_vector | 10/160 | 10 | 10 | 0 | 0.062 | 0.000 |
| gemini | full_system | 14/160 | 14 | 13 | 1 | 0.087 | 0.006 |
| claude | no_rag | 24/160 | 24 | 22 | 2 | 0.150 | 0.013 |
| claude | vanilla_budget | 0/160 | 0 | 0 | 0 | 0.000 | 0.000 |
| claude | vanilla_vector | 23/160 | 33 | 24 | 9 | 0.144 | 0.056 |
| claude | full_system | 4/160 | 6 | 6 | 0 | 0.025 | 0.000 |
| gpt | no_rag | 2/160 | 2 | 0 | 2 | 0.013 | 0.013 |
| gpt | vanilla_budget | 8/160 | 8 | 0 | 8 | 0.050 | 0.050 |
| gpt | vanilla_vector | 6/160 | 6 | 5 | 1 | 0.037 | 0.006 |
| gpt | full_system | 23/160 | 23 | 11 | 12 | 0.144 | 0.075 |

## 매뉴얼에 없는 플래그 전부 (진짜 환각 후보)

- claude no_rag: {'Display Properties': 2}
- claude vanilla_vector: {'QC': 9}
- gemini full_system: {'OK': 1}
- gemini no_rag: {'Add/Display': 1, 'Track Horizon 3D': 1, 'Horizon auto-track': 1, 'Lock/Unlock patch': 1, 'Track Horizon': 1, 'Lock Horizon': 2}
- gemini vanilla_budget: {'OK': 1, 'Lock/Unlock current patch': 1, 'Lock Horizon': 1, 'Add/Display': 1, 'Lock patch': 1}
- gpt full_system: {'Z/X': 12}
- gpt no_rag: {'QC': 2}
- gpt vanilla_budget: {'QC': 8}
- gpt vanilla_vector: {'QC': 1}

## 매뉴얼에 있는 플래그 (조작 명칭·마우스 동작·메뉴 항목)

{'Manual Tracking': 37, 'Add': 21, 'Properties': 16, 'Left-click + drag': 13, 'Ctrl + Left-click': 10, 'Left-click': 7, 'Display': 3, 'sections only': 2, 'Display Only': 2, 'Ctrl+': 2, 'Ctrl +': 1, 'Attribute': 1, 'Ctrl': 1}

참고: GPT full_system의 'Z/X'(12건)는 매뉴얼 p.85/p.89의 "short keys (Z and X by default)"를 축약한 표기라 문자열 대조에서는 '없음'으로 분류되지만 내용상 매뉴얼 근거가 있다. 'QC'(Claude vanilla_vector 9, GPT 11)는 매뉴얼 step 15 "QC the auto-tracked horizon patch"의 약어이며 위 대조 방식(길이 ≥ 3)에서 제외됐다.

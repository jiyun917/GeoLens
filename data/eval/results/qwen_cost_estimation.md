# Qwen3-235B-A22B 서빙 비용 환산 — 사전 준비

**모델**: Qwen3-235B-A22B-Instruct, INT4 GPTQ 양자화
**서빙 엔진**: vLLM
**호스팅**: 자체 NAS 시스템
**엔드포인트**: `http://168.131.141.77:28000/v1`

## 실측 처리량 (v2 unified2 매트릭스)

| 지표 | 값 |
|------|-----|
| Total 스텝 실행 (Qwen only) | 240 (5 rep × 2 시나리오 × 6 백엔드 × 4 스텝) |
| Mean input tokens/step | ~1,900 (백엔드별 상이, no_rag 최소 614, vanilla 최대 6,888) |
| Mean output tokens/step | ~445 |
| Mean latency/step | 7.3–42.2s (백엔드별) |
| 매트릭스 실행 시작~종료 시간 | 2026-07-16 15:24 ~ 19:29 (약 4시간) |

## 3가지 산정 시나리오

**시나리오 A**: 실제 하드웨어가 A100 80GB × 4 (권장 최소 구성)일 때
- 클라우드 임대가 (Lambda Labs 기준, 2026-07): A100 80GB $1.29/h
- 4대 시간당 $5.16/h
- 4시간 실행 총비용 → $20.64
- 240 스텝 → 스텝당 **$0.086** (86 µUSD)

**시나리오 B**: 실제 하드웨어가 H100 80GB × 2 (권장 최소)
- 클라우드 임대가: H100 80GB $2.49/h
- 2대 시간당 $4.98/h
- 4시간 → $19.92
- 240 스텝 → 스텝당 **$0.083** (83 µUSD)

**시나리오 C**: 실제 하드웨어가 A6000 48GB × 4 (컨슈머급 근사)
- 클라우드 임대가: A6000 $0.80/h
- 4대 시간당 $3.20/h
- 4시간 → $12.80
- 240 스텝 → 스텝당 **$0.053** (53 µUSD)

## 산정 근거

**INT4 GPTQ + vLLM 필요 VRAM 추정**:
- Qwen3-235B (A22B activated) INT4 = 235 × 0.5 bytes/param = ~118 GB weights
- KV cache + activation buffer: ~30–50 GB (context 20K token 기준)
- 총 필요 VRAM: ~150–170 GB
- **최소 구성**: A100 80GB × 2 (텐서 병렬화) 또는 H100 80GB × 2

**시간 계산**:
- 벤치 매트릭스 실행 4시간은 실제 GPU 활성 시간과 근사 (아이들 오버헤드 최소)
- Qwen만 240 스텝 실행 소요시간이 관측됨

## 대안: Table 표기 옵션

만약 하드웨어 확정 불가 시:

**옵션 1**: 셀에 "n/a (self-hosted)" + 각주에 처리량 정보
```
| qwen full_system | n/a (self-hosted, 30.9s/step) |
```

**옵션 2**: 셀에 "H100-equiv $0.083*" + 각주에 산정 근거
```
| qwen full_system | ~$0.083* (H100-equiv) |
* Estimated using cloud rental rate for H100 80GB × 2 at $4.98/h.
  Actual self-hosted hardware differs; see §Methods.
```

**옵션 3 (권장)**: 두 값 병기
```
| qwen full_system | $0 (self-hosted) / ~$0.083 (cloud-equiv) |
```

## 사용자 확인 필요

다음 정보 확인 요청:
1. NAS 서빙 하드웨어 종류 (예: A100 80GB × 4, H100 × 2 등)
2. 임대가 기준을 어느 클라우드 벤더로 할지 (Lambda / AWS / GCP)
3. Table 표기 방식 (옵션 1/2/3)

확인 회신 후 Table 1의 Qwen cost 셀 및 §4.4 서술 갱신.

# 서울 공유자전거 수요 예측 (Seoul Bike Demand Forecast)

시간대와 날씨 정보로 서울 공유자전거의 **시간당 대여 수**를 예측하는 Keras 회귀 모델입니다. (머신러닝 미니 프로젝트)

시간당 수요를 예측하면 자전거 재배치와 운영 계획에 활용할 수 있습니다.

## 데이터

- **출처**: [Seoul Bike Sharing Demand (UCI Machine Learning Repository)](https://archive.ics.uci.edu/dataset/560/seoul+bike+sharing+demand)
- **기간**: 2017-12-01 ~ 2018-11-30 (365일 × 24시간 = 8,760행)
- **입력 변수**: 시간, 기온, 습도, 풍속, 가시거리, 이슬점, 일사량, 강수량, 적설량, 계절, 공휴일 여부 + 날짜에서 만든 요일·월·주말 여부
- **출력 변수**: `rented_bike_count` (시간당 대여 수)

변수별 설명, 단위, 값 범위, UCI 설명과 실제 파일이 다른 점은 [docs/data_description.md](docs/data_description.md)에 정리되어 있습니다.

## 결과

| 항목 | 내용 |
|---|---|
| 모델 | Dense 128-64-32 (relu) → 1 |
| optimizer / loss / metric | Adam (lr 0.001) / MSE / MAE |
| batch size / epochs | 32 / 100 |
| 데이터 분할 | 무작위 분할, train 70 / validation 15 / test 15 |

| | MSE | RMSE | MAE |
|---|---|---|---|
| validation | 34,268.3 | 185.1 | 110.6 |
| **test** | **30,180.8** | **173.7** | **111.3** |

기본 모델(Dense 64-32-1)의 validation MSE 104,863.9에서 하이퍼파라미터 실험으로 약 67% 줄였습니다. 단계별 상세 내용은 [docs/project_summary.md](docs/project_summary.md)에 정리되어 있습니다.

## 폴더 구조

```
seoul-bike-demand-forecast/
├─ data/
│  ├─ raw/SeoulBikeData.csv     ← 원본 데이터 (수정하지 않음)
│  └─ processed/                ← 정리본, 분할된 데이터 (노트북 실행 시 생성)
├─ notebooks/                   ← 단계별 노트북 (01 → 05 순서로 실행)
├─ src/                         ← 노트북에서 공통으로 쓰는 코드
├─ results/                     ← 실험 결과, 최적 하이퍼파라미터
└─ docs/                        ← 문서
   ├─ data_description.md       ← 데이터 설명
   └─ project_summary.md        ← 단계별 작업 정리
```

| 노트북 | 하는 일 |
|---|---|
| `01_data_cleaning.ipynb` | 원본 로드(Latin-1), 컬럼명 정리, 날짜 변환 → 정리본 저장 |
| `02_eda.ipynb` | 시간대·계절·기온·비/눈·공휴일별 대여 수, 상관관계, 이상치 확인 |
| `03_preprocessing.ipynb` | humidity 0 보정, 비운영 시간 제외, 날짜 변수, 인코딩, 분할, 표준화 |
| `04_experiments.ipynb` | 기본 모델 + 하이퍼파라미터 실험 4개 (layer/뉴런 수, 활성화 함수, learning rate, 타깃 로그 변환) |
| `05_final_model.ipynb` | 최적 조합으로 학습, test 데이터로 최종 평가 |

## 실행 방법

### 1. 환경 만들기

Python 3.14용 TensorFlow가 없어서(2026-11 확인) Python 3.12 conda 환경을 사용합니다.

```bash
conda create -n ml python=3.12 -y
```

```bash
conda activate ml
```

```bash
pip install tensorflow pandas numpy matplotlib scikit-learn ipykernel
```

개발에 사용한 버전: Python 3.12.14, tensorflow 2.21.0, keras 3.15.1, numpy 2.5.4, pandas 3.1.0, matplotlib 3.11.2, scikit-learn 1.9.1

### 2. 노트북 실행

1. VS Code에서 `notebooks/` 폴더의 노트북을 열고, 커널로 `ml` 환경을 선택합니다.
2. **01 → 02 → 03 → 04 → 05 순서**로 실행합니다. 앞 노트북이 저장한 파일을 다음 노트북이 읽습니다.
   - 04는 실험 때문에 CPU 기준 약 6분이 걸립니다.
   - 05는 04가 저장한 `results/best_config.json`을 읽으므로, 실험을 다시 돌리지 않고 최종 평가만 할 수 있습니다.
3. 랜덤 시드를 42로 고정해서 같은 환경에서는 같은 결과가 나옵니다.

## 한계

- 데이터가 1년치뿐이고 대여소별 정보가 없습니다.
- 무작위 분할이라 인접한 시간대가 train과 test에 나뉘어 들어가므로, 실제 미래 예측보다 성능이 좋게 나왔을 수 있습니다.
- 하이퍼파라미터 실험은 시드 하나로 한 번씩만 실행했습니다.

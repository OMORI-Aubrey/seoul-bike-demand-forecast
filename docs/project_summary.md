# 작업 정리: 서울 공유자전거 수요 예측

머신러닝 미니 프로젝트에서 지금까지 진행한 작업, 결정 사항, 결과를 단계별로 정리한 문서입니다.

## 프로젝트 개요

- **주제**: 서울 공유자전거 시간당 대여 수 예측 (정형 데이터 회귀, Keras)
- **데이터**: Seoul Bike Sharing Demand (UCI), 2017-12-01 ~ 2018-11-30, 8,760행 × 14열 (365일 × 24시간)
- **타깃**: `rented_bike_count` (시간당 대여 수)

## 1단계: 환경 구성

- 처음 확인했을 때 VS Code Jupyter 커널(Anaconda base, Python 3.14)에는 TensorFlow가 없었고, Python 3.14용 TensorFlow도 PyPI에 없었음
- conda 환경 **`ml`** (Python 3.12.14)을 새로 만들어 사용 (다른 프로젝트에서도 사용 가능)
- 설치한 버전: tensorflow 2.21.0, keras 3.15.1, numpy 2.5.4, pandas 3.1.0, matplotlib 3.11.2, scikit-learn 1.9.1
- `keras.utils.set_random_seed(42)`로 시드를 고정하면 결과가 똑같이 재현되는 것을 확인
- Windows에서는 TensorFlow GPU를 지원하지 않아 CPU로만 학습

## 2단계: 데이터 로드·형식 정리 (`notebooks/01_data_cleaning.ipynb`)

- 원본이 UTF-8이 아니어서 `encoding='latin-1'`로 읽음 (비ASCII 문자는 `°` 하나뿐)
- 컬럼명 14개를 영문 소문자로 변경 (예: `Temperature(°C)` → `temperature`, `Functioning Day` → `functioning_day`)
- `date`를 `dd/mm/yyyy` 형식으로 보고 `dayfirst=True`로 datetime 변환
- `data/processed/seoul_bike_clean.csv`에 UTF-8로 저장 (원본 파일은 수정하지 않음)

## 3단계: EDA (`notebooks/02_eda.ipynb`)

운영하지 않은 시간 295행(대여 수가 전부 0)을 빼고, 운영한 시간 8,465행으로 분석했습니다.

| 가설 | 결과 |
|---|---|
| 출퇴근 시간대에 수요가 몰린다 | ✅ 18시 1,554, 8시 1,050이 정점, 4~5시가 최저(약 140). 주중에만 두 개의 정점이 있고, 주말·공휴일은 오후에 완만하게 오르는 형태 |
| 비·눈이 오면 수요가 줄어든다 | ✅ 비 올 때 167 vs 안 올 때 766 / 눈 있을 때 185 vs 없을 때 759 |
| 기온이 적당한 계절에 수요가 많다 | ✅ 여름 1,034 > 가을 924 > 봄 746 > 겨울 226. 25~30°C에서 가장 많고 35°C를 넘으면 줄어듦 |
| 평일과 공휴일의 패턴이 다르다 | ✅ 공휴일 529 vs 평일 739, 공휴일에는 출퇴근 정점이 없음 |

- 타깃 왜도 1.14 (오른쪽 꼬리가 긺)
- 대여 수와의 상관계수: temperature 0.56, hour 0.43, dew_point_temp 0.40 순. temperature와 dew_point_temp 사이 상관계수 0.91
- **humidity = 0인 17행**: 2018-05-19 ~ 05-28 새벽에 몰려 있음. 같은 행의 기온·이슬점으로 계산한 습도는 33~72%라서 측정 오류로 판단

## 4단계: 전처리 (`notebooks/03_preprocessing.ipynb`)

1. humidity가 0인 17행을 기온·이슬점으로 계산한 상대습도(Magnus 공식)로 대체. 정상 행에서 계산값과 기록값의 차이는 평균 0.24%p
2. `functioning_day == 'No'`인 295행 제외, 컬럼 삭제 (8,760 → 8,465행)
3. 날짜에서 `day_of_week`, `month`, `is_weekend` 추출 후 `date` 삭제
4. 인코딩: `seasons`는 원-핫 4개 컬럼, `holiday`는 0/1 → 입력 변수 17개
5. 분할: **무작위 분할, train 70 / validation 15 / test 15** (5,925 / 1,270 / 1,270행, `random_state=42`)
6. 표준화: `StandardScaler`를 train으로만 fit (데이터 누수 방지). 0/1 컬럼은 표준화하지 않음
7. 분할된 데이터를 `data/processed/X_*.csv`, `y_*.csv`로 저장

## 5~6단계: 기본 모델·하이퍼파라미터 실험 (`notebooks/04_experiments.ipynb`)

- **기본 모델**: Dense 64-32-1 (relu), Adam lr 0.001, loss MSE, metric MAE, batch 32, epoch 100 → val MSE 104,863.9, MAE 211.4
- **실험 방식**: 한 번에 하나씩만 바꾸고, val MSE가 가장 낮은 값을 다음 실험에 사용. test 데이터는 사용하지 않음

| 실험 | 시험한 값 | 선택 | val MSE |
|---|---|---|---|
| 1. layer/뉴런 수 | 32 / 64-32 / 128-64 / 128-64-32 | **128-64-32** | 34,268.3 |
| 2. 활성화 함수 | relu / tanh / elu | **relu** | 34,268.3 (tanh 346,296.5, elu 45,520.8) |
| 3. learning rate | 0.0001 / 0.001 / 0.003 / 0.01 | **0.001** | 34,268.3 (0.003은 37,658.2) |
| 4. 타깃 로그 변환 | raw / log1p | **raw** | 34,268.3 (log1p 58,657.4, 과적합 보임) |

- 결과는 `results/experiments.csv`, `results/best_config.json`에 저장

## 7단계: 최종 모델·평가 (`notebooks/05_final_model.ipynb`)

- **최종 하이퍼파라미터**: Dense 128-64-32 (relu) → 1, Adam lr 0.001, loss MSE, metric MAE, batch 32, epoch 100, 타깃 raw, 파라미터 12,673개
- 최종 모델은 train으로 학습하고, test로 **한 번만** 평가

| | MSE | RMSE | MAE |
|---|---|---|---|
| validation | 34,268.3 | 185.1 | 110.6 |
| **test** | **30,180.8** | **173.7** | **111.3** |

- test와 validation 성능이 비슷하고, 음수 예측은 0개
- 예측 vs 실제 그래프: 대부분 y = x 선 근처에 모여 있음. 대여 수가 클수록 오차가 퍼지고, 2,500 이상에서는 조금 적게 예측
- 비교 기준 (저장된 분할 데이터로 추가 계산): 모든 시간에 train 평균(732.9)만 예측하면 test MSE 401,418.8 / RMSE 633.6 / MAE 512.4 → 최종 모델은 MSE가 약 1/13
- R² (= 1 - 모델 MSE / 타깃 분산): test 약 0.925, validation 약 0.914

## 8단계: 제출 정리 (진행 중)

- 처음에는 `bike_demand.py`로 내보냈지만, GitHub 주소로 제출하기로 해서 삭제
- 하나였던 노트북을 **단계별 노트북(`notebooks/`)과 공통 코드(`src/`)로 분리**. 01→05 실행 결과가 분리 전과 똑같은 것을 확인
- `.gitignore` 추가
  - `.vscode/`: VS Code 개인 설정. 이미 추적되던 `.vscode/settings.json`은 `git rm --cached`로 추적 해제
  - `__pycache__/`, `*.pyc`: `src`를 import할 때 자동으로 생기는 Python 캐시
- 문서 작성: `README.md`, `docs/project_summary.md`(이 문서), `docs/data_description.md`(데이터 출처·변수 설명, UCI 설명과 실제 파일 비교)
- VS Code에서 `ml` 커널로 01 → 05를 실행하고 **출력 결과를 포함해 저장**. 모든 코드 셀이 오류 없이 실행됐고, 저장된 결과가 이 문서의 값과 같음
- 이해도 검사 대비 정리 문서를 저장소 밖(수업 자료 폴더)에 따로 작성

## 폴더 구조

```
seoul-bike-demand-forecast/
├─ .gitignore                            ← .vscode/, __pycache__/, *.pyc 제외
├─ README.md
├─ docs/
│  ├─ data_description.md               ← 데이터 설명
│  └─ project_summary.md                ← 이 문서
├─ data/
│  ├─ raw/SeoulBikeData.csv             ← 원본 (수정 안 함)
│  └─ processed/
│     ├─ seoul_bike_clean.csv           ← 01 출력
│     └─ X_train/val/test.csv, y_train/val/test.csv  ← 03 출력
├─ results/
│  └─ experiments.csv, best_config.json ← 04 출력
├─ notebooks/
│  ├─ 01_data_cleaning.ipynb
│  ├─ 02_eda.ipynb
│  ├─ 03_preprocessing.ipynb
│  ├─ 04_experiments.ipynb   (약 6분)
│  └─ 05_final_model.ipynb
└─ src/
   ├─ __init__.py
   ├─ config.py   (경로, SEED, TARGET)
   ├─ data.py     (load_clean, save_splits, load_splits)
   └─ model.py    (build_model, plot_history)
```

## 한계 (보고서용)

- 데이터가 1년치뿐이고 대여소별 정보가 없음
- 무작위 분할이라 인접한 시간대가 train과 test에 나뉘어 들어감 → 실제 "미래 예측"보다 점수가 좋게 나왔을 수 있음
- 실험은 시드 하나(42)로 한 번씩만 실행 → 비슷한 값끼리는 순위가 바뀔 수 있음
- 가장 큰 구조(128-64-32)가 가장 좋았고 100 epoch에서도 아직 수렴 중이었음. 더 큰 구조나 더 많은 epoch은 시험하지 않음

## 남은 일

- 보고서(PDF) 작성

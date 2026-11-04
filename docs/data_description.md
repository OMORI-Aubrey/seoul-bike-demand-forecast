# 데이터 설명: Seoul Bike Sharing Demand

이 프로젝트에서 사용한 데이터의 출처, 변수 설명, 실제 파일에서 확인한 내용을 정리한 문서입니다.

## 출처

- **이름**: Seoul Bike Sharing Demand
- **제공처**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/560/seoul+bike+sharing+demand) (2020-02-29 등록)
- **내용**: 서울 공공자전거의 시간당 대여 수와 그 시간의 날씨, 공휴일 정보
- **UCI 표기 특성**: Multivariate / Subject Area: Business / Associated Tasks: Regression / Feature Type: Integer, Real
- **크기**: 8,760행 (365일 × 24시간), 변수 13개 + 대여 수 = 14열
- **결측치**: 없음 (UCI 표기와 실제 파일 모두 확인)

## 파일 정보 (실제 파일에서 확인)

- 파일: `data/raw/SeoulBikeData.csv`
- 기간: 2017-12-01 ~ 2018-11-30
- 인코딩: UTF-8이 아님. 비ASCII 문자는 컬럼명의 `°`(바이트 0xB0)뿐이며, `encoding='latin-1'`로 읽음
  - cp949로 읽으면 `°C`가 `캜`로 깨짐
- 결측치 0개, 중복 행 0개

## 변수 설명

UCI 변수 표의 설명과 단위에, 실제 파일에서 확인한 자료형과 값 범위를 함께 정리했습니다.

| 원본 컬럼명 | 변경한 컬럼명 | 설명 | 단위 | 실제 자료형 | 값 범위 (최소 ~ 최대) |
|---|---|---|---|---|---|
| `Date` | `date` | 날짜 | - | 문자열 (`dd/mm/yyyy`) | 2017-12-01 ~ 2018-11-30 |
| `Rented Bike Count` | `rented_bike_count` | 해당 시간의 대여 수 | 대 | 정수 | 0 ~ 3,556 (평균 704.6, 중앙값 504.5) |
| `Hour` | `hour` | 시간 | 시 | 정수 | 0 ~ 23 |
| `Temperature(°C)` | `temperature` | 기온 | °C | 실수 | -17.8 ~ 39.4 |
| `Humidity(%)` | `humidity` | 습도 | % | 정수 | 0 ~ 98 |
| `Wind speed (m/s)` | `wind_speed` | 풍속 | m/s | 실수 | 0 ~ 7.4 |
| `Visibility (10m)` | `visibility` | 가시거리 | 10m | 정수 | 27 ~ 2,000 (= 270m ~ 20km) |
| `Dew point temperature(°C)` | `dew_point_temp` | 이슬점 온도 | °C | 실수 | -30.6 ~ 27.2 |
| `Solar Radiation (MJ/m2)` | `solar_radiation` | 일사량 | MJ/m² | 실수 | 0 ~ 3.52 |
| `Rainfall(mm)` | `rainfall` | 강수량 | mm | 실수 | 0 ~ 35.0 |
| `Snowfall (cm)` | `snowfall` | 적설량 | cm | 실수 | 0 ~ 8.8 |
| `Seasons` | `seasons` | 계절 | - | 범주형 | Spring 2,208 / Summer 2,208 / Autumn 2,184 / Winter 2,160 |
| `Holiday` | `holiday` | 공휴일 여부 | - | 범주형 (2개 값) | No Holiday 8,328 / Holiday 432 |
| `Functioning Day` | `functioning_day` | 대여 서비스 운영 여부 | - | 범주형 (2개 값) | Yes 8,465 / No 295 |

## UCI 설명과 실제 파일이 다른 점

| 항목 | UCI 설명 | 실제 파일 | 이 프로젝트의 처리 |
|---|---|---|---|
| `Date` 형식 | year-month-day | `dd/mm/yyyy` (예: `01/12/2017` = 2017년 12월 1일) | `pd.to_datetime(..., dayfirst=True)`로 변환 |
| `Functioning Day` 값 | NoFunc / Fun | `No` / `Yes` | 값 그대로 사용 |
| `Rainfall`, `Snowfall` 자료형 | Integer | 소수 포함 (소수인 행: 강수 370개, 적설 369개) | 실수로 사용 |
| 역할(Role) | `Functioning Day`가 Target, `Rented Bike Count`는 Feature | - | **`Rented Bike Count`를 타깃(출력 변수)**으로 사용. 시간당 수요 예측이 목적이기 때문 |

## 데이터에서 발견한 특이사항

- **운영하지 않은 시간**: `Functioning Day == 'No'`인 295행은 대여 수가 전부 0이고, 대여 수가 0인 행은 이 295행뿐입니다. 운영하지 않아 생긴 0이라 수요로 볼 수 없으므로 전처리에서 제외했습니다.
- **humidity = 0인 17행**: 2018-05-19 ~ 05-28 새벽(2~7시)에 몰려 있고, 0 다음으로 작은 값은 10입니다. 같은 행의 기온과 이슬점으로 계산한 습도(Magnus 공식)는 33~72%여서 측정 오류로 판단했습니다. 전처리에서 계산값으로 바꿨습니다(정상 행에서 계산값과 기록값의 차이는 평균 0.24%p).
- **타깃 분포**: 오른쪽 꼬리가 깁니다(운영 시간 기준 왜도 1.14). 타깃 로그 변환을 실험했지만 성능이 좋아지지 않았습니다.
- **`Snowfall`의 의미**: UCI에는 단위(cm)만 있고, 그 시간에 새로 내린 눈인지 쌓인 눈인지는 설명되어 있지 않습니다.

전처리와 모델링 과정은 [project_summary.md](project_summary.md)에 정리되어 있습니다.

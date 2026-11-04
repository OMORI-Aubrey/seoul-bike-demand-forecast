"""프로젝트 공통 설정: 파일 경로, 랜덤 시드, 타깃 컬럼명

노트북이 어느 폴더에서 실행되든 같은 파일을 가리키도록 프로젝트 루트 기준으로 경로를 잡는다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_PATH = ROOT / 'data' / 'raw' / 'SeoulBikeData.csv'          # 원본 (수정 금지)
PROCESSED_DIR = ROOT / 'data' / 'processed'
CLEAN_PATH = PROCESSED_DIR / 'seoul_bike_clean.csv'              # 01에서 저장하는 정리본
RESULTS_DIR = ROOT / 'results'
EXPERIMENTS_PATH = RESULTS_DIR / 'experiments.csv'               # 04에서 저장하는 실험 결과
BEST_CONFIG_PATH = RESULTS_DIR / 'best_config.json'              # 04에서 저장, 05에서 읽는 최적 조합

SEED = 42
TARGET = 'rented_bike_count'

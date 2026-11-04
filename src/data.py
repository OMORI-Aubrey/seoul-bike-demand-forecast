"""노트북 사이에서 데이터를 주고받는 함수

- load_clean(): 01에서 저장한 정리본 읽기 (02, 03에서 사용)
- save_splits() / load_splits(): 03에서 분할·스케일링한 데이터를 저장하고 04, 05에서 읽기
"""
import pandas as pd

from src.config import CLEAN_PATH, PROCESSED_DIR, TARGET

SPLITS = ['train', 'val', 'test']


def load_clean():
    """정리본(UTF-8)을 읽고 date를 datetime으로 변환"""
    return pd.read_csv(CLEAN_PATH, parse_dates=['date'])


def save_splits(X_train, X_val, X_test, y_train, y_val, y_test):
    """분할된 데이터를 X_train.csv, y_train.csv ... 6개 파일로 저장"""
    for name, X, y in zip(SPLITS, [X_train, X_val, X_test], [y_train, y_val, y_test]):
        X.to_csv(PROCESSED_DIR / f'X_{name}.csv', index=False)
        y.to_csv(PROCESSED_DIR / f'y_{name}.csv', index=False)


def load_splits():
    """저장된 분할 데이터를 Keras 입력용 float32 배열로 읽기

    반환: X_train, X_val, X_test, y_train, y_val, y_test
    """
    X = [pd.read_csv(PROCESSED_DIR / f'X_{name}.csv').to_numpy('float32') for name in SPLITS]
    y = [pd.read_csv(PROCESSED_DIR / f'y_{name}.csv')[TARGET].to_numpy('float32') for name in SPLITS]
    return (*X, *y)

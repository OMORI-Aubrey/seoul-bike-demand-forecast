"""Keras 회귀 모델 생성과 학습 곡선 그리기 (04, 05 노트북에서 공통 사용)"""
import keras
import matplotlib.pyplot as plt

from src.config import SEED


def build_model(n_inputs, hidden_units, activation, learning_rate):
    """Dense 회귀 모델 생성

    hidden_units: 은닉층별 뉴런 수, 예) (128, 64, 32)
    출력층은 뉴런 1개, 활성화 함수 없음 / loss=MSE, metric=MAE, optimizer=Adam
    """
    keras.utils.set_random_seed(SEED)  # random, numpy, tensorflow 시드를 한 번에 고정
    model = keras.Sequential([keras.Input(shape=(n_inputs,))])
    for units in hidden_units:
        model.add(keras.layers.Dense(units, activation=activation))
    model.add(keras.layers.Dense(1))
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=learning_rate), loss='mse', metrics=['mae'])
    return model


def plot_history(history, title):
    """train / validation 의 loss(MSE)와 MAE 학습 곡선"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, key in zip(axes, ['loss', 'mae']):
        ax.plot(history.history[key], label='train')
        ax.plot(history.history[f'val_{key}'], label='validation')
        ax.set_xlabel('Epoch')
        ax.set_ylabel(key.upper())
        ax.set_title(f'{title} {key.upper()}')
        ax.legend()
        ax.grid(alpha=0.3)
    axes[0].set_yscale('log')
    plt.show()

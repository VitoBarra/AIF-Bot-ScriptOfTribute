import numpy as np

def Linear(x: np.ndarray) -> np.ndarray:
    return x

def ThanH(x: np.ndarray) -> np.ndarray:
    return np.tanh(x)

def Sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))

def LeakyReLU(x: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    return np.where(x > 0, x, alpha * x)

def ELU(x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    return np.where(x > 0, x, alpha * (np.exp(x) - 1))

def Softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)



ACTIVATION_FUNCTION_NAME_MAP = {
    "linear": Linear,
    "tanh": ThanH,
    "sigmoid": Sigmoid,
    "leaky_relu": LeakyReLU,
    "elu": ELU,
}

ACTIVATION_NAMES = list(ACTIVATION_FUNCTION_NAME_MAP.keys())

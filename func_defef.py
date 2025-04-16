import numpy as np
from numba import njit, float64, types
from numba.experimental import jitclass
import math


def hex_to_rgb(hex_color):
    # Убираем символ # в начале строки, если он есть
    hex_color = hex_color.lstrip('#')
    
    # Преобразуем строки в целые числа
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)

@njit
def gamma_function(n):
    return np.sqrt(2 * np.pi) * (n / np.e) ** n

@njit
def betta_function(n, m):
    if len(n) != len(m):
        raise ValueError('Массивы не одиннаковой длинны')
    return (gamma_function(n) * gamma_function(m)) / gamma_function(n + m)


spec = [
    ('a', float64), ('b', float64), ('c', float64), ('d', float64),
    ('e', float64), ('f', float64), ('g', float64), ('h', float64),
]

# norm(o): sqrt(a^2 + b^2 + ...)
@njit
def octonion_norm(o):
    return math.sqrt(np.sum(o ** 2))


# vector_norm(o): sqrt(b^2 + ... + h^2)
@njit
def octonion_vector_norm(o):
    return math.sqrt(np.sum(o[1:] ** 2))


# Сложение двух октанионов
@njit
def octonion_add(o1, o2):
    return o1 + o2


# Возведение октаниона в степень
@njit
def octonion_pow(o, p):
    vnorm = octonion_vector_norm(o)
    if vnorm == 0.0:
        return np.array([o[0] ** p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    mag = octonion_norm(o)
    theta = math.acos(o[0] / mag)

    log_q = np.empty(8)
    log_q[0] = math.log(mag)
    for i in range(1, 8):
        log_q[i] = o[i] / vnorm * theta

    # scale
    log_q *= p

    v = octonion_vector_norm(log_q)
    expa = math.exp(log_q[0])

    if v == 0.0:
        return np.array([expa, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    sin_v = math.sin(v)
    cos_v = math.cos(v)
    coef = sin_v / v

    result = np.empty(8)
    result[0] = expa * cos_v
    for i in range(1, 8):
        result[i] = expa * log_q[i] * coef

    return result
import numpy as np
from numba import njit, float64, types
from numba.experimental import jitclass
import math
import cmath


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



# norm(o): sqrt(a^2 + b^2 + ...)
@njit
def octonion_norm(o):
    return math.sqrt(np.sum(o ** 2))


# vector_norm(o): sqrt(b^2 + ... + h^2)
@njit
def octonion_vector_norm(o):
    return math.sqrt(np.sum(o[1:] ** 2))


@njit
def multiply_octonions(a, b, f=False):
    result = np.zeros(8)
    # Сокращения для удобства
    if f:
        a0, a1, a2, a3, a4, a5, a6, a7 = b
        b0, b1, b2, b3, b4, b5, b6, b7 = a
    else:
        a0, a1, a2, a3, a4, a5, a6, a7 = a
        b0, b1, b2, b3, b4, b5, b6, b7 = b        

    result[0] =  a0*b0 - a1*b1 - a2*b2 - a3*b3 - a4*b4 - a5*b5 - a6*b6 - a7*b7
    result[1] =  a0*b1 + a1*b0 + a2*b3 - a3*b2 + a4*b5 - a5*b4 - a6*b7 + a7*b6
    result[2] =  a0*b2 - a1*b3 + a2*b0 + a3*b1 + a4*b6 + a5*b7 - a6*b4 - a7*b5
    result[3] =  a0*b3 + a1*b2 - a2*b1 + a3*b0 + a4*b7 - a5*b6 + a6*b5 - a7*b4
    result[4] =  a0*b4 - a1*b5 - a2*b6 - a3*b7 + a4*b0 + a5*b1 + a6*b2 + a7*b3
    result[5] =  a0*b5 + a1*b4 - a2*b7 + a3*b6 - a4*b1 + a5*b0 - a6*b3 + a7*b2
    result[6] =  a0*b6 + a1*b7 + a2*b4 - a3*b5 - a4*b2 + a5*b3 + a6*b0 - a7*b1
    result[7] =  a0*b7 - a1*b6 + a2*b5 + a3*b4 - a4*b3 - a5*b2 + a6*b1 + a7*b0

    return result

# Возведение октаниона в степень
@njit
def _quaternion_conj(q):
    # сопряжение кватерниона
    return np.array([q[0], -q[1], -q[2], -q[3]])

@njit
def octonion_log(o):
    """
    Логарифм октаниона: log(o) = ln|o| + (v/|v|)*acos(o[0]/|o|)
    """
    mag = octonion_norm(o)
    if mag == 0.0:
        return np.zeros(8)

    vnorm = octonion_vector_norm(o)
    log_q = np.empty(8)
    log_q[0] = math.log(mag)
    if vnorm == 0.0:
        for i in range(1, 8):
            log_q[i] = 0.0
    else:
        theta = math.acos(o[0] / mag)
        for i in range(1, 8):
            log_q[i] = o[i] / vnorm * theta
    return log_q

@njit
def octonion_exp(o):
    """
    Экспонента октаниона: exp(a + v) = e^a [cos|v| + (v/|v|) sin|v|]
    """
    expa = math.exp(o[0])
    vnorm = octonion_vector_norm(o)
    result = np.empty(8)
    result[0] = expa * math.cos(vnorm)
    if vnorm == 0.0:
        for i in range(1, 8):
            result[i] = 0.0
    else:
        coef = expa * math.sin(vnorm) / vnorm
        for i in range(1, 8):
            result[i] = o[i] * coef
    return result

@njit
def octonion_pow(o, w):
    """
    Возведение октаниона o в октанион-показатель w: exp(w * log(o)).
    При mag(o)=0 возвращает нулевой октанион.
    """
    # вычисляем логарифм o
    log_o = octonion_log(o)
    # умножаем октанионы w и log_o
    prod = multiply_octonions(w, log_o)
    # и берём экспоненту
    return octonion_exp(prod)

@njit
def make_octonion(real, i=0.0, j=0.0, k=0.0, l=0.0, m=0.0, n=0.0, o=0.0):
    """
    Конструктор октаниона:
      real — действительная часть,
      i, j, k, l, m, n, o — коэффициенты мнимых ед.
    По умолчанию все мнимые части 0.0.
    """
    return np.array([real, i, j, k, l, m, n, o], dtype=np.float64)

@njit
def divide_octonions(a, b):
    """
    Деление октанионов a / b, безопасно: при нулевом b возвращает нулевой октанион.
    Внутри реализовано умножение через схему Кэли–Диксона без вызова внешних функций.
    """
    # квадрат нормы делителя
    norm_sq = 0.0
    for i in range(8):
        norm_sq += b[i] * b[i]
    if norm_sq == 0.0:
        return np.zeros(8)

    # обратный октанион b
    b_conj = np.empty(8)
    b_conj[0] =  b[0]
    for i in range(1, 8):
        b_conj[i] = -b[i]
    b_inv = b_conj / norm_sq

    # разбиение на кватернионы по Кэли–Диксону
    a0, a1 = a[:4], a[4:]
    c0, c1 = b_inv[:4], b_inv[4:]
    conj_c0 = _quaternion_conj(c0)
    conj_c1 = _quaternion_conj(c1)

    # inline умножение кватернионов (функция qmul)
    def qmul(u, v):
        return np.array([
            u[0]*v[0] - u[1]*v[1] - u[2]*v[2] - u[3]*v[3],
            u[0]*v[1] + u[1]*v[0] + u[2]*v[3] - u[3]*v[2],
            u[0]*v[2] - u[1]*v[3] + u[2]*v[0] + u[3]*v[1],
            u[0]*v[3] + u[1]*v[2] - u[2]*v[1] + u[3]*v[0],
        ])

    # (a0,a1)*(c0,c1) = (a0·c0 - conj(c1)·a1, c1·a0 + a1·conj(c0))
    part0 = qmul(a0, c0) - qmul(conj_c1, a1)
    part1 = qmul(c1, a0) + qmul(a1, conj_c0)

    # собираем результат обратно в 8-мерный вектор
    res = np.empty(8)
    res[:4] = part0
    res[4:] = part1
    return res

@njit
def step(arr, shift=1):
    n = len(arr)
    result = np.empty(n, dtype=arr.dtype)
    for i in range(n):
        result[(i + shift) % n] = arr[i]
    return result




@njit
def octonion_sin(o, n=0):
    num_bits = 32

    # Получаем двоичное представление числа в виде списка бит
    s = [(n >> i) & 1 for i in range(num_bits)]  # Сдвигаем и извлекаем биты

    # Используем побитовые значения
    io = multiply_octonions(make_octonion(0, 1), o, s[0] == 1)
    neg_io = multiply_octonions(make_octonion(0, -1), o, s[1] == 1 if len(s) > 1 else False)
    temp1 = octonion_exp(io)
    temp2 = octonion_exp(neg_io)
    diff = temp1 - temp2
    denom = multiply_octonions(make_octonion(0, 1), make_octonion(2), s[2] == 1 if len(s) > 2 else False)
    
    return divide_octonions(diff, denom)

@njit
def octonion_cos(o, n=0):
    num_bits = 32

    # Получаем двоичное представление числа в виде списка бит
    s = [(n >> i) & 1 for i in range(num_bits)]  # Сдвигаем и извлекаем биты

    # Используем побитовые значения для вычисления косинуса
    io = multiply_octonions(make_octonion(0, 1), o, s[0] == 1)
    neg_io = multiply_octonions(make_octonion(0, -1), o, s[1] == 1 if len(s) > 1 else False)
    temp1 = octonion_exp(io)
    temp2 = octonion_exp(neg_io)
    
    # Вычисление косинуса (среднее значение экспоненциальных функций)
    return (temp1 + temp2) / 2

@njit
def octonion_tan(o, n1=0, n2=0):
    return divide_octonions(octonion_sin(o, n1), octonion_cos(o, n2))

@njit
def octonion_cot(o, n1=0, n2=0):
    return divide_octonions(octonion_cos(o, n1), octonion_sin(o, n2))

@njit
def octonion_sec(o, n=0):
    return divide_octonions(make_octonion(1.0), octonion_cos(o, n))

@njit
def octonion_csc(o, n=0):
    return divide_octonions(make_octonion(1.0), octonion_sin(o, n))

# Гиперболические функции
@njit
def octonion_sinh(o):
    return divide_octonions((octonion_exp(o) - octonion_exp(-o)), make_octonion(2.0))

@njit
def octonion_cosh(o):
    return divide_octonions((octonion_exp(o) + octonion_exp(-o)), make_octonion(2.0))

@njit
def octonion_tanh(o):
    return divide_octonions(octonion_sinh(o), octonion_cosh(o))

@njit
def octonion_coth(o):
    return divide_octonions(octonion_cosh(o), octonion_sinh(o))

@njit
def octonion_sech(o):
    return divide_octonions(make_octonion(1.0), octonion_cosh(o))

@njit
def octonion_csch(o):
    return divide_octonions(make_octonion(1.0), octonion_sinh(o))

# Арк-функции
@njit
def octonion_arcsin(o, n=0):
    s = [(n >> i) & 1 for i in range(4)]
    io = multiply_octonions(make_octonion(0, 1), o, bool(s[0]))
    o2 = multiply_octonions(o, o, bool(s[1]))
    sqrt_term = octonion_pow(make_octonion(1.0) - o2, make_octonion(0.5))
    term = multiply_octonions(make_octonion(0, 1), sqrt_term, bool(s[2]))
    log_val = octonion_log(io + term, n)
    return -multiply_octonions(make_octonion(0, 1), log_val, bool(s[3]))


@njit
def octonion_arccos(o, n=0):
    return make_octonion(math.pi / 2) - octonion_arcsin(o, n)

@njit
def octonion_arctan(o, n=0):
    s = [(n >> i) & 1 for i in range(2)]
    io = multiply_octonions(make_octonion(0, 1), o, bool(s[0]))
    half = (
        octonion_log(make_octonion(1.0) + io, n) - octonion_log(make_octonion(1.0) - io, n)) / make_octonion(2.0)
    return multiply_octonions(make_octonion(0, 1), half, bool(s[1]))


@njit
def octonion_arccot(o, n=0):
    return octonion_arctan(make_octonion(1.0) / o, n)

@njit
def octonion_arcsec(o, n=0):
    return octonion_arccos(make_octonion(1.0) / o, n)

@njit
def octonion_arccsc(o, n=0):
    return octonion_arcsin(make_octonion(1.0) / o, n)

@njit
def octonion_arsinh(o):
    sqrt_term = octonion_pow(octonion_pow(o, make_octonion(2)) + make_octonion(1.0), make_octonion(0.5))
    return octonion_log(o + sqrt_term)

@njit
def octonion_arcosh(o):
    sqrt_term = octonion_pow(octonion_pow(o, make_octonion(2)) - make_octonion(1.0), make_octonion(0.5))
    return octonion_log(o + sqrt_term)

@njit
def octonion_artanh(o):
    log_num = octonion_log(make_octonion(1.0) + o)
    log_den = octonion_log(make_octonion(1.0) - o)
    return (log_num - log_den) / 2

@njit
def octonion_arcoth(o):
    log_num = octonion_log(o + make_octonion(1.0))
    log_den = octonion_log(o - make_octonion(1.0))
    return (log_num - log_den) / 2

@njit
def octonion_arsech(o):
    return octonion_arcosh(make_octonion(1.0) / o)

@njit
def octonion_arcsch(o):
    return octonion_arsinh(make_octonion(1.0) / o)

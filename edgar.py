from sympy import symbols, Function, sympify, Max
import numpy as np
import math

def safe_abs_np(vec):
    real_abs = np.abs(vec.real)
    imag_abs = np.abs(vec.imag)
    
    # Вычисляем максимальную величину между вещественной и мнимой частью
    s = np.maximum(real_abs, imag_abs)
    
    # Избегаем деления на ноль, заменяя нули в real_abs и imag_abs на маленькие значения (например, 1e-10)
    epsilon = 1e-10
    normalized_real = np.where(s != 0, real_abs / (s + epsilon), 0)
    normalized_imag = np.where(s != 0, imag_abs / (s + epsilon), 0)
    
    # Возвращаем модуль
    return np.where(s == 0, 0, s * np.sqrt(normalized_real**2 + normalized_imag**2))


# Пример использования
vec = np.array([1+2j, 3+4j, 0+0j])  # Пример комплексного вектора
result = safe_abs_np(vec)
print(result)



# Объявляем переменные
z, c, i = symbols('z c i')

# Кастомная функция
class mod(Function):
    @classmethod
    def eval(self, value):
        return 


local={
    'mod': mod
}

def transform(string):
    return sympify(string, locals=local)

def result_count(code, value):
    return code.evalf(subs=value)



#print(transform(string))

import textwrap
from numba import njit, prange
from types import FunctionType
from typing import Callable, Dict
from func_defef import gamma_function, betta_function, octonion_norm, octonion_vector_norm, octonion_add, octonion_pow
import numpy as np


@njit
def z_index(z, gradient, iteration, max_iterations, scale_type, log_type, escape_radius):
    n_colors = gradient.shape[0]
    
    # Вычисляем нормированное значение для выбора цвета
    if scale_type == "linear":
        return  iteration % len(gradient)
    else:
        if iteration <= 0:
            index = 0
        else:
            alpha = np.log(iteration) / np.log(max_iterations) 
            endet = np.log(1 + escape_radius)
            if log_type == "beautiful":
                zet = 1
            else:
                zet = np.log(1 + octonion_norm(z))
            alpha = alpha * endet * zet
            index = alpha * (len(gradient) - 1)
    
    
        return int(index % len(gradient))

def compiledExpression(expr: str, functions: list):
    # Словарь с контекстом для функций, которые будут использоваться
    context = {name: func for name, func in functions}

    # Создаем строку кода с динамически вычисляемым выражением
    # Переменные (их имена) передаем как параметры функции
    code = textwrap.dedent(f"""
        import numpy as np  # Добавляем импорт numpy
        @njit(parallel=True)
        def compiled_func(wi, vi, ui, ti, zi, hi, yi, x, max_iterations, escape_radius, gradient, color3, scale_type, log_type, if_while, len_colors):
            colors = np.zeros((len(x), 3), dtype=np.uint8)  # Массив для цветов
            for len_x in prange(len(x)):  # Проходим по всем элементам x
                xi = x[len_x]
                c = np.array([xi, yi, hi, zi, ti, ui, vi, wi])
                z = np.array([xi, yi, hi, zi, ti, ui, vi, wi])
                for i in range(max_iterations):
                    # Применяем переданное выражение прямо в коде
                    z = {expr}
                    
                    if z is None:
                        colors[len_x] = gradient[0]
                        break
                    elif norm(z) >= escape_radius:
                        colors[len_x] = gradient[z_index(z, gradient, i, max_iterations, scale_type, log_type, escape_radius)]
                        break
                if i == max_iterations - 1:
                    colors[len_x] = color3
            return colors
    """)

    # Контекст для exec
    exec_context = {'njit': njit}  # Добавляем только необходимое из контекста
    exec_context.update(context)

    # Компиляция и возвращение скомпилированной функции
    exec(code, exec_context)
    return exec_context['compiled_func']


def cot(vector):
    return 1 / np.tan(vector)

def arccot(vector):
    return np.arctan(1 / vector)

def arccoth(vector):
    return 0.5 * np.log((vector + 1) / (vector - 1))

def coth(vector):
    return np.cosh(vector) / np.sinh(vector)

functions = np.array([
   ('z_index', z_index),  
   ('mod', np.linalg.norm), 
   ('sin', np.sin), 
   ('cos', np.cos),
   ('tg', np.tan),
   ('ctg', cot),
   ('sinh', np.sinh),
   ('cosh', np.cosh),
   ('tgh', np.tanh),
   ('ctgh', coth),
   ('sqrt', np.sqrt),
   ('exp', np.exp),
   ('log', np.log),
   ('log10', np.log10),
   ('log2', np.log2),
   ('arcsin', np.arcsin),
   ('arccos', np.arccos),
   ('arctg', np.arctan),
   ('arcctg', arccot),
   ('arcsinh', np.arcsinh),
   ('arccosh', np.arccosh),
   ('arctgh', np.arctanh),
   ('arcctgh', arccoth),
   ('gamma', gamma_function), 
   ('betta', betta_function), 
   ('prange', prange), 
   ('norm', octonion_norm), 
   ('vector_norm', octonion_vector_norm), 
   ('add', octonion_add), 
   ('pow', octonion_pow)
   ])



"""


# Пример проверки:
triple = np.array([1, 2j, 0])
power = 2
res_array = triple_pow(triple, power)
res_complex = complex(1, 2) ** 2

print("Результат в виде массива:", res_array)
print("Результат комплексного возведения:", res_complex)
"""

"""
z = Octonion(1.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0)
c = Octonion(1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
z = z ** 2 + c
print(z)
"""
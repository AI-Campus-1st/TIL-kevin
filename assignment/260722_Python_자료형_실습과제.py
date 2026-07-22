print('ax^2+bx+c = 0에서 a, b, c 값을 순서대로 입력하시오.')
a = input('a에 해당하는 값 입력: ')
'''
if a == 0:
    print('이차방정식만 해당됩니다') '''
b = input('b에 해당하는 값 입력: ')
c = input('c에 해당하는 값 입력: ')
a = float(a)
b = float(b)
c = float(c)
print([a, b, c])
D = (b**2)-(4*a*c)
print('D = ', D)
print('두 근의 값: ', ((-1*b)+(D**0.5))/(2*a), ', ',\
       ((-1*b)-(D**0.5))/(2*a))
type(((-1*b)+(D**0.5))/(2*a))
'''
import math
a = float(a)
b = float(b)
c = float(c)
D = pow(b, 2) - (4*a*c)
print('D = ', D)
print('두 실근의 값: ', round(((-1 * b) + (math.sqrt(D)))/(2 * a), 4), ', ',\
       round(((-1 * b) - (math.sqrt(D)))/(2 * a), 4))
'''
'''
허근일 경우 round()로 반올림이 안 되는데 이런 경우 소수점 정리는 어떻게 하나요?
출력값을 소수점 말고 분수 형태로 표현하는 방법도 알고 싶습니다
(지자분하게 하면 가능은 할 것 같은데 별도의 함수가 있는지 궁금합니다)
조건문에 대해 배우면 a == 0일 때 거부하는 분기를 만들 수 있을 것 같습니다
'''
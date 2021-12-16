d = {0: 'Zero', 1: 'One', 4: 'Four', 5:'Unknown'}
d[3] = 'Three'

y = str(d.get(0,'unknown'))+str(d.get(3,'unknown'))+str(d.get(2,'unknown')) 
print(y)
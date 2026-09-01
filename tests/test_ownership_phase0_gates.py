import numpy as np
def test_quadratic_projection_monotonic():
    k=np.asarray([128,256,512],dtype=float); t=0.001*k*k+2; c=np.polyfit(k*k,t,1); assert c[0]>0 and c[0]*4096**2+c[1]>c[0]*2048**2+c[1]

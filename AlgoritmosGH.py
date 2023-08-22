from scipy import signal
from sklearn.decomposition import NMF
import numpy as np
from ezc3d import c3d
import random
import math
import pandas as pd



class Algoritmos:
    
    def recortarVectores(self, eventos_lado, eventos_contexto, eventos_tiempo):
        eventos_contexto_recortado = []
        eventos_tiempo_recortado = []
        eventos_lado_recortado = []

        #Recorto los vectores
        for i in range (len(eventos_contexto)):  
            if "EMG" in eventos_contexto[i]:
                eventos_contexto_recortado.append(eventos_contexto[i])
                eventos_tiempo_recortado.append(eventos_tiempo[1][i])
                eventos_lado_recortado.append(eventos_lado[i])
        
        return eventos_contexto_recortado,eventos_tiempo_recortado,eventos_lado_recortado
    
    def ordenarTemporalmente(self, eventos_lado_recortado, eventos_contexto_recortado, eventos_tiempo_recortado):
        eventos_tiempo_recortado_2 = eventos_tiempo_recortado  
        eventos_lado_ordenado=sorted(zip(eventos_tiempo_recortado, eventos_lado_recortado)) 
        eventos_contexto_ordenado=sorted(zip(eventos_tiempo_recortado_2, eventos_contexto_recortado))
                
        tiempos = []
        lados = []
        contextos = []

        for x, y in eventos_lado_ordenado:
            tiempos.append(x)
            
        for x, y in eventos_lado_ordenado:
            lados.append(y)
            
        for x, y in eventos_contexto_ordenado:
            contextos.append(y)
            
        
        return tiempos,lados,contextos    
    
    def obtenerPasos(self, lados, contextos, paciente):
        
        paso_izquierdo = ['Left', 'Rigth', 'Rigth','Left', 'Left']
        paso_derecho = ['Rigth', 'Left', 'Left','Rigth', 'Rigth']
        paso_eventos = ['EMG_Heel_Strike', 'EMG_Heel_Off','EMG_Heel_Strike', 'EMG_Heel_Off','EMG_Heel_Strike']
        
        for i in range(len(lados)-len(paso_derecho)+1):
            if(lados[i]==paso_derecho[0] and
               contextos[i] == paso_eventos[0] and
               lados[i+1]==paso_derecho[1] and
               contextos[i+1] == paso_eventos[1] and
               lados[i+2]==paso_derecho[2] and
               contextos[i+2] == paso_eventos[2] and
               lados[i+3]==paso_derecho[3] and
               contextos [i+3] == paso_eventos[3] and
               lados[i+4]==paso_derecho[4] and
               contextos [i+4]== paso_eventos[4]):
                print ("Coincidencia paso derecho")
                paciente.pasos.append(['d', i])
                

        for i in range(len(lados)-len(paso_izquierdo)+1):
            if(lados[i]==paso_izquierdo[0] and
               contextos[i] == paso_eventos[0] and
               lados[i+1]==paso_izquierdo[1] and
               contextos [i+1]== paso_eventos[1] and
               lados[i+2]==paso_izquierdo[2] and
               contextos [i+2] == paso_eventos[2] and
               lados[i+3]==paso_izquierdo[3] and
               contextos [i+3] == paso_eventos[3] and
               lados[i+4]==paso_izquierdo[4] and
               contextos [i+4] == paso_eventos[4]):
                print ("Coincidencia paso izquierdo")
                paciente.pasos.append(['i', i])
                
        
        return paciente.pasos
    
    def obtenerPasosC3d(self, paciente, directorioC3D):
        
        #c = c3d('SujetoNoPatologico1.c3d')
        c=c3d(directorioC3D)
        print(c['parameters']['POINT']['USED']['value']);  # Print the number of points used
        #point_data = c['data']['points']
        #points_residuals = c['data']['meta_points']['residuals']
        #analog_data = c['data']['analogs']
        #Abro informacion necesaria del C3d
        eventos_lados = c['parameters']['EVENT']['CONTEXTS']['value']
        eventos_tiempos = c['parameters']['EVENT']['TIMES']['value']
        eventos_contextos = c['parameters']['EVENT']['LABELS']['value']
        
        tiempos= []
        lados= []
        contextos = []
        
        contextos, tiempos,lados = Algoritmos().recortarVectores(eventos_lados, eventos_contextos, eventos_tiempos)
        tiempos,lados,contextos = Algoritmos().ordenarTemporalmente(lados, contextos, tiempos)
        paciente.pasos = Algoritmos().obtenerPasos(lados, contextos, paciente)
            
    def obtenerNumeroDeMuestrasDePaso (self, pasoElegido, tiempos):
        
        tiempoInicial=tiempos[pasoElegido[1]]
        tiempoFinal=tiempos[pasoElegido[1]+4]

        #Calculo el numero de muestras correspondietes al paso

        N_ti = round(tiempoInicial * 2000)
        print ("Tiempo: ")
        print (tiempoInicial)
        print ("Tiempo: ")
        print (tiempoFinal)
        N_tf = round(tiempoFinal * 2000)
        
        return N_ti, N_tf
    
    def obtenerPasosExcel(self, sujetoSujetoNoPatologico, df):


        pasos = []
        pasos_final=[]
        
        filas = []
        for i in range(2):
            filas.append(df.iloc[i].tolist())
            
        filas = [fila[1:] for fila in filas]
        filas[0] = [elem[:-1] for elem in filas[0]]
        

        etiquetas = filas[0]
        valores = filas[1]
        new_etiquetas=[]
        new_valores=[]
        
        for i in range(len(etiquetas)):
            if not math.isnan(valores[i]) and (i == 0 or etiquetas[i] != etiquetas[i-1] or valores[i] != valores[i-1]):
                new_etiquetas.append(etiquetas[i])
                new_valores.append(valores[i])

        filas = [new_etiquetas,new_valores]
        
        eventos_ordenados = sorted(zip(filas[1], filas[0])) 
        
                    
        for i in range (len(eventos_ordenados)-4):
            if (eventos_ordenados[i][1] == "RHS" and 
                eventos_ordenados[i+1][1] == "LTO" and
                eventos_ordenados [i+2][1] == "LHS" and
                eventos_ordenados [i+3][1] == "RTO" and
                eventos_ordenados [i+4][1] == "RHS"):
                    
                paso=['d', eventos_ordenados[i][0],eventos_ordenados[i+1][0],eventos_ordenados[i+2][0],eventos_ordenados[i+3][0], eventos_ordenados[i+4][0]]
                pasos.append(paso)

            if (eventos_ordenados[i][1] == "LHS" and 
               eventos_ordenados[i+1][1] == "RTO"  and
               eventos_ordenados [i+2][1] == "RHS" and
               eventos_ordenados [i+3][1] == "LTO" and
               eventos_ordenados [i+4][1] == "LHS"):
                   
               paso=['i',eventos_ordenados[i][0],eventos_ordenados[i+1][0],eventos_ordenados[i+2][0],eventos_ordenados[i+3][0], eventos_ordenados[i+4][0]]
               pasos.append(paso)

        paso_izq = []
        paso_der = []
             
        for paso in pasos:
            if paso[0]=="i":
                paso_izq.append(paso)
            if paso[0]=="d":
                paso_der.append(paso)
        
        if(len(paso_izq)>0):
            pasos_final.append(paso_izq[random.randint(0, len(paso_izq)-1)])
        if(len(paso_der)>0):
            pasos_final.append(paso_der[random.randint(0, len(paso_der)-1)])

        return pasos_final
            

        
    def calcularEnvolvente(self, vector,fm):
        
        #Pongo f_inf f_sup 
        
        # b, a = signal.butter(3, [2*20/fm, 2*400/fm], 'bandpass')  
        f_inf_pasabanda=20
        f_sup_pasabanda=400
        f_pasa_bajo=3

        if fm==500:
            f_sup_pasabanda=200
            
        #Esto es asi porque la frecuencia de corte SujetoNoPatologicoizada tiene que estar entre 0 y 1    
        
        b, a = signal.butter(3, [2*f_inf_pasabanda/fm, 2*f_sup_pasabanda/fm], 'bandpass')  
        EMG_pasaBanda = signal.filtfilt(b, a, vector)

        EMG_rectificado = abs (EMG_pasaBanda)

        b, a = signal.butter(3, 2*f_pasa_bajo/fm, 'lowpass')   #Configuration filter 8 representa el orden del filtro
        envolvente = signal.filtfilt(b, a, EMG_rectificado)  #data es la señal a filtrar
            
        return envolvente
                
    def convertirATension(self, vector):
        aux = []
        for x in vector:
            aux.append(x*(5)/(2**12))
        return aux
    
    def calcularVariacionSinergia(self, EMG):
        for i in range (len(EMG)):
            for j in range (len(EMG[i])):
                if (EMG[i][j]<0):
                    EMG[i][j]=0
                
        V=EMG
        variacion=[]
        sinergias = []
        
        for i in range (0, 8):
            model = NMF(n_components=(i+1), init='random', random_state=0, max_iter=50000)
            W = model.fit_transform(V)
            H = model.components_
            d_aprox=np.dot(W[:,:i],H[:i,:])
            sinergias.append([W,H,1-(np.linalg.norm(V-d_aprox)**2)/np.linalg.norm(V)**2])
            
        return sinergias
    
    def SujetoNoPatologicoize_list(lst):
        max_val = max(lst)
        if max_val == 0:
            return lst
        else:
            return [float(i)/max_val for i in lst]
    
    def obtenerEMGProcesado(self, sujetoSujetoNoPatologico, pasos):
        EMG = []
        EMG_interpolado = []
        EMG_recortado= [] 
        EMG_procesado = []    

        
            
        for i in sujetoSujetoNoPatologico.EMGs:
            #if sujetoSujetoNoPatologico.Id!="SujetoNoPatologico2":
            EMG.append(i)        
        
        for idx, lst in enumerate(EMG):
            lst_norm = Algoritmos.SujetoNoPatologicoize_list(lst) # SujetoNoPatologicoizar la señal
            lst_env = Algoritmos().calcularEnvolvente(lst_norm, 2000) # calcular la envolvente de la señal
            EMG[idx] = lst_env # reemplazar la lista original con la lista interpolada y SujetoNoPatologicoizada

        for lst in EMG:
            for j in range(len(lst)):
                if lst[j] < 0:
                    lst[j] = abs(lst[j])
        
        for idx, lst in enumerate(EMG_recortado):
            x = np.linspace(0, len(lst) * 1 / 2000, 100)
            t = np.linspace(0, len(lst) * 1 / 2000, len(lst))
            y = lst
            EMG_interpolado = np.interp(x, t, y) # interpolar la señal
            EMG_procesado.append(EMG_interpolado) # reemplazar la lista original con la lista interpolada y SujetoNoPatologicoizada
        


        return EMG_procesado
            
  
        

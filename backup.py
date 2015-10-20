#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,datetime,json
DIR_BASE = "/root/backup/"
DIR_BACKUP = "/srv/backup/"
HOY = datetime.datetime.now()
HOY = HOY.strftime("%d_%m_%Y")

# Función que ejecuta un comando, si se produce algún error lo especifíca
def run(comando):
        res=os.system(comando)
        if res!=0:
                print "Error al ejecutar %s" % comando

# Función que devuelve el comando rdiff-backup que se va a ejecutar. Recibe el servidor, el directorio origen y el directorio destino.
def makeCommand(servidor,dirOrig,dirDest):
        return "rdiff-backup root@%s::%s %s" % (servidor,dirOrig,dirDest)

# Función que devuelve la ruta donde se va a realizar la copia. Formado por la constante DIR_BACKUP/nombre del servidor/directorio de copia.
def makedirDest(servidor,dirDest,dirCopia=""):
        return DIR_BACKUP+dirDest+"/"+servidor+"/"+dirCopia

# Función que recibe el directorio donde se va a realizar una copia y comprueba cuantos directorios de copia completas existen (numerados como 01,02,...). 
# Devuelve un diccionario con los siguientes campos: dirCompAct: el número del directorio donde se está realizando las copias incrementales actualmente.
# dirCompSig: El siguiente número de directorio, por si se tiene que crear una nueva copia completa.
# dircompBorrar: Indica el directorio de copia completa que hay que borrar por que se ha llegado al número máximo, "0" en caso de que no haya que borrar ninguno.
def examDir(dirDest,n_max_copias):
        for root, dirs, files in os.walk(dirDest):
                break
        if len(dirs)==0:
                dirs.append("0")
        dirs_num = [int(i) for i in dirs]
        dirs_num.sort(reverse=True)
        response={}
        response["dirCompAct"]=str(dirs_num[0])
        response["dirCompSig"]=str(dirs_num[0]+1)
        dirs_num.sort()
        if len(dirs_num)==n_max_copias:
                response["dirCompBorrar"] = str(dirs_num[0])
        else:
                response["dirCompBorrar"]="0"

        return response

# Función que ejecuta una copia total. Recibe el servidor, directorio origen, directorio destino. Si recibe el indicador yCompleta realiza también una copia completa.
def copiaTotal(servidor,dirOrig,dirDest,yCompleta=False):
        run(makeCommand(servidor,dirOrig,dirDest+"total_"+HOY))
        run ("tar cvzf %stotal_%s.tar.gz %s>/dev/null" % (dirDest,HOY,dirDest+"total_"+HOY))
        if yCompleta:
                run("mv %stotal_%s %s1" % (dirDest,HOY,dirDest))
        else:
                run ("rm -r %s" % dirDest+"total_"+HOY)
# Función que incrementa el contador de copias realizadas que se guarda en el fichero backuo.cont
def incContador():
        try:
                archi=open(DIR_BASE+'backup.cont','r')
                linea=archi.readline()
                archi.close()
                archi=open(DIR_BASE+'backup.cont','w')
                archi.write(str(int(linea)+1))
                archi.close
        except:
                print "Error en el fichero contador"
                exit()
        return int(linea)

# Función que lee el fichero de configuración backup.conf
def loadCopias():
        try:
                json_data=open(DIR_BASE+'backup.json')
                data = json.load(json_data)
        except:
                print "Error en la configuración"
                exit()
        json_data.close()
        return data

# Programa principal

copias = loadCopias()
DIAS = incContador()
print "Copia %s" % DIAS
print "="*20
# Por cada una de la tareas de copia de seguridad definidas en e fichero de configuración
for copia in copias:
        for servidor in copia["servidores"]:
                dirDest=makedirDest(servidor,copia["dirDest"])
                # Si es la primera vez que se encuentra esta tarea de backup
                if not os.path.isdir(dirDest):
                        # Copia total
                        os.system ("mkdir -p %s" % dirDest)
                        copiaTotal(servidor,copia["dirOrig"],dirDest,True)
                        # Primera copia completa
                        print "Copia Total %s %s %s" % (servidor,copia["copia"],HOY)
                else:
                        # Copia total
                        if DIAS % copia["copiaT"]==0:
                                copiaTotal(servidor,copia["dirOrig"],dirDest)
                                print "Copia Total %s %s %s" % (servidor,copia["copia"],HOY)

                        # Copia completa
                        elif DIAS % copia["copiaC"]==0:
                                res=examDir(dirDest,copia["n_max_comp"])
                                run (makeCommand(servidor,copia["dirOrig"],dirDest+res["dirCompSig"]))
                                if res["dirCompBorrar"]!="0":
                                        run ("rm -r %s" % dirDest+res["dirCompBorrar"])
                                print "Copia Completa %s %s %s" % (res["dirCompSig"],servidor,copia["copia"])
                                if res["dirCompBorrar"]!="0":
                                        print "Borrando copias: "+res["dirCompBorrar"]

                        # Copia incremental
                        elif DIAS % copia["copiaI"]==0:
                                res=examDir(dirDest,copia["n_max_comp"])
                                run(makeCommand(servidor,copia["dirOrig"],dirDest+res["dirCompAct"]))
                                print "Copia incremental %s %s %s" % (res["dirCompAct"],servidor,copia["copia"])

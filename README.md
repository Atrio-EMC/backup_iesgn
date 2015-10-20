# backup_iesgn

Script python para automatizar los backup en el IES Gonzalo Nazareno.

Script en python que automatiza las copias de seguridad en la infraestructura del IES Gonzalo Nazareno. Se debe programa su ejecución en el cron, por ejemplo.

		0 1 * * * python /root/backup/backup.py >> /srv/backup/backup.log

El fichero de configuración está escrito en JSON, y es una lista de diccionarios con los siguientes campos:

* copia: Descripción de la tarea de copia de seguridad
* dirDest: Directorio donde se va a guardar los datos copiados.
* servidores: Lista de los servidores donde se va a realizar la copia.
* dirOrig: Directorio que se va a copiar.
* copiaT: Cada cuantos días se va a hacer una copia total.
* copiaC: Cada cuantos días se va a hacer una copia completa.
* copiaI: Cada cuantos días se va a hacer una copia incremental.
* n_max_comp: Rotación del las copias totales.

Ejemplo de fichero backup.conf:

		[
		{"copia":"pagina web",
		"dirDest":"pagina_web",
		"servidores":["www.iesgn.org"],
		"dirOrig":"/srv",
		"copiaT":365,"copiaC":60,"copiaI":1,"n_max_comp":2
		},
		...
		]
Se hace una copia total cada 365 días del directorio /srv, del servidor www.iesgn.org, y se guarda en el directorio "pagina_web". Cada 60 días se hace una copia completa, y cada día se hace una incremental. Sólo se guardan las dos últimas copias completas.

Los tipos de copias que se realizan son las siguientes:

* Copia total: Se guarda el directorio comprimido con tar.gz.
* Copia completa: Se van guardando en directorios (numerados como 01,02,...) la copia completa del directorio a copiar.
* Copia incremental: En las copias completas se van guardando los ficheros que se han modificaco desde la última copia completa o incremental.

El script utiliza la herramienta [rdiff-backup](http://www.nongnu.org/rdiff-backup/) para realizar las copias completas e incrementales. Por lo tanto en los servidores donde queremos realizar las copias, tenemos que instalar el programa rdiff-backup y además deben ser accesibles por ssh (utilizando clave rsa para la autentificación ssh).
# MariaDB Local Backup Tool

Script en Python para realizar backup completo de todas las bases de datos de un servidor MariaDB en Ubuntu 22.04.

## Características

* Un archivo `.sql` por cada base de datos
* Compresión individual en formato `.sql.gz`
* Verificación de integridad del dump
* Exclusión automática de bases del sistema
* Solicitud segura de contraseña (no queda en historial)
* Estructura modular orientada a clases

---

## Requisitos

* Ubuntu 22.04
* MariaDB 10.6.x
* Python 3.10 o superior
* mysqldump disponible en el sistema

Verificar instalación:

```bash
mysql --version
mysqldump --version
python3 --version
```

---

## Estructura del Proyecto

```
mariadb-backup/
│
├── mariadb_backup.py
└── README.md
```

---

## Configuración

Dentro del archivo `mariadb_backup.py` se define la configuración principal:

```python
config = MariaDBBackupConfig(
    user="root",
    password=password,
    backup_dir="/home/sal/backups/mariadb"
)
```

Bases excluidas automáticamente:

* information_schema
* performance_schema
* mysql
* sys

---

## Uso

Ejecutar:

```bash
python3 mariadb_backup.py
```

El script solicitará la contraseña del usuario root.

---

## Resultado del Backup

Por cada base se generará un archivo con el formato:

```
nombre_base_YYYYMMDD_HHMMSS.sql.gz
```

Ejemplo:

```
clientes_20260224_013012.sql.gz
pagos_20260224_013013.sql.gz
```

---

## Validaciones que realiza el script

* Verifica código de salida de mysqldump
* Verifica que el archivo `.sql` no esté vacío
* Comprime usando gzip
* Realiza lectura de prueba del archivo comprimido
* Verifica que el archivo `.gz` no esté vacío
* Elimina archivos incompletos si ocurre un error

---

## Restauración

Restaurar una base:

```bash
gunzip archivo.sql.gz
mysql -u root -p nombre_base < archivo.sql
```

Restaurar sin descomprimir manualmente:

```bash
gunzip -c archivo.sql.gz | mysql -u root -p nombre_base
```

---

## Recomendaciones antes de reinstalar el sistema

1. Ejecutar el backup completo.
2. Verificar que los archivos `.gz` existan y tengan tamaño coherente.
3. Copiar el directorio de backups a un medio externo.

Ejemplo para empaquetar todos los backups:

```bash
tar -czf mariadb_backups.tar.gz /home/sal/backups/mariadb
```

---

## Posibles Mejoras Futuras

* Rotación automática de backups
* Logging estructurado
* Soporte para ejecución con cron
* Uso de archivo `.my.cnf` para credenciales
* Backup incremental
* Envío automático a servidor remoto o almacenamiento en la nube

---

## Disclaimer

Este script realiza backups completos por base de datos. No reemplaza estrategias profesionales de alta disponibilidad, replicación o backups con binlogs en entornos críticos.

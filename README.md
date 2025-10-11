# Simulador de Sistema de Archivos FAT

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)

## Descripción

Este proyecto es un **simulador educativo de un sistema de archivos basado en FAT (File Allocation Table)**, desarrollado en Python como parte de un ejercicio académico de la Facultad de Ingeniería (Segundo Semestre, Septiembre 2025). El simulador replica los mecanismos básicos de manejo de archivos en un sistema FAT, permitiendo operaciones como crear, listar, abrir, modificar, eliminar y recuperar archivos.

A nivel lógico, cada archivo se representa mediante una tabla FAT serializada en JSON, que incluye metadatos como nombre, ruta de datos inicial, estado de papelera de reciclaje, cantidad de caracteres, fechas (creación, modificación, eliminación), propietario (owner) y permisos (lectura/escritura). Los datos "físicos" se segmentan en bloques de máximo 20 caracteres, enlazados en una cadena (simulando clústeres de FAT), y almacenados en archivos JSON separados.

El sistema incluye gestión de permisos: solo el owner puede asignar/revocar permisos, y se valida el acceso antes de leer o modificar archivos. La eliminación mueve archivos a una "papelera virtual" sin borrar datos físicos, permitiendo recuperación.

Este simulador es ideal para entender conceptos de sistemas de archivos, segmentación de datos y control de acceso, sin requerir hardware real o sistemas operativos complejos.

## Características Principales

- **Creación de Archivos**: Solicita nombre y contenido, segmenta en bloques de 20 caracteres y crea entradas en la FAT.
- **Listado de Archivos**: Muestra archivos activos (excluyendo eliminados).
- **Papelera de Reciclaje**: Lista archivos eliminados y permite recuperación (solo por el owner).
- **Apertura de Archivos**: Muestra metadatos y concatena el contenido de todos los bloques (respetando permisos de lectura).
- **Modificación de Archivos**: Lee contenido actual, solicita nuevo contenido, actualiza bloques y metadatos (respetando permisos de escritura).
- **Eliminación**: Marca como eliminado en FAT (mueve a papelera) sin borrar bloques físicos.
- **Gestión de Permisos**: El owner puede agregar/revocar permisos de lectura o escritura a otros usuarios.
- **Persistencia**: Todos los datos se guardan en archivos JSON en un directorio simulado (`filesystem/`), permitiendo sesiones múltiples.
- **Validación de Permisos**: Usuario actual (ingresado al inicio) se usa para verificar accesos.

## Requisitos

- **Python**: Versión 3.6 o superior (usa módulos estándar: `json`, `os`, `datetime`, `typing`).
- No se requieren dependencias externas (biblioteca estándar de Python).
- Sistema operativo: Compatible con Windows, macOS o Linux.

## Contribución

¡Contribuciones son bienvenidas! Si quieres mejorar el simulador (e.g., agregar soporte multiusuario avanzado, límites de disco, o visualización gráfica):

1. Fork el repositorio.
2. Crea una rama: `git checkout -b feature/nueva-funcion`.
3. Commit cambios: `git commit -m "Agrega nueva función"`.
4. Push a la rama: `git push origin feature/nueva-funcion`.
5. Abre un Pull Request.

Por favor, mantén el código educativo y enfocado en conceptos de FAT.

## Créditos y Contacto

- **Autor**: Diego Ovalle - Di3g0_01 – Basado en contenido de clase sobre Manejo e Implementación de Archivos y FAT.
- **Fecha**: Octubre 2025.
- Para dudas o sugerencias: Ovallediego.p@gmail.com o abre un issue en GitHub.

¡Gracias por usar este simulador! Si es para fines educativos, ¡espero que te ayude a entender mejor los sistemas de archivos. 🚀

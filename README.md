## 🛡️ Auditoría y Monitoreo de Eventos Críticos en Amazon S3

### 📝 Descripción del Proyecto:
Arquitectura de auditoría y monitoreo basada en eventos para Amazon S3 utilizando AWS CloudTrail, CloudWatch y SNS, capaz de detectar operaciones críticas sobre objetos sensibles y generar alertas automáticas.

---

### 🏗️ Arquitectura

![alt text](assets/ArquitecturaProyecto-ServiciosAWS.png)

---

### 🎯 Objetivo

Detectar automáticamente operaciones sensibles realizadas sobre objetos dentro de un bucket Amazon S3 y notificar eventos críticos hacia los responsables de seguridad o infraestructura.

---

### 🧠 Caso de Uso

El proyecto simula un escenario donde una empresa almacena respaldos de bases de datos en un bucket S3 crítico.  
Cada vez que un objeto es descargado, eliminado o cargado, el sistema genera eventos de auditoría y alertas automáticas.

---

### ☁️ Servicios AWS Utilizados

- Amazon S3
- AWS CloudTrail
- Amazon CloudWatch
- Amazon SNS
- IAM

---
### 🔍 Eventos Monitoreados

- PutObject
- DeleteObject

---

### 🚀 Funcionalidades

- Auditoría Object-Level sobre Amazon S3
- Registro de Data Events mediante CloudTrail
- Centralización de logs en CloudWatch
- Creación de métricas automáticas mediante Metric Filters
- Alarmas automáticas
- Notificaciones vía SNS

---

### 🚀 Próximas mejoras del proyecto

Este proyecto representa una primera arquitectura de monitoreo y auditoría sobre Amazon S3 utilizando CloudTrail, CloudWatch y SNS.

Actualmente, la solución permite:
- Registrar eventos sobre objetos dentro de un bucket sensible.
- Supervisar actividades mediante CloudWatch Logs.
- Detectar patrones específicos utilizando Metric Filters.
- Generar alarmas automáticas y notificaciones vía SNS.

Sin embargo, como evolución natural del proyecto, plantéo una segunda versión enfocada en arquitecturas event-driven y monitoreo avanzado, incorporando servicios como:

- Amazon EventBridge
- AWS Lambda

Con ello, se buscará:
- Procesar eventos en tiempo real.
- Obtener detalles específicos de cada acción realizada.
- Identificar usuarios, objetos e IPs involucradas.
- Personalizar completamente las alertas enviadas.
- Construir una arquitectura de auditoría mucho más cercana a escenarios enterprise reales.

---

### 🧑‍💻 Sobre Mí

Brayan Neciosup Bolaños - Data & Cloud Engineer Jr.

Actualmente explorando **Infraestructura como Código** y su potencial para el despliegue de recursos en AWS.

📫 **Contacto**  
- 🌐 Portafolio: [Portafolio_WIX](https://bryanneciosup626.wixsite.com/brayandataanalitics)  
- 💼 LinkedIn: [linkedin.com/in/brayanneciosup](https://www.linkedin.com/in/brayan-rafael-neciosup-bola%C3%B1os-407a59246/)  
- 🧠 GitHub: [github.com/brayanneciosup](https://github.com/BrayanR03)  
- ✉️ Email: [bryanneciosup626@gmail.com](bryanneciosup626@gmail.com)

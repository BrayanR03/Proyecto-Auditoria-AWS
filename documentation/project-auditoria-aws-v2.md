## 🛡️ Auditoría y Monitoreo de Eventos Críticos en Amazon S3 mediante CloudTrail, EventBridge, Lambda y SNS

### 📖 Introducción

Este proyecto tiene como objetivo construir una arquitectura de auditoría y monitoreo para actividades críticas realizadas sobre objetos almacenados en Amazon S3.

La primera versión de la solución fue implementada utilizando Amazon S3, AWS CloudTrail, Amazon CloudWatch y Amazon SNS, permitiendo registrar eventos, generar métricas y enviar alertas automáticas cuando se detectaban operaciones sobre un bucket considerado sensible.

```yml
Amazon S3
    ↓
AWS CloudTrail
    ↓
Amazon CloudWatch
    ↓
Amazon SNS
```

Si bien esta arquitectura cumplía correctamente con el monitoreo basado en métricas, durante las pruebas se identificaron diversas limitaciones para escenarios de auditoría y seguridad:

* Las alertas generadas por CloudWatch estaban enfocadas en métricas y umbrales.
* Las notificaciones no incluían información detallada sobre el recurso afectado.
* No era posible identificar rápidamente qué objeto había sido modificado o eliminado.
* Las alertas carecían de contexto suficiente para procesos de investigación.
* Existía una separación entre la notificación recibida y la evidencia almacenada por CloudTrail.

En procesos de auditoría resulta fundamental disponer de información más específica, como:

* Nombre del bucket afectado.
* Nombre del objeto involucrado.
* Tipo de operación realizada.
* Dirección IP de origen.
* Usuario responsable de la acción.
* Evidencia que permita rastrear el evento dentro de los registros de auditoría.

Debido a ello, se decidió evolucionar la arquitectura hacia un enfoque orientado a eventos, incorporando `Amazon EventBridge` y `AWS Lambda` como componentes principales para el procesamiento de eventos generados por Amazon S3.

La nueva arquitectura permite reaccionar directamente ante eventos de creación y eliminación de objetos, enriqueciendo las notificaciones enviadas a los responsables de seguridad e incluyendo información relevante para la supervisión operativa.

Durante esta evolución también se identificaron comportamientos particulares relacionados con las operaciones de eliminación de objetos. Algunas acciones realizadas desde la consola de AWS eran registradas como `DeleteObjects` en lugar de `DeleteObject`, lo que inicialmente dificultó identificar correctamente los recursos afectados dentro del flujo de monitoreo.

A partir de las pruebas realizadas se logró comprender el comportamiento de estos eventos y adaptar la arquitectura para garantizar una correcta identificación de las operaciones ejecutadas sobre el bucket monitoreado.

La arquitectura final implementada quedó definida de la siguiente manera:

```yml
Amazon S3
    ├── AWS CloudTrail
    │
    └── Amazon EventBridge
            ↓
        AWS Lambda
            ↓
        Amazon SNS
```

Esta arquitectura permite combinar dos capacidades fundamentales:

* **Auditoría**, mediante AWS CloudTrail y sus registros históricos.
* **Monitoreo basado en eventos**, mediante EventBridge, Lambda y SNS.

Uno de los hallazgos más importantes del proyecto fue la posibilidad de correlacionar las notificaciones recibidas por correo electrónico con los registros de auditoría almacenados en CloudTrail mediante el campo `request-id`.

Gracias a esta correlación, cada alerta enviada a los stakeholders puede asociarse posteriormente con el evento exacto registrado por CloudTrail, permitiendo rastrear de forma precisa quién ejecutó la acción, cuándo ocurrió y sobre qué recurso fue realizada.

Como resultado, la solución no solo permite detectar actividades sensibles sobre Amazon S3 en tiempo real, sino también mantener la trazabilidad necesaria para procesos de auditoría, cumplimiento normativo e investigación de incidentes.

En las siguientes secciones se documentará paso a paso la implementación de la arquitectura, los problemas encontrados durante el desarrollo, las decisiones tomadas para su evolución y las soluciones aplicadas para alcanzar el diseño final.

---

## 🔄 Actualización End-to-End del Proyecto

### 📦 DESACOPLMIENTO DE AMAZON CLOUDWATCH

#### 1️⃣ ELIMINAR ALARMAS

* Accederemos a: 

    `CloudWatch → Alarms → All alarms`
* Eliminaremos la alarma:
    
     `sns-s3-security-alerts`

#### 2️⃣ ELIMINAR METRIC FILTERS

* Accederemos a: 

    `CloudWatch → Log Management → aws-cloudtrail-logs-xxxxx → Metric filters`

* Eliminaremos:

    `AuditoriaS3Events`

#### ⚠️ IMPORTANTE: 
* No eliminar el LOG GROUP
* Las métricas expiran
* Es opcional eliminar las configuraciones en Amazon SNS (En mi caso lo mantendré)

---

### ⌨️ ACOPLAMIENTO DE AWS LAMBDA

El siguiente paso consiste en crear una función **AWS Lambda**, la cual será la encargada de procesar los eventos generados por Amazon S3 y construir notificaciones más detalladas para los responsables de auditoría y monitoreo.

#### 🛠️ Creación de la función

Desde el servicio **AWS Lambda**, creamos una nueva función con la siguiente configuración:

* **Nombre:** `lambda-s3-compliance-notification`
* **Runtime:** `Python 3.14`

Para este proyecto permitiremos que AWS genere automáticamente el rol IAM asociado a la función, debido que implementa correctamente el **principio de mínimo privilegio** para la ejecución inicial.

Una vez completada la configuración, damos click en `Create Function`

---

#### 💻 Implementación del código

Nos dirigimos al apartado **Code** y reemplazamos el contenido generado por defecto con el archivo: [lambda-function.py](https://github.com/BrayanR03/Proyecto-Auditoria-AWS/tree/main/assets/lambda_function.py)

Antes de desplegar la función, debemos actualizar la variable:
**TOPIC_ARN**, reemplazando su valor por el **ARN del tópico SNS** creado anteriormente.

En mi caso: `arn:aws:sns:us-east-2:747554529824:sns-s3-security-alerts`

Finalmente, desplegamos los cambios mediante:
`Deploy (Ctrl + Shift + U)`


Con ello, la función Lambda quedará lista para ser utilizada posteriormente como destino de Amazon EventBridge.

---

### 📩 ACOPLAMIENTO DE AMAZON EVENTBRIDGE

#### 1️⃣ Habilitar eventos desde Amazon S3

Inicialmente, regresamos al bucket que será auditado:
`bucket-brayan-project-compliance`

Y realizamos la siguiente configuración:

```yml
Properties → Amazon EventBridge → Edit → 
Send notifications to Amazon EventBridge for 
all events in this bucket → On → Save changes
```

Con esta configuración, Amazon S3 enviará los eventos generados dentro del bucket hacia el **bus por defecto de Amazon EventBridge**, permitiendo su posterior procesamiento y filtrado.

---

#### 2️⃣ Creación de la regla en EventBridge

Una vez habilitada la integración, creamos una regla para filtrar únicamente los eventos que nos interesan:

```yml
Rules
    → Select Event Bus
        → default
            → Event Pattern Rules
                → Create Rule
```

Configuramos los siguientes valores:

* **Name:** `rule-s3-object-events`
* **Event Bus:** `default`
* ✔️ **Enable the rule on the selected event bus**

Continuamos con **Next** y configuramos:

**Event Source**

* AWS events or EventBridge partner events

**Custom Pattern (JSON Editor)**

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created", "Object Deleted"],
  "detail": {
    "bucket": {
      "name": ["bucket-brayan-project-compliance"]
    }
  }
}
```

Este patrón permitirá capturar únicamente eventos de creación y eliminación de objetos dentro del bucket auditado. Debido a que el bucket de S3, envía un JSON con diferentes valores y uno de ellos es el de **detail-type** de la regla creada en EventBridge.

---

#### 🎯 Configuración del Target

Seleccionamos como destino la función Lambda creada anteriormente:

* **Target Type:** AWS Service
* **Select a Target:** Lambda Function
* **Target Location:** Target in this account
* **Function:** `lambda-s3-compliance-notification`

**Permissions**

* ✔️ Use execution role (recommended)
* Create a new role for this specific resource:             `Amazon_EventBridge_Invoke_Lambda_Compliance`

Para este proyecto permitiremos que AWS genere automáticamente el rol de ejecución, aplicando el **principio de mínimo privilegio** para la invocación de la función Lambda.

Finalmente, daremos click en **Next** → **Next** → **Create Rule**

---

#### 🔄 Flujo final de la arquitectura

Una vez creada la regla, el flujo de eventos quedará definido de la siguiente manera:

```yml
Amazon S3
    ↓
Amazon EventBridge
    ↓
Rule: rule-s3-object-events
    ↓
AWS Lambda
    ↓
Amazon SNS
    ↓
Email de Notificación
```

Cuando se produzca una operación de **PutObject** o **DeleteObject** dentro del bucket monitoreado, EventBridge recibirá el evento, lo filtrará mediante la regla creada y lo enviará a la función Lambda. Posteriormente, Lambda procesará la información relevante del evento y publicará una notificación en SNS para su distribución por correo electrónico.







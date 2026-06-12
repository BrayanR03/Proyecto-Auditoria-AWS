# 🛡️ Auditoría y Monitoreo de Eventos Críticos en Amazon S3 mediante CloudTrail, CloudWatch y SNS

Inicialmente, este proyecto parecía una implementación sencilla basada únicamente en registrar eventos sobre un bucket S3.

Sin embargo, conforme avanzaba la investigación y configuración de los servicios involucrados, quedó claro que AWS ofrece un ecosistema mucho más profundo en cuanto: auditoría, observabilidad y monitoreo automatizado de eventos críticos dentro de la nube.

En entornos empresariales, los buckets S3 suelen almacenar información altamente sensible:

* respaldos de bases de datos,
* archivos financieros,
* datasets críticos,
* información analítica,
* documentación confidencial,
* entre otros activos importantes.

Por ello, resulta fundamental implementar mecanismos que permitan:

* auditar accesos,
* supervisar operaciones sobre objetos,
* detectar actividades sensibles,
* y notificar automáticamente a los responsables de seguridad o infraestructura.

Este proyecto busca precisamente construir un pipeline de auditoría y monitoreo sobre Amazon S3, utilizando servicios nativos de AWS para detectar y notificar operaciones realizadas sobre objetos críticos dentro de un bucket sensible.

---

## 🎯 Objetivo del Proyecto

Diseñar una arquitectura de auditoría y monitoreo basada en eventos para Amazon S3, capaz de detectar operaciones críticas realizadas sobre objetos dentro de un bucket sensible y generar alertas automáticas hacia los stakeholders responsables de la supervisión y seguridad de la información.

Para ello, se utilizarán servicios como:

* AWS CloudTrail,
* Amazon CloudWatch,
* y Amazon SNS,

permitiendo registrar, monitorear y reaccionar ante operaciones como:

* cargas de archivos (PutObject),
* y eliminaciones (DeleteObject).

El enfoque principal del proyecto se centra en construir un mecanismo de observabilidad y notificación automatizada sobre actividades sensibles realizadas dentro de Amazon S3.

---

## 🧠 Casuística del Proyecto

Imaginemos un escenario donde una empresa almacena respaldos de bases de datos dentro de un bucket Amazon S3 considerado crítico para la operación del negocio.

Si bien es normal que los sistemas suban periódicamente nuevos respaldos hacia dicho bucket, no resulta habitual que múltiples usuarios descarguen o eliminen estos archivos constantemente.

Bajo este contexto, el equipo encargado de la seguridad cloud, infraestructura o administración de bases de datos necesita contar con mecanismos que permitan:

* detectar accesos sensibles,
* supervisar operaciones sobre objetos críticos,
* y recibir alertas automáticas cuando ocurran eventos potencialmente importantes.

Por ello, este proyecto implementa una arquitectura de monitoreo basada en eventos que permite identificar actividades como:

* eliminación de archivos,
* o cargas inesperadas de objetos,

generando notificaciones automáticas hacia los responsables correspondientes mediante Amazon SNS.

---

## 🔄 Implementación End-to-End del Proyecto

### 📦 CONFIGURACIÓN S3

Para la implementación del proyecto, será necesario crear 2 buckets en Amazon S3:

---

#### 🪣 Bucket A — Bucket Principal Auditado

Este bucket permitirá almacenar la información sensible que será auditada mediante el Trail configurado en pasos posteriores.

El objetivo será registrar:

* qué acciones fueron realizadas,
* qué usuarios las ejecutaron,
* y sobre qué recursos se realizaron dichas acciones.

Esto resulta importante en escenarios relacionados sobre auditoría. Este primer bucket tendrá por nombre:
`bucket-brayan-project-auditoria`

---

#### 🪣 Bucket B — Bucket de Logs del Trail

Este bucket permitirá almacenar cada evento registrado sobre el bucket principal auditado anteriormente.

Aquí se almacenarán los logs generados por AWS CloudTrail relacionados a las operaciones realizadas sobre los objetos del bucket principal. Este segundo bucket tendrá por nombre:
`bucket-brayan-project-auditoria-trail`

---

### 📖 CONFIGURACIÓN CLOUDTRAIL

Para tener una idea general, AWS CloudTrail es un servicio que permite registrar eventos realizados a nivel de cuenta dentro de AWS.

Toda acción que un usuario o servicio realice sobre un recurso específico puede quedar registrada, permitiendo posteriormente realizar tareas de:

* auditoría,
* supervisión
* y monitoreo

---

#### 🛤️ TRAIL

El componente principal será el **Trail**, el cual permitirá registrar eventos que ocurran sobre diversos recursos y servicios dentro de AWS.

En este caso, el Trail permitirá registrar las acciones realizadas por usuarios sobre el bucket S3 auditado:
`bucket-project-auditoria-brayan`

---

##### ⚙️ CONFIGURACIÓN DEL TRAIL:
Crearemos un Trail desde CloudTrail y lo alinearemos al bucket creado anteriormente para el registro de eventos.

* 📝 General Details (Detalles generales)

    | Configuración                    | Valor                                    |
    | -------------------------------- | ---------------------------------------- |
    | Trail name                 | `trail-s3-project-auditoria`            |
    | Storage Location | `bucket-project-auditoria-brayan-trail` |

    > En **Storage Location**, seleccionamos **Use existing S3 bucket** porque previamente creamos el bucket donde se registrarán los eventos del bucket auditado. 

---

* Asimismo, seguiremos aplicando las siguientes configuraciones:

    | Configuración               | Acción                          |
    | --------------------------- | ------------------------------- |
    | **Log file SSE-KMS encryption** | No marcar (mantendremos SSE-S3) |
    | **Log file validation**         | Marcar (Enabled ✔️)                          |

    >La opción **Log file validation** permitirá detectar posibles alteraciones o manipulaciones sobre los logs generados.

---

* **SNS Notification Delivery**: Para esta parte de la configuración **no habilitaremos** SNS Notification Delivery.

---

* 📊 CloudWatch Logs: **Habilitaremos CloudWatch Logs** para poder visualizar el estado y funcionamiento del Trail mediante logs centralizados.

    | Configuración        | Valor                                       |
    | -------------------- | ------------------------------------------- |
    | CloudWatch Logs      | Habilitado (Enabled ✔️)                            |
    | Nombre del Log Group | `AWS asigna el nombre del log group` |

    En mi caso, el nombre del log group fue: `aws-cloudtrail-logs-747554529824-fb75b47d`

---

* 👤 IAM Role: Será necesario **crear un nuevo rol IAM o utilizar uno existente** para permitir la integración entre CloudTrail y CloudWatch Logs.

    | Configuración  | Valor                         |
    | -------------- | ----------------------------- |
    | Nombre del Rol | `CloudTrailRol-S3-Auditoria` |

    La política que generó AWS y es utilizada para este rol se encuentra en:
    [politica_iam_auditoria.json](https://github.com/BrayanR03/Proyecto-Auditoria-AWS/tree/main/assets/politica_iam_auditoria.json)

---

* 🔍 Configuración de eventos: Aquí definiremos qué tipos de eventos del bucket S3 serán registrados por el Trail. Y en los events, elegiremos:
    

    *  🛠️ Management Events: Permiten auditar eventos relacionados a infraestructura y configuración AWS. Por ejemplo:

        * cambios IAM,
        * políticas,
        * configuración de S3,
        * modificaciones sobre CloudTrail.
    
        En este caso, al seleccionar este tipo de evento, nos brindará una sección para elegir la **API activity** y aquí marcaremos:

        * Read Events → habilitado
        * Write Events → habilitado


    * 📦 Data Events: Permiten auditar acciones realizadas directamente sobre los objetos almacenados en S3. En este caso al seleccionar este tipo de evento, también nos brindará una sección para elegir las operaciones realizadas sobre cada objeto del bucket:

        * `PutObject`
        * `DeleteObject`

        Además, CloudTrail permite dos tipos de selectores sobre la elección de **Data Events**:
        * Basic event selectors,
        * Advanced event selectoes.

        Para este proyecto utilizaremos:

        ```yaml
        Advanced Event Selectors (Debido a un control granular sobre el bucket a auditar)
        ```

        Asimismo, se realizarán las siguientes configuraciones sobre este selector:

        | Configuración         | Valor  |
        | --------------------- | ------ |
        | Resource type         | S3     |
        | Log selector template | Custom |

        Y en **Advanced event selectors**:

        | Field         | Operator   | Value                                            |
        | ------------- | ---------- | ------------------------------------------------ |
        | resources.ARN | startsWith | `arn:aws:s3:::bucket-project-auditoria-brayan/` |

---

* 📊 Configure Event Aggregation

    - No habilitaremos esta opción.
    - Aunque, si bien permite agrupar eventos y generar enfoques orientados a organizaciones, para este proyecto no será necesario.

* Una vez finalizada la configuración, procederemos a crear el Trail (**Damos click en Next y Create**).

---

### 📦 HABILITAR DATA EVENTS DESDE S3

Posteriormente, regresaremos al bucket que será auditado:

```yml
bucket-project-auditoria-brayan
```

Y realizaremos los siguiente:

```yml
Accederemos a:

Properties → AWS CloudTrail data events → AWS CloudTrail → Configure data event logging
→ CloudTrail destination → Seleccionar ARN del Trail creado previamente
→ Enable data events
```


* Una vez habilitado el Trail y los Data Events, ya podremos subir archivos al bucket S3 y observar cómo los eventos comienzan a registrarse dentro del bucket destinado para los logs del Trail.

* Es importante considerar que los registros pueden tardar algunos minutos en aparecer y no siempre se visualizarán de manera instantánea.

---

### 📊 CONFIGURACIÓN CLOUDWATCH

Ahora vamos a verificar que el Trail envíe correctamente los eventos hacia CloudWatch Logs. Es importante tener en cuenta que CloudTrail genera sus logs y los envía en paralelo:

* Al bucket S3 destinado para almacenar los registros (`bucket-brayan-project-auditoria-trail`),
* y al Log Group de CloudWatch configurado durante la creación del Trail.

---

#### 🔍 VERIFICACIÓN DE LOGS EN CLOUDWATCH

Para verificar el correcto registro de eventos en CloudWatch:

* Accedemos al Log Group del Trail creado anteriormente.

En mi caso:

```yml
aws-cloudtrail-logs-747554529824-fb75b47d
```

---

#### 📑 Log Streams

* El Log Group se compone principalmente de un conjunto de Log Streams.

* Aquí es donde CloudWatch separa y organiza los logs generados por las acciones realizadas sobre el bucket S3.

* Sin embargo, revisar manualmente cada Log Stream puede resultar poco práctico debido a la cantidad de eventos generados.

---

#### 🔎 CLOUDWATCH LOGS INSIGHTS

Para verificar correctamente si el registro del objeto subido al bucket S3 funcionó, utilizaremos el apartado de CloudWatch denominado:

```yml
Logs Insights
```

Aquí podremos realizar consultas utilizando queries propias de CloudWatch Logs Insights para filtrar y mostrar únicamente la información relevante.

---

##### 📄 QUERY UTILIZADA

```sql
fields @timestamp, eventName, eventCategory, requestParameters.bucketName, requestParameters.key
| filter requestParameters.bucketName = "bucket-brayan-project-auditoria"
| filter eventName in ["PutObject","DeleteObject"]
| sort @timestamp desc
| limit 20
```


La query mostrará:

* los logs ordenados del más reciente al más antiguo,
* limitando el resultado a 20 registros,
* y filtrando únicamente eventos relacionados al bucket auditado.

Aquí ya podremos verificar si el nombre del objeto subido a S3 aparece correctamente dentro de los logs.

En mi caso, el objeto sí aparece, confirmando que CloudWatch está recibiendo correctamente los eventos enviados por CloudTrail.

---

#### 📈 CONFIGURACIÓN DE METRIC FILTER

Ahora configuraremos un Metric Filter, el cuál analizará continuamente todos los eventos generados dentro del Log Group y buscará coincidencias con un patrón específico.

* **DEFINE PATTERN**

    En este caso, el patrón común que comunmente se utilizaria:

    ```yml
    PutObject
    ```

    Buscaría todos los logs de carga de objetos al bucket, pero, en las casuísticas de la vida real, querremos saber quienes eliminan objetos también. Asi que, trabajaremos con esas 2 acciones de s3: `PutObject`,`DeleteObject`.

    Nos dirigiremos a **Metric filters** dentro del log group y le daremos en **Create metric filter**

    | Configuración         | Valor  |
    | --------------------- | ------ |
    | Filter pattern        |  Verificar ⬇️   |
    ```yml
    { ($.eventName = PutObject) || ($.eventName = DeleteObject) }
    ```

    La opción:

    ```yml
    Select log data to test
    ```

    solo permitirá validar manualmente si el patrón detecta correctamente eventos existentes antes de crear la métrica definitiva.

    En este caso, al elegir cualquier **log group**
    permitirá verificar que el pattern ingresado anteriormente funciona. 
    
    Si en caso, aparecen resultados en **Results** AL DARLE CLICK EN **Test pattern** nuestro pattern funciona correctamente. Y daremos click en **Next**

    Sino, debemos verificar que nuestro pattern esta correctamente definido o en nuestros **logs groups** existen registros previos.


* **ASSIGN METRIC**:

    | Configuración         | Valor  |
    | --------------------- | ------ |
    | Filter name        |  `Filter-Auditoria-S3` |
    | Filter pattern     | `Patron definido anteriormente` |
    | Metric Namespace | `S3Auditoria`    |
    | Metric Name      | `AuditoriaS3Events` |
    | Metric Value     | `1`               |
    | Default Value    | `0`               |


📌 Explicación

* **Filter name:** nombre del filtro 
* **Filter pattern:** pattern definido anteriormente  
* **Metric Namespace:** agrupará lógicamente las métricas relacionadas al proyecto.
* **Metric Name:** nombre de la métrica generada.
* **Metric Value:** cada vez que un log haga match con el Metric Filter, aumentará el valor de la métrica.
* **Default Value:** inicializa la métrica en 0.

---
* 📍 Dimensions

    CloudWatch también permite utilizar Dimensions como:

    * `@aws.account`
    * `@aws.region`

Sin embargo, estas características están más orientadas a escenarios multi-cuenta o multi-región, por lo que no serán necesarias para este proyecto.

Ahora damos click en **Next** y luego **Create metric filter**

---

#### 🚨 CREACIÓN DE ALARMA EN CLOUDWATCH

Posteriormente, nos dirigiremos al apartado:

```yml
CloudWatch → Alarms → Create alarm → Select metric
```

Las alarmas en CloudWatch permitirán definir umbrales basados en la métrica creada anteriormente.

La alarma evaluará continuamente la métrica y verificará si se encuentra dentro o fuera del umbral definido.

---

Seleccionaremos:

* el Namespace (`S3Auditoria`), luego **Metrics with no dimensions**,
* y la métrica (`AuditoriaS3Events`). Asimismo, daremos click **Select metric**,

Posteriormente configuraremos:

| Configuración | Valor      |
| ------------- | ---------- |
| Statistic     | `Sum`      |
| Period        | `1 minute` |

---
📌 Explicación

* **Sum:** permitirá sumar cada evento tipo: `PutObject` y `DeleteObject`.
* **1 minute:** permitirá que la alarma evalúe continuamente la métrica cada minuto.

---

Posteriormente:

| Configuración  | Valor           |
| -------------- | --------------- |
| Threshold Type | `Static`        |
| Condition      | `Greater/Equal` |
| Than           | `1`             |

Además, en **Additioal configuration**:

| Configuración  | Valor           |
| -------------- | --------------- |
| Datapoints to alarm  | `1` out of `1`        |
| Missing data treatment      | `Treat missing data as good (not breaching threshold)` |


---
📌 Resultado

En pocas palabras:

Si los eventos `PutObject`,`DeleteObject` superan o son iguales a `1`, la alarma cambiará de estado y posteriormente podrá generar una notificación.

Asimismo, la configuración **Missing data treatment** permite definir cómo CloudWatch interpretará los períodos donde no existan datos o eventos asociados a la métrica.

Si se configura incorrectamente, los datos faltantes podrían interpretarse como eventos que superan el umbral, manteniendo la alarma en estado **ALARM** y generando notificaciones repetidas.

Por ello, se configura esta opción como `Treat missing data as good (not breaching threshold)`, permitiendo que, cuando no existan nuevos eventos sobre el bucket S3, la alarma vuelva automáticamente al estado OK y deje de enviar alertas.

Ahora bien, antes de seguir creando la alarma configuremos la notificación ...

---

### 📢 CONFIGURACIÓN DE SNS

Antes de finalizar la creación de nuestra alarma en CloudWatch, será necesario configurar un Topic dentro del servicio **Amazon Simple Notification Service (SNS)**.

SNS forma parte de los servicios orientados a eventos (*Event-Driven*) dentro de AWS. Su funcionamiento se basa en una arquitectura Publisher / Subscriber, donde:

- Un **Publisher** genera y envía mensajes.
- Un **Topic** actúa como canal centralizado de mensajería y distribución.
- Uno o varios **Subscribers** reciben dichos mensajes a través de diferentes protocolos.

Entre los protocolos soportados por SNS se encuentran:

- Email
- SMS
- HTTP / HTTPS
- AWS Lambda
- Amazon SQS

En este proyecto, CloudWatch actuará como **Publisher**, enviando alertas al Topic SNS cuando se detecten eventos relevantes sobre el bucket auditado.

---

#### 📨 CREACIÓN DEL TOPIC (Amazon SNS → Topics)

En el servicio de **SNS**, crearemos el Topic que actuará como canal de distribución de alertas.

| Configuración | Valor |
|---|---|
| Tipo | `Standard` |
| Nombre | `sns-s3-security-alerts` |

* ¿Por qué Standard?

    Elegiremos un Topic de tipo **Standard** debido a que las alertas no requieren un orden estricto de entrega, ofreciendo mayor flexibilidad para este escenario de monitoreo. Asimismo, daremos click en: `Create Topic`

#### 👥 CREACIÓN DE SUBSCRIPTIONS (Amazon SNS → Subscriptions)

Posteriormente, crearemos los **Subscribers** que recibirán las alertas enviadas por el Topic.

| Configuración | Valor |
|---|---|
| Topic ARN | ARN del Topic creado anteriormente |
| Protocol | Email |
| Endpoint | mi_correo@gmail.com |

Una vez creada la Subscription:

- SNS enviará automáticamente un correo de confirmación.
- Será necesario abrir dicho correo y confirmar la suscripción.
- Después de la confirmación, el Subscriber quedará habilitado para recibir notificaciones. Revisar imagen: [Confirmacion-SNS](https://github.com/BrayanR03/Proyecto-Auditoria-AWS/tree/main/assets/ConfirmacionSNS.png) 

---

### 🚨 RE-CONFIGURACIÓN DE LA ALARMA EN CLOUDWATCH

Con el Topic SNS ya configurado, regresaremos a la creación de la alarma en CloudWatch.

---

#### ⚙️ CONFIGURACIÓN DE LA ALARMA

En **Alarm state trigger**, elegiremos: **In alarm** y seleccionaremos el Topic creado anteriormente:

```yml
sns-s3-security-alerts
```

---
Luego, en los detalles de la alarma:

| Configuración | Valor |
|---|---|
| Alarm Name | `alarm-s3-auditoria-detection` |
| Description | Detecta operaciones PutObject y DeleteObject dentro del bucket auditado y genera alertas automáticas vía SNS. |

Una vez configurada:

```yml
Next → Create Alarm
```

---

#### 📊 ESTADO INICIAL DE LA ALARMA

Al finalizar su creación, la alarma normalmente mostrará el estado:

```yml
Insufficient Data
```

Esto ocurre porque aún no existen eventos suficientes para que CloudWatch pueda evaluar la métrica asociada.

En este caso, todavía no se ha producido ningún evento `PutObject`,`DeleteObject` que permita activar la evaluación de la alarma.

---

#### 🧪 VALIDACIÓN

Para comprobar el funcionamiento completo de la arquitectura:

1. Subimos un nuevo archivo al bucket auditado.
2. CloudTrail registra el evento.
3. CloudWatch recibe el log.
4. El Metric Filter detecta el evento `PutObject`.
5. La métrica incrementa su valor.
6. La alarma cambia de estado.
7. SNS distribuye la notificación al correo configurado.

Si todo funciona correctamente, recibiremos un correo notificando que se ha detectado una operación sobre el bucket auditado. Y asi, podemos realizar lo mismo eliminando el objeto.

---

### ✅ FLUJO FINAL DE LA SOLUCIÓN

```plaintext
Amazon S3
      │
      ▼
AWS CloudTrail
      │
      ▼
CloudWatch Logs
      │
      ▼
Metric Filter
      │
      ▼
CloudWatch Alarm
      │
      ▼
SNS Topic
      │
      ▼
Email Notification
```

Este flujo completa la arquitectura de auditoría y monitoreo para eventos críticos realizados sobre objetos dentro del bucket S3 auditado.

---

### 🚀 Conclusiones y evolución del Proyecto

Este proyecto permitió construir una arquitectura de monitoreo y auditoría sobre Amazon S3 utilizando servicios nativos de AWS como:

* ☁️ AWS CloudTrail
* 📊 Amazon CloudWatch
* 📩 Amazon SNS

El objetivo principal fue supervisar y registrar actividades realizadas sobre un bucket sensible dentro de AWS, permitiendo detectar acciones importantes como:

* 📤 Subida de objetos (`PutObject`)
* 🗑️ Eliminación de objetos (`DeleteObject`)

Gracias al uso de **Object-Level Logging**, fue posible registrar eventos a nivel de objetos dentro del bucket, comprendiendo cómo AWS genera trazabilidad y auditoría sobre recursos críticos en la nube.

---

### 🧠 Puntos importantes en el desarrollo 
A lo largo del desarrollo del proyecto, se reforzaron conceptos importantes relacionados con:

* 🧾 Data Events y Management Events
* 🔥 Object-Level Logging
* 📂 CloudTrail Trails
* 📊 CloudWatch Logs
* 🔎 Logs Insights
* 📈 Metric Filters
* 🚨 Alarmas en CloudWatch
* 📩 Arquitecturas de notificación mediante SNS
* 👀 Observabilidad y monitoreo en AWS

Además, el proyecto permitió comprender el flujo completo de auditoría dentro de AWS:

```yml
S3
↓
CloudTrail
↓
CloudWatch Logs
↓
Metric Filters
↓
CloudWatch Alarm
↓
SNS Notification
```

---

### ⚠️ Limitaciones

Durante las pruebas y validaciones del proyecto, también se identificaron ciertas limitaciones importantes relacionadas con el enfoque basado únicamente en métricas y alarmas de CloudWatch.

Si bien las alarmas permiten detectar cuándo ocurre un evento, las notificaciones generadas no detallan completamente:

* 👤 Qué usuario realizó la acción.
* 📄 Qué objeto fue afectado.
* 🌐 Desde qué origen se ejecutó el evento.
* 🕒 Información enriquecida del evento.

Esto se debe a que CloudWatch Alarm trabaja principalmente evaluando métricas y no procesando directamente el contenido completo de los logs.

---

### 🔥 Evolución futura del Proyecto

Como siguiente evolución, este proyecto servirá como base para implementar una arquitectura mucho más avanzada y orientada a eventos (*Event-Driven Architecture*), incorporando:

* ⚡ Amazon EventBridge
* 🧠 AWS Lambda

La finalidad será:

* 📬 Procesar eventos en tiempo real.
* 🧾 Analizar el JSON completo generado por CloudTrail.
* 📢 Construir alertas enriquecidas y personalizadas.
* 🔐 Mejorar la trazabilidad y supervisión sobre recursos sensibles.
* 🏢 Acercar la arquitectura a escenarios enterprise reales de auditoría y seguridad cloud.

Con esta evolución, el proyecto pasará de un enfoque de monitoreo basado en métricas hacia una solución de auditoría inteligente y automatizada dentro del ecosistema AWS.

---

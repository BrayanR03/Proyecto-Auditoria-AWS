import json
import boto3
from datetime import datetime, timezone

sns = boto3.client('sns')

TOPIC_ARN = "arn:aws:sns:us-east-2:747554529824:sns-s3-security-alerts"

EVENT_LABELS = {
    "Object Created": "Carga de objeto",
    "Object Deleted": "Eliminación de objeto",
}

def format_datetime(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M:%S UTC")
    except Exception:
        return iso_str

def lambda_handler(event, context):
    print(json.dumps(event))

    # ── Extracción de campos ──────────────────────────────────────
    detail      = event.get("detail", {})
    detail_type = event.get("detail-type", "Unknown")

    bucket_name = detail.get("bucket", {}).get("name", "Desconocido")
    object_key  = detail.get("object", {}).get("key", "Desconocido")
    object_size = detail.get("object", {}).get("size", None)
    source_ip   = detail.get("source-ip-address", "Desconocido")
    request_id  = detail.get("request-id", "Desconocido")
    event_time  = format_datetime(event.get("time", "Desconocido"))
    region      = event.get("region", "Desconocido")
    account_id  = event.get("account", "Desconocido")
    action      = EVENT_LABELS.get(detail_type, detail_type)

    size_line = ""
    if object_size is not None:
        size_kb = round(object_size / 1024, 2)
        size_line = f"  Tamaño          : {size_kb} KB\n"

    # ── Cuerpo del correo ─────────────────────────────────────────
    subject = f"[ALERTA S3] {action} detectada — {bucket_name}"

    message = f"""
================================================================
         SISTEMA DE MONITOREO DE SEGURIDAD — AWS S3
================================================================

Se ha detectado actividad en un bucket S3 bajo su cuenta de AWS.
A continuación se detallan los datos del evento registrado:

----------------------------------------------------------------
  DETALLE DEL EVENTO
----------------------------------------------------------------
  Acción            : {action}
  Fecha y hora      : {event_time}
  Región            : {region}
  Cuenta AWS        : {account_id}

----------------------------------------------------------------
  RECURSO AFECTADO
----------------------------------------------------------------
  Bucket            : {bucket_name}
  Objeto            : {object_key}
{size_line}
----------------------------------------------------------------
  ORIGEN DE LA SOLICITUD
----------------------------------------------------------------
  Dirección IP      : {source_ip}

----------------------------------------------------------------
  DATOS DE TRAZABILIDAD (CloudTrail)
----------------------------------------------------------------
  Request ID        : {request_id}

  Este identificador permite correlacionar este correo con el
  registro exacto en los logs de AWS CloudTrail ubicados en:

  AWSLogs/{account_id}/CloudTrail/{region}/

================================================================
  Este mensaje fue generado automáticamente por el sistema de
  alertas de seguridad. No responda a este correo.
================================================================
"""

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=subject,
        Message=message
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Notificación enviada correctamente")
    }
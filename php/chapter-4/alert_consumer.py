import json, smtplib
import pika
#before testing, please use commad:
#1.create user on defalut vhost /:
#rabbitmqctl add_user alert_user alertme

#2.set permission for user:
#rabbitmqctl set_permissions alert_user ".*" ".*",".*"
def send_mail(recipients,subject,message):
    """E-mail generator for received alerts."""
    headers = ("From:%s\r\nTO:\r\n Date:\r\n"+\
                  "Subject:%s\r\n\r\n") % ("alerts@ourcompany.com", subject)
    #if no smtp server set up in localhost, plz comment the following 4 lines for testing.
    smtp_server = smtplib.SMTP()
    smtp_server.connect("mail.ourcompany.com", 25)
    smtp_server.sendmail("alerts@ourcompany.com", recipients, headers + str(message));
    smtp_server.close()

def critical_notify(channel, method, header, body):
    """Sends CRITICAL alerts to administrators via e-mail."""
    EMAIL_RECIPS = ["ops.team@ourcompany.com",]
    message = json.loads(body)

    send_mail(EMAIL_RECIPS, "CRITICAL ALERT", message)

    print("Sent alert via e-mail! Alert Text: %s Recipients: %s" % (str(message), str(EMAIL_RECIPS)))

    channel.basic_ack(delivery_tag=method.delivery_tag)

def rate_limit_notify(channel, method, header,body):
        """Sends the message to the administrators via e-mail."""

        EMAIL_RECIPS = ["api.team@ourcompany.com",]
        message = json.loads(body)
        #(f-asc_10) Transmit e-mail to SMTP Server
        send_mail(EMAIL_RECIPS, "RATE LIMIT ALERT", message)
        print("Sent alert via email! Alert Text: %s Recipients: %s" % (str(message), str(EMAIL_RECIPS)))
        channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    AMQP_SERVER = "localhost"
    AMQP_USER = "alert_user"
    AMQP_PASS = "alertme"
    AMQP_VHOST = "/"
    AMQP_EXCHANGE = "alerts"

    creds_broker = pika.PlainCredentials(AMQP_USER, AMQP_PASS)
    conn_params = pika.ConnectionParameters(AMQP_SERVER, virtual_host=AMQP_VHOST, credentials=creds_broker)
    conn_broker = pika.BlockingConnection(conn_params)
    channel = conn_broker.channel()

    channel.exchange_declare(exchange=AMQP_EXCHANGE, exchange_type="topic", auto_delete=False)

    channel.queue_declare(queue="critical", auto_delete=False)
    channel.queue_bind(queue="critical", exchange="alerts", routing_key="critical.*")

    channel.queue_declare(queue="rate_limit", auto_delete=False)
    channel.queue_bind("rate_limit", exchange="alerts", routing_key="*.rate_limit")

    channel.basic_consume(critical_notify, queue="critical", no_ack=False, consumer_tag="critical")
    channel.basic_consume(rate_limit_notify, queue="rate_limit", no_ack=False, consumer_tag="rate_limit")

    print "Ready for alerts!"
    channel.start_consuming()


import json, pika

from optparse import OptionParser

#usage: alert_producer -r critical.rate_limit -m rate_out_of_limitation
opt_parser = OptionParser()

opt_parser.add_option("-r", "--routing_key", dest="routing_key", help="Routing key for message " +\
                      " (e.g. myalert.im)")

opt_parser.add_option("-m", "--message", dest="message", help="Message text for alert")

args = opt_parser.parse_args()[0]

creds_broker = pika.PlainCredentials("alert_user", "alertme")
conn_params = pika.ConnectionParameters("localhost", virtual_host="/", credentials = creds_broker)
conn_broker = pika.BlockingConnection(conn_params)

channel = conn_broker.channel()

msg = json.dumps(args.message)
msg_props = pika.BasicProperties()
msg_props.content_type = "application/json"
msg_props.durable = False


channel.publish(body=msg, exchange="alerts", properties=msg_props, routing_key=args.routing_key)
print("Sent message %s tagged with routing key '%s' to " % (args.message, args.routing_key))



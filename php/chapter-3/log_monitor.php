<?php
 require_once('../php-amqplib/amqp.inc');
 require_once('../config/config.php');

$conn = new AMQPConnection(HOST, PORT, USER, PASS);
$ch = $conn->channel();

list($errors_queue, ,) = $ch->queue_declare();
list($warnings_queue, ,) = $ch->queue_declare();
list($info_queue, ,) = $ch->queue_declare();

$exchange = 'amq.rabbitmq.trace';
//$exchange = 'amq.rabbitmq.log';


$ch->queue_bind($errors_queue,$exchange,"error");
$ch->queue_bind($warnings,$exchange,"warning");
$ch->queue_bind($info_queue,$exchange,"info");

$error_callback = function($msg){
echo 'error: ', $msg->body, "\n";
$msg->delivery_info['channel']->basic_ack($msg->delivery_info['delivery_tag']);
};
$warning_callback = function($msg){
echo 'warning: ', $msg->body,"\n";
$msg->delivery_inof['channel']->basic_ack($msg->delivery_info['delivery_tag']);
};
$info_callback = function($msg){
echo 'info: ', $msg->body, "\n";
$msg->delivery_info['channel']->basic_ack($msg->delivery_info['delivery_tag']);
};

$ch->basic_consume($error_queue,"",false,false,false,false,$error_callback);
$ch->basic_consume($warning_queue,"",false,false,false,false,$warning_callback);
$ch->basic_consume($info_queue,"",false,false,false,false,$info_callback);

while(count($ch->callbacks)){
$ch->wait();
}


?>